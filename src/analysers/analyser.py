import logging
import ccxt.async as ccxt
from ..database.models.types import Types
from ..database.models.status import Status
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

    def __init__(self):
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
        self.minimum_order = settings.MINIMUM_AMOUNT_TO_TRADE

    async def get_latest_depth(self, market, coin, params={}):
        return await self.markets.get(market).fetch_order_book(self._pair.format(coin), params=params)

    async def get_balance(self, market, params={}):
        return await self.markets.get(market).fetch_balance(params=params)

    def is_order_filled(self, order, order_id, market):
        """
        Use this method when parsing the result of an order fetch

        :param order:
        :param order_id:
        :param market:
        :return:
        """
        # TODO: Refactor to add markets more easily
        if market == "LIQUI":
            if order.get("info").get("return").get(str(order_id)).get("status") == 1:
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
            logger.error("Cannot remaining amount for market {}".format(market))
        return 0

    def extract_order_executed_amount(self, order, order_id, market):
        # TODO: Refactor to add markets more easily
        if market == "LIQUI":
            return order.get("info").get("return").get(str(order_id)).get("amount")
        elif market == "BINANCE":
            return float(order.get("info").get("executedQty"))
        else:
            logger.error("Cannot executed amount for market {}".format(market))
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

    @staticmethod
    def extract_type(order, market):
        if market == "LIQUI":
            return Types[order.get("side").upper()]
        elif market == "BINANCE":
            return Types[order.get("info").get("side")]
        else:
            logger.error("Cannot extract type for market {}".format(market))
        return Types.UNKNOWN

    @staticmethod
    def extract_start_amount(order, market):
        if market == "LIQUI":
            return order.get("amount")
        elif market == "BINANCE":
            return float(order.get("info").get("origQty"))
        else:
            logger.error("Cannot extract start amount for market {}".format(market))
        return 0

    @staticmethod
    def extract_remaining_amount2(order, market):
        if market == "LIQUI":
            return order.get("info").get("return").get("remains")
        elif market == "BINANCE":
            return float(order.get("info").get("origQty")) - float(order.get("info").get("executedQty"))
        else:
            logger.error("Cannot extract remaining amount for market {}".format(market))
        return 0

    @staticmethod
    def extract_remaining_amount_order(order, market):
        if market == "LIQUI":
            return order.get("info").get("amount")
        elif market == "BINANCE":
            return float(order.get("info").get("origQty")) - float(order.get("info").get("executedQty"))
        else:
            logger.error("Cannot extract remaining amount for market {} (order)".format(market))
        return 0

    @staticmethod
    def extract_price2(order, market):
        if market == "LIQUI":
            return order.get("price")
        elif market == "BINANCE":
            return float(order.get("info").get("price"))
        else:
            logger.error("Cannot extract price for market {}".format(market))
        return 0

    @staticmethod
    def extract_status(order, market):
        if market == "LIQUI":
            if order.get("info").get("return").get("order_id") == 0:
                return Status.DONE
            else:
                return Status.ONGOING
        elif market == "BINANCE":
            if order.get("info").get("status") == "FILLED":
                return Status.DONE
            else:
                return Status.ONGOING
        else:
            logger.error("Cannot extract status for market {}".format(market))
        return Status.UNKNOWN

    @staticmethod
    def extract_status_order(order, market):
        if market == "LIQUI":
            return {0: Status.ONGOING,
                    1: Status.DONE,
                    2: Status.CANCELLED,
                    3: Status.CANCELLED}[order.get("info").get("status")]
        elif market == "BINANCE":
            return {'NEW': Status.ONGOING,
                    'PARTIALLY_FILLED': Status.ONGOING,
                    'FILLED': Status.DONE,
                    'CANCELED': Status.CANCELLED}[order.get("info").get("status")]
        else:
            logger.error("Cannot extract status for market {} (order)".format(market))
        return Status.UNKNOWN

    @staticmethod
    def is_filled(order, market):
        if Analyser.extract_status(order, market) == Status.DONE:
            return True
        else:
            return False

    def extract_good_order(self, orders):
        for order in orders:
            if order[0]*order[1] > self.minimum_order:
                return order
        logger.error("No good order found")
        return [orders[0][0], 0]
