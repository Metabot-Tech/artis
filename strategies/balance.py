import logging
import time
import asyncio
from dynaconf import settings
from strategies.trader import Trader
from strategies.analyser import Analyser
from strategies.reporter import Reporter

logger = logging.getLogger(__name__)


class Analysis:
    def __init__(self, buy, sell, exposure):
        self.buy = buy
        self.sell = sell
        self.exposure = exposure


class Balance(object):
    def __init__(self, coin, market1, market2):
        self.trader = Trader()
        self.analyser = Analyser()
        self.reporter = Reporter()
        self.coin = coin
        self.markets = [market1, market2]
        self.running = True
        self.balance_eth = 0
        self.balance_coin = 0

    def _update_balance(self):
        loop = asyncio.get_event_loop()

        try:
            balance_tasks = [self.analyser.get_balance(i) for i in self.markets]
            balance_results = loop.run_until_complete(asyncio.gather(*balance_tasks))
            balance = dict(zip(self.markets, balance_results))
        except:
            logger.error("An error occurred when trying to fetch the balance")
            return

        self.balance_eth = dict(zip(self.markets, [balance.get(i).get("ETH").get('free') for i in self.markets]))
        self.balance_coin = dict(zip(self.markets, [balance.get(i).get(self.coin).get('free') for i in self.markets]))

        logger.debug("Balance ETH: {}".format(self.balance_eth))
        logger.debug("Balance coin: {}".format(self.balance_coin))

    def run(self):
        logger.debug("Starting balance strategy of {}".format(self.coin))
        self.running = True
        update_balance = True
        loop = asyncio.get_event_loop()

        while self.running:
            logger.info("Balance started for coin {}".format(self.coin))

            # Update balance
            if update_balance:
                self._update_balance()
                update_balance = False

            # Get latest prices
            try:
                depth_tasks = [self.analyser.get_latest_depth(i, self.coin, {'limit': 5}) for i in self.markets]
                depth_results = loop.run_until_complete(asyncio.gather(*depth_tasks))
                depth = dict(zip(self.markets, depth_results))
            except:
                logger.error("Market timeout!")
                break

            # Analyse best offer
            asks = dict(zip(self.markets, [depth.get(i).get("asks")[0] for i in self.markets]))
            bids = dict(zip(self.markets, [depth.get(i).get("bids")[0] for i in self.markets]))

            analyses = [
                Analysis(self.markets[0], self.markets[1], bids.get(self.markets[1])[0]/asks.get(self.markets[0])[0]),
                Analysis(self.markets[1], self.markets[0], bids.get(self.markets[0])[0]/asks.get(self.markets[1])[0])
            ]

            # Perform balance
            for analysis in analyses:
                logger.debug("Exposure: {}".format(analysis.exposure))

                # Check profit
                if analysis.exposure < settings.PROFIT_FACTOR:
                    continue

                # Check available volume
                volumes = {
                    'ask': asks.get(analysis.buy)[1],
                    'bid': bids.get(analysis.sell)[1]
                }

                volumes_wanted = {
                    'buy': round(settings.AMOUNT_TO_TRADE/asks.get(analysis.buy)[0], 6),
                    'sell': round(settings.AMOUNT_TO_TRADE/bids.get(analysis.sell)[0], 6)
                }

                if volumes.get('ask') < volumes_wanted.get('buy'):
                    logger.warning("Ask is not big enough, skipping")
                    continue

                if volumes.get('bid') < volumes_wanted.get('sell'):
                    logger.warning("Bid if not big enough, skipping")
                    continue

                if self.balance_coin.get(analysis.sell) < volumes_wanted.get('sell'):
                    logger.error("Cannot sell, empty {} wallet on {}".format(self.coin, analysis.sell))
                    self.reporter.error("Cannot sell, empty {} wallet on {}".format(self.coin, analysis.sell))
                    continue

                if self.balance_eth.get(analysis.buy) < settings.AMOUNT_TO_TRADE:
                    logger.error("Cannot buy, empty ETH wallet on {}".format(self.coin, analysis.buy))
                    self.reporter.error("Cannot buy, empty ETH wallet on {}".format(self.coin, analysis.buy))
                    continue

                # Buy and sell
                # input("Press Enter to buy/sell...")
                buy_order = self.trader.buy(analysis.buy, self.coin, volumes_wanted.get('buy'), asks.get(analysis.buy)[0])
                sell_order = self.trader.sell(analysis.sell, self.coin, volumes_wanted.get('sell'), bids.get(analysis.sell)[0])

                logger.debug(buy_order)
                logger.debug(sell_order)
                update_balance = True
                break

            logger.info("Balance done for coin {}".format(self.coin))

            # Sleep
            time.sleep(1)
