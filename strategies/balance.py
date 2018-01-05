import logging
import time
import sys
import asyncio
from strategies.trader import Trader
from strategies.helper import Helper
from database.models.trade import Trade
from database.models.balance import Balance as BalanceModel
from database.models.types import Types
from database.models.status import Status
from database.models.coins import Coins
from dynaconf import settings

logger = logging.getLogger(__name__)


class Analysis:
    def __init__(self, buy, sell, exposure):
        self.buy = buy
        self.sell = sell
        self.exposure = exposure


class Balance(object):
    _max_pending_sells = 5
    _sell_timeout = 5
    _sell_miss_percentage = 0.995

    def __init__(self, coin, market1, market2, trader, analyser, reporter, database, helper):
        self.trader = trader
        self.analyser = analyser
        self.reporter = reporter
        self.reporter.logger = logger
        self.db = database
        self.helper = helper
        self.coin = coin
        self.markets = [market1, market2]
        self.running = True
        self.balance_eth = {"LIQUI": 0, "BINANCE": 0}
        self.balance_coin = {"LIQUI": 0, "BINANCE": 0}
        self.opened_orders = 0

        # Fill database with base balance if empty
        if self.db.count_transactions() == 0:
            transaction = self.db.create_transaction()
            self._update_balance(transaction)

        self._update_pending_sells()

    def _update_pending_sells(self):
        sells = self.db.fetch_pending_sells()
        pending_sells = len(sells)
        for sell in sells:
            order = self.trader.fetch_order(sell.market.name, sell.coin.name, sell.order_id)
            if self.analyser.is_filled(order, sell.market.name):
                pending_sells -= 1
                sell.status = Status.DONE
                self.db.upsert_trade(sell)

        logger.debug("Pending sells remaining: {}".format(pending_sells))

        return pending_sells

    def _update_balance(self, transaction=None):
        """
        This fetch the balance for each market for ETH and the coin currently traded.
        It updates the object balance variables.

        :return: Nothing
        """
        loop = asyncio.get_event_loop()

        try:
            balance_tasks = [self.analyser.get_balance(i) for i in self.markets]
            balance_results = loop.run_until_complete(asyncio.gather(*balance_tasks))
            balance = dict(zip(self.markets, balance_results))
        except:
            logger.exception("An error occurred when trying to fetch the balance")
            return False

        # Store in database
        for market in self.markets:
            # Update values
            self.balance_eth[market] = balance.get(market).get("ETH").get('free')
            self.balance_coin[market] = balance.get(market).get(self.coin).get('free')

            # Update database
            if transaction is not None:
                balance_eth = BalanceModel(transaction, market, Coins.ETH, self.balance_eth.get(market))
                self.db.upsert_balance(balance_eth)
                balance_coin = BalanceModel(transaction, market, Coins[self.coin], self.balance_coin.get(market))
                self.db.upsert_balance(balance_coin)

        logger.debug("Total ETH: {}".format(sum([self.balance_eth.get(i) for i in self.markets])))
        logger.debug("Total {}: {}".format(self.coin, sum([self.balance_coin.get(i) for i in self.markets])))

        return True

    def _handle_miss_buy(self, order, market):
        self.reporter.warning("Trade miss when buying {} on {}. Cancelling order: {}".format(self.coin,
                                                                                             market,
                                                                                             order.get("id")))
        try:
            cancellation = self.trader.cancel_order(market, self.coin, order.get("id"))
            logger.debug(cancellation)
        except:
            logger.exception("")
            self.reporter.error("Cannot cancel buy: {} on {}".format(order.get("id"), market))

        fetched_order = self.trader.fetch_order(market, self.coin, order.get("id"))
        return Trader.fill_fetch_order(fetched_order, market)

    def _buy(self, analysis, volumes_wanted, asks):
        """
        This try to buy the selected coin from the selected market at the selected price.
        It will cancel the order if it is not able to fill the order instantly.

        .. todo:: Change the parameters

        :param analysis: The analysis object
        :param volumes_wanted: The volume wanted
        :param asks: Asks for all markets
        :return: Boolean for order completion and the order itself
        """
        try:
            order = self.trader.buy(analysis.buy, self.coin, volumes_wanted.get('buy'), asks.get(analysis.buy)[0])
        except:
            logger.exception("Failed to buy {} on {}".format(self.coin, analysis.buy))
            return None

        logger.debug(order)

        if not self.analyser.is_filled(order, analysis.buy):
            return self._handle_miss_buy(order, analysis.buy)

        return Trader.fill_buy_sell_order(order, analysis.buy)

    def _handle_miss_sell(self, order, analysis, asks):
        # Check each second if sold until timeout
        for i in range(self._sell_timeout):
            fetched_order = self.trader.fetch_order(analysis.sell, self.coin, order.get("id"))
            fetched_order = Trader.fill_fetch_order(fetched_order, analysis.sell)
            if fetched_order.status == Status.DONE:
                return True, fetched_order, None
            time.sleep(1)

        # If not sold, cancel order
        self.reporter.warning("Trade miss when selling {} on {}. Cancelling order: {}".format(self.coin,
                                                                                              analysis.sell,
                                                                                              order.get("id")))
        cancellation = self.trader.cancel_order(analysis.sell, self.coin, order.get("id"))
        logger.debug(cancellation)

        # Create new order at market price
        old_order = self.trader.fetch_order(analysis.sell, self.coin, order.get("id"))
        old_order = Trader.fill_fetch_order(old_order, analysis.sell)
        try:
            new_price = asks.get(analysis.sell)[0]*self._sell_miss_percentage
            logger.debug(new_price)
            new_order = self.trader.sell(analysis.sell, self.coin, old_order.remaining_amount,
                                         asks.get(analysis.sell)[0]*self._sell_miss_percentage)
        except:
            self.reporter.error("Failed to sell {} on {}, stopping".format(self.coin, analysis.sell))
            logger.exception("")
            return False, None, old_order

        logger.debug(new_order)

        return True, Trader.fill_buy_sell_order(new_order, analysis.sell), old_order

    def _sell(self, analysis, volumes_wanted, bids, asks):
        try:
            order = self.trader.sell(analysis.sell, self.coin, volumes_wanted.get('sell'),
                                     bids.get(analysis.sell)[0])
        except:
            self.reporter.error("Failed to sell {} on {}, stopping".format(self.coin, analysis.sell))
            return False, None, None

        logger.debug(order)

        if not self.analyser.is_filled(order, analysis.sell):
            return self._handle_miss_sell(order, analysis, asks)

        return True, Trader.fill_buy_sell_order(order, analysis.sell), None

    def _get_trade_volumes(self, asks, bids, analysis, rounding=0):
        # Check available volume
        volumes = {
            'ask': asks.get(analysis.buy)[1],
            'bid': bids.get(analysis.sell)[1]
        }

        prices = {
            'ask': asks.get(analysis.buy)[0],
            'bid': bids.get(analysis.sell)[0]
        }

        volumes_wanted = {
            'buy': round(settings.AMOUNT_TO_TRADE / asks.get(analysis.buy)[0], 6),
            'sell': round(settings.AMOUNT_TO_TRADE / bids.get(analysis.sell)[0], 6)
        }

        # Ask too small
        if volumes.get('ask') < volumes_wanted.get('buy'):
            volumes_wanted['buy'] = volumes.get('ask')
            volumes_wanted['sell'] = volumes.get('ask') / analysis.exposure
            logger.debug("Ask too small, reducing sell to {} and buy to {}".format(volumes_wanted['sell'],
                                                                                   volumes_wanted['buy']))

        # Bid too small
        if volumes.get('bid') < volumes_wanted.get('sell'):
            volumes_wanted['buy'] = volumes.get('bid') * analysis.exposure
            volumes_wanted['sell'] = volumes.get('bid')
            logger.debug("Bid too small, reducing sell to {} and buy to {}".format(volumes_wanted['sell'],
                                                                                   volumes_wanted['buy']))

        # Wallet coin too small
        if self.balance_coin.get(analysis.sell) < volumes_wanted.get('sell'):
            if self.balance_coin.get(analysis.sell) * prices.get('bid') < settings.MINIMUM_AMOUNT_TO_TRADE:
                self.reporter.error("Cannot sell, empty {} wallet on {}".format(self.coin, analysis.sell), 3600)
                return None
            else:
                volumes_wanted['sell'] = self.balance_coin.get(analysis.sell)
                volumes_wanted['buy'] = volumes_wanted.get('sell') * analysis.exposure
                logger.debug("No enough coin in wallet, reducing sell to {} and buy to {}".format(volumes_wanted['sell'],
                                                                                                  volumes_wanted['buy']))

        # Wallet eth too small
        if self.balance_eth.get(analysis.buy) < volumes_wanted.get('buy') * prices.get('ask'):
            if self.balance_eth.get(analysis.buy) < settings.MINIMUM_AMOUNT_TO_TRADE:
                self.reporter.error("Cannot buy, empty ETH wallet on {}".format(analysis.buy), 3600)
                return None
            else:
                volumes_wanted['buy'] = self.balance_eth.get(analysis.buy) / prices.get('ask')
                volumes_wanted['sell'] = volumes_wanted['buy'] / analysis.exposure
                logger.debug("No enough eth in wallet, reducing sell to {} and buy to {}".format(volumes_wanted['sell'],
                                                                                                 volumes_wanted['buy']))

        # Remove fees
        volumes_wanted['buy'] = volumes_wanted['buy'] * (1 - settings.get(analysis.buy).SERVICE_FEE_HIGH)
        volumes_wanted['sell'] = volumes_wanted['sell'] * (1 - settings.get(analysis.sell).SERVICE_FEE_HIGH)

        # Round
        volumes_wanted['buy'] = round(volumes_wanted['buy'], rounding)
        volumes_wanted['sell'] = round(volumes_wanted['sell'], rounding)

        return volumes_wanted

    def run(self):
        logger.debug("Starting balance strategy of {}".format(self.coin))
        self.running = True
        update_balance = True
        loop = asyncio.get_event_loop()
        transaction = None
        pending_sells = 0

        while self.running:
            # Update balance
            if update_balance:
                if self._update_balance(transaction):
                    update_balance = False
                    transaction = None

            # Get latest prices
            try:
                depth_tasks = [self.analyser.get_latest_depth(i, self.coin, {'limit': 5}) for i in self.markets]
                depth_results = loop.run_until_complete(asyncio.gather(*depth_tasks))
                depth = dict(zip(self.markets, depth_results))
            except:
                logger.error("Market timeout!")
                continue

            # Analyse best offer
            asks = dict(zip(self.markets, [self.analyser.extract_good_order(depth.get(i).get("asks")) for i in self.markets]))
            bids = dict(zip(self.markets, [self.analyser.extract_good_order(depth.get(i).get("bids")) for i in self.markets]))

            analyses = [
                Analysis(self.markets[0], self.markets[1], bids.get(self.markets[1])[0]/asks.get(self.markets[0])[0]),
                Analysis(self.markets[1], self.markets[0], bids.get(self.markets[0])[0]/asks.get(self.markets[1])[0])
            ]

            # Perform balance
            for analysis in analyses:
                # Check profit
                if analysis.exposure < settings.PROFIT_FACTOR:
                    continue

                # Check available volume
                volumes_wanted = self._get_trade_volumes(asks, bids, analysis)

                if volumes_wanted is None:
                    update_balance = True
                    time.sleep(30)
                    continue

                # Check pending sells
                if pending_sells >= self._max_pending_sells:
                    pending_sells = self._update_pending_sells()
                    if pending_sells > 0:
                        self.reporter.error("{} pending sales, please address the issue".format(pending_sells))
                    continue

                # Buy
                buy_order = self._buy(analysis, volumes_wanted, asks)
                logger.debug(buy_order)
                if buy_order is None:
                    continue

                if buy_order.executed_amount == 0:
                    continue

                if buy_order.remaining_amount > 0:
                    if buy_order.remaining_amount > settings.MINIMUM_AMOUNT_TO_TRADE*bids.get(analysis.sell)[0]:
                        volumes_wanted['sell'] = round(buy_order.executed_amount / analysis.exposure)
                    else:
                        self.reporter.error("Buy miss {} on {} not big enough to sell, remaining: {}".format(buy_order.id,
                                                                                                             buy_order.market,
                                                                                                             buy_order.remaining_amount))

                logger.info("Successfully performed buy order: {}".format(buy_order.id))

                # Sell
                sell_done, sell_order, cancelled_sell_order = self._sell(analysis, volumes_wanted, bids, asks)
                if not sell_done:
                    # TODO: Should not exit here, should at least save the state
                    logger.error("Currently not handling bad sell, stopping")
                    sys.exit(1)
                logger.info("Successfully performed sell order: {}".format(sell_order.id))

                # Store buy information in database
                transaction = self.db.create_transaction()
                buy_trade = Trade(transaction,
                                  analysis.buy,
                                  Types.BUY,
                                  self.coin,
                                  buy_order.executed_amount,
                                  buy_order.price,
                                  buy_order.id,
                                  buy_order.status)
                self.db.upsert_trade(buy_trade)

                # Store sell information in database
                if sell_order.remaining_amount > 0:
                    pending_sells += 1

                if cancelled_sell_order is not None:
                    cancelled_sell_trade = Trade(transaction,
                                                 analysis.sell,
                                                 Types.SELL,
                                                 self.coin,
                                                 cancelled_sell_order.executed_amount,
                                                 cancelled_sell_order.price,
                                                 cancelled_sell_order.id,
                                                 cancelled_sell_order.status)
                    self.db.upsert_trade(cancelled_sell_trade)

                sell_trade = Trade(transaction,
                                   analysis.sell,
                                   Types.SELL,
                                   self.coin,
                                   sell_order.start_amount,
                                   sell_order.price,
                                   sell_order.id,
                                   sell_order.status)
                self.db.upsert_trade(sell_trade)

                update_balance = True
                break

            # Sleep
            time.sleep(0.1)
