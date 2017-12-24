import itertools
import logging
import strategies.helpers as helpers
import database.operations as db
from database.models.trade import Trade
from database.models.coins import Coins
from dynaconf import settings
from liqui import Liqui
from binance.client import Client
from strategies.trader import Trader
from strategies.watchdog import WatchDog

logger = logging.getLogger(__name__)


class CoinAnalysis(object):
    def __init__(self, coin=None, origin=None, origin_price=0, destination=None, destination_price=0, profit_factor=0):
        self.coin = coin
        self.origin = origin
        self.origin_price = origin_price
        self.destination = destination
        self.destination_price = destination_price
        self.profit_factor = profit_factor


class Arbitrage(object):
    def __init__(self):
        self.liqui = Liqui(settings.LIQUI.API_KEY, settings.LIQUI.API_SECRET)
        self.binance = Client(settings.BINANCE.API_KEY, settings.BINANCE.API_SECRET)
        self.trader = Trader()
        self.watchdog = WatchDog()

    def _get_coin_analysis(self, coin, origin, destination):
        coin_analysis = CoinAnalysis(coin=coin, origin=origin, destination=destination)

        # Temporary origin market checking until abstracted
        if origin == "LIQUI":
            pair = "{}_eth".format(coin).lower()
            origin_ticker = self.liqui.ticker(pair)
            origin_last_price = origin_ticker.get(pair).get('last')
        elif origin == "BINANCE":
            symbol = "{}ETH".format(coin)
            origin_ticker = self.binance.get_ticker(symbol=symbol)
            origin_last_price = float(origin_ticker.get('lastPrice'))
        else:
            logger.error("Unknown origin market: {}".format(origin))
            return coin_analysis

        coin_analysis.origin_price = origin_last_price
        logger.debug("Last price for origin market {} is {:.7f}".format(origin, origin_last_price))

        # Temporary destination market checking until abstracted
        if destination == "LIQUI":
            pair = "{}_eth".format(coin).lower()
            destination_ticker = self.liqui.ticker(pair)
            destination_last_price = destination_ticker.get(pair).get('last')
        elif destination == "BINANCE":
            symbol = "{}ETH".format(coin)
            destination_ticker = self.binance.get_ticker(symbol=symbol)
            destination_last_price = float(destination_ticker.get('lastPrice'))
        else:
            logger.error("Unknown destination market: {}".format(origin))
            return coin_analysis

        coin_analysis.destination_price = destination_last_price
        logger.debug("Last price for destination market {} is {:.7f}".format(destination, destination_last_price))

        coin_analysis.profit_factor = round(destination_last_price / origin_last_price, 6)

        logger.debug("Profit Factor: {}".format(coin_analysis.profit_factor))

        return coin_analysis

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
                coins_analysis.append(self._get_coin_analysis(coin, market_pair[0], market_pair[1]))
                coins_analysis.append(self._get_coin_analysis(coin, market_pair[1], market_pair[0]))

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
                continue

            # Create transaction
            transaction = db.create_transaction()
            trade = db.upsert_trade(Trade(transaction.id,
                                          coins_analysis[i].origin,
                                          settings.AMOUNT_TO_TRADE,
                                          Coins.ETH))
            trade.order_id = self.trader.buy_coin(coins_analysis[i].coin,
                                                  coins_analysis[i].origin,
                                                  amount_wanted,
                                                  coins_analysis[i].origin_price)






