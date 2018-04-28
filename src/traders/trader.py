import logging
import ccxt
from dynaconf import settings
from ..analysers.analyser import Analyser

logger = logging.getLogger(__name__)


class Order:
    def __init__(self, market, id, type, start_amount, remaining_amount, price, status):
        self.market = market
        self.type = type
        self.id = id
        self.start_amount = start_amount
        self.executed_amount = round(start_amount - remaining_amount, 8)
        self.remaining_amount = remaining_amount
        self.price = price
        self.status = status


class Trader(object):
    _sleep_time = 5
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

        # Init markets
        for key, value in self.markets.items():
            value.load_markets()

    @staticmethod
    def new_exposure(exposure):
        current_profit = exposure - 1
        minimum_profit = settings.PROFIT_FACTOR - 1

        new_profit = current_profit * (1 - settings.PROFIT_REDUCTION / minimum_profit)
        new_exposure = round(1 + new_profit, 6)

        logger.info("New exposure: {}".format(new_exposure))

        return new_exposure

    @staticmethod
    def profit_reduction(exposure):
        current_profit = exposure - 1
        minimum_profit = settings.PROFIT_FACTOR - 1

        reduction = round(current_profit * settings.PROFIT_REDUCTION / minimum_profit, 10)

        logger.info("Profit reduction: {}".format(reduction))

        return reduction

    @staticmethod
    def fill_buy_sell_order(order, market):
        return Order(market,
                     order.get('id'),
                     Analyser.extract_type(order, market),
                     Analyser.extract_start_amount(order, market),
                     Analyser.extract_remaining_amount2(order, market),
                     Analyser.extract_price2(order, market),
                     Analyser.extract_status(order, market))

    @staticmethod
    def fill_fetch_order(order, market):
        return Order(market,
                     order.get('id'),
                     Analyser.extract_type(order, market),
                     Analyser.extract_start_amount(order, market),
                     Analyser.extract_remaining_amount_order(order, market),
                     Analyser.extract_price2(order, market),
                     Analyser.extract_status_order(order, market))

    def buy(self, market, coin, volume, rate):
        symbol = self._pair.format(coin)
        volume = self.markets.get(market).amount_to_lots(symbol, volume)
        return self.markets.get(market).create_order(symbol, self._LIMIT, 'buy', volume, rate)

    def sell(self, market, coin, volume, rate):
        symbol = self._pair.format(coin)
        volume = self.markets.get(market).amount_to_lots(symbol, volume)
        return self.markets.get(market).create_order(symbol, self._LIMIT, 'sell', volume, rate)

    def cancel_order(self, market, coin, order_id):
        symbol = self._pair.format(coin)
        return self.markets.get(market).cancel_order(order_id, symbol)

    def fetch_order(self, market, coin, order_id):
        symbol = self._pair.format(coin)
        return self.markets.get(market).fetch_order(order_id, symbol)
