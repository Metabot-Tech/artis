import itertools
import logging
import strategies.helper as helpers
import database.operations as db
from database.models.trade import Trade
from database.models.coins import Coins
from dynaconf import settings
from strategies.trader import Trader
from strategies.watchdog import WatchDog
from strategies.analyser import Analyser

logger = logging.getLogger(__name__)


class Arbitrage(object):
    def __init__(self):
        self.trader = Trader()
        self.watchdog = WatchDog()
        self.analyser = Analyser()

    def run(self):
        markets = settings.MARKETS
        logger.debug("Supported markets: {}".format(markets))

        # Analyse all possible combinations
        coins_analysis = []
        for market_pair in itertools.combinations(markets, 2):
            logger.info("Comparing markets: {}".format(market_pair))

            # Verify supported coins by both markets
            supported_coins = helpers.intersect(settings[market_pair[0]].get("COINS"),
                                                settings[market_pair[1]].get("COINS"))

            logger.debug("Supported coins: {}".format(supported_coins))

            # Check all coins
            for coin in supported_coins:
                logger.info("Comparing coin: {}".format(coin))
                coins_analysis.append(self.analyser.get_coin_analysis(coin, market_pair[0], market_pair[1]))
                coins_analysis.append(self.analyser.get_coin_analysis(coin, market_pair[1], market_pair[0]))

        # Try perform arbitrage from most paying coins
        coins_analysis.sort(key=lambda x: x.profit_factor, reverse=True)

        for i in range(len(coins_analysis)):
            logger.info("Trying to perform arbitrage on coin {}, from {} to {}".format(coins_analysis[i].coin,
                                                                                       coins_analysis[i].origin,
                                                                                       coins_analysis[i].destination))
            # Verify profitability
            if coins_analysis[i].profit_factor < settings["PROFIT_FACTOR"]:
                logger.warning("Arbitrage with coin {} is not profitable enough".format(coins_analysis[i].coin))
                return False

            # Verify supply
            amount_wanted = settings.AMOUNT_TO_TRADE / coins_analysis[i].origin_price
            amount_available = self.watchdog.get_available_volume(coins_analysis[i].coin, coins_analysis[i].origin)

            if amount_wanted > amount_available:
                logger.warning("Not enough {} available from {}, skipping".format(coins_analysis[i].coin,
                                                                                  coins_analysis[i].origin))
                continue

            # TODO: Check balance in account

            # Create transaction
            transaction = db.create_transaction()
            trade = db.upsert_trade(Trade(transaction,
                                          coins_analysis[i].origin,
                                          settings.AMOUNT_TO_TRADE,
                                          Coins.ETH,
                                          amount_wanted,
                                          coins_analysis[i].coin))
            #trade.order_id = self.trader.buy_coin(coins_analysis[i].coin,
            #                                      coins_analysis[i].origin,
            #                                      amount_wanted,
            #                                      coins_analysis[i].origin_price)
            return True






