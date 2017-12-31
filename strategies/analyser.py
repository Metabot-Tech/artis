import logging
import asyncio
import ccxt.async as ccxt
from liqui import Liqui
from binance.client import Client
from dynaconf import settings

logger = logging.getLogger(__name__)


class CoinAnalysis(object):
    def __init__(self, coin=None, origin=None, origin_price=0, destination=None, destination_price=0, profit_factor=0):
        self.coin = coin
        self.origin = origin
        self.origin_price = origin_price
        self.destination = destination
        self.destination_price = destination_price
        self.profit_factor = profit_factor


class Analyser(object):
    _pair = "{}/ETH"
    _LIMIT = "limit"
    _minimum_order = 0.01 # In ETH

    def __init__(self):
        self.liqui = Liqui(settings.LIQUI.API_KEY, settings.LIQUI.API_SECRET)
        self.binance = Client(settings.BINANCE.API_KEY, settings.BINANCE.API_SECRET)
        self.markets = {
            'LIQUI': ccxt.liqui({
                'apiKey': settings.LIQUI.API_KEY,
                'secret': settings.LIQUI.API_SECRET
            }),
            'BINANCE': ccxt.binance({
                'apiKey': settings.BINANCE.API_KEY,
                'secret': settings.BINANCE.API_SECRET
            })
        }

    def get_coin_analysis(self, coin, origin, destination):
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

    async def get_latest_depth(self, market, coin, params={}):
        return await self.markets.get(market).fetch_order_book(self._pair.format(coin), params=params)

    async def get_balance(self, market, params={}):
        return await self.markets.get(market).fetch_balance(params=params)

    def is_filled(self, order, market):
        # TODO: Refactor to add markets more easily
        if market == "LIQUI":
            if order.get("info").get("return").get("order_id") is 0:
                return True
        elif market == "BINANCE":
            if order.get("info").get("status") == "FILLED":
                return True
        else:
            logger.error("Cannot extract status for market {}".format(market))
        return False

    def extract_amount(self, order, market):
        # TODO: Refactor to add markets more easily
        if market == "LIQUI":
            return order.get("info").get("return").get("received")
        elif market == "BINANCE":
            return float(order.get("info").get("executedQty"))
        else:
            logger.error("Cannot extract status for market {}".format(market))
        return 0

    def extract_remaining_amount(self, order, market):
        # TODO: Refactor to add markets more easily
        if market == "LIQUI":
            return order.get("info").get("return").get("remains")
        elif market == "BINANCE":
            price = float(order.get("info").get("origQty")) - float(order.get("info").get("executedQty"))
            logger.debug(price)
            return price
        else:
            logger.error("Cannot extract status for market {}".format(market))
        return 0

    def extract_price(self, order, market):
        # TODO: Refactor to add markets more easily
        if market == "LIQUI":
            return order.get("price")
        elif market == "BINANCE":
            return float(order.get("info").get("price"))
        else:
            logger.error("Cannot extract status for market {}".format(market))
        return 0

    def extract_good_order(self, orders):
        for order in orders:
            if order[0]*order[1] > self._minimum_order:
                return order
        logger.error("No good order found, returning first one")
        return orders[0]
