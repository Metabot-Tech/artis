import itertools
import logging
import strategies.helpers as helpers
from dynaconf import settings
from liqui import Liqui

logger = logging.getLogger(__name__)


class ProfitFactor(object):
    def __init__(self, coin=None, origin=None, destination=None, factor=None):
        self.coin = coin
        self.origin = origin
        self.destination = destination
        self.factor = factor


class Arbitrage(object):
    _pair = "{}_eth"

    def __init__(self):
        self.liqui = Liqui(settings.LIQUI.API_KEY, settings.LIQUI.API_SECRET)

    def get_profit_factor(self, coin, origin, destination):
        profit_factor = ProfitFactor(coin=coin, origin=origin, destination=destination)
        pair = self._pair.format(coin).lower()

        # Temporary origin market checking until abstracted
        if origin == "LIQUI":
            origin_ticker = self.liqui.ticker(pair)
            origin_last_price = origin_ticker.get(pair).get('last')
            logger.debug("Last price for origin market {} is {:.7f}".format(origin, origin_last_price))
        elif origin == "BINANCE":
            pass
        else:
            logger.error("Unknown origin market: {}".format(origin))
            return profit_factor

        # Temporary destination market checking until abstracted
        if destination == "LIQUI":
            destination_ticker = self.liqui.ticker(pair)
            destination_last_price = destination_ticker.get(pair).get('last')
            logger.debug("Last price for destination market {} is {:.7f}".format(origin, destination_last_price))
        elif origin == "BINANCE":
            pass
        else:
            logger.error("Unknown destination market: {}".format(origin))
            return profit_factor



        return profit_factor

    def run(self):
        markets = settings.MARKETS
        logger.debug("Supported markets: {}".format(markets))

        for market_pair in itertools.combinations(markets, 2):
            logger.info("Comparing markets: {}".format(market_pair))

            # Verify supported coins by both markets
            supported_coins = helpers.intersect(settings[market_pair[0]].get("COINS"),
                                                settings[market_pair[1]].get("COINS"))

            logger.debug("Supported coins: {}".format(supported_coins))

            # Check all coins
            profit_factor = []
            for coin in supported_coins:
                logger.info("Comparing coin: {}".format(coin))
                profit_factor.append(self.get_profit_factor(coin, market_pair[0], market_pair[1]))
                profit_factor.append(self.get_profit_factor(coin, market_pair[1], market_pair[0]))

