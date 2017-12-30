import logging
import time
import ccxt
from dynaconf import settings
from liqui import Liqui
from binance.client import Client

logger = logging.getLogger(__name__)


class Trader(object):
    _sleep_time = 5
    _pair = "{}/ETH"
    _LIMIT = "limit"

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

        # Init markets
        for key, value in self.markets.items():
            value.load_markets()

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

    def buy_coin(self, coin, market, amount, price):
        # Temporary origin market checking until abstracted
        if market == "LIQUI":
            pair = "{}_eth".format(coin).lower()
            order = self.liqui.buy(pair, price, amount)
            order_id = order.get("order_id")
        elif market == "BINANCE":
            symbol = "{}ETH".format(coin)
        else:
            logger.error("Unknown market: {}".format(market))
            return -1

        logger.info("Buying {} {} at {} on {}. ID: {}".format(amount, coin, price, market, order_id))
        return order_id

    def sell_coin(self, coin, market, amount, price):
        # Temporary origin market checking until abstracted
        if market == "LIQUI":
            pair = "{}_eth".format(coin).lower()
            order = self.liqui.sell(pair, price, amount)
            order_id = order.get("order_id")
        elif market == "BINANCE":
            symbol = "{}ETH".format(coin)
        else:
            logger.error("Unknown market: {}".format(market))
            return -1

        logger.info("Selling {} {} at {} on {}. ID: {}".format(amount, coin, price, market, order_id))
        return order_id

    def wait_for_order(self, order_id, market, timeout=300):
        completed = False
        while not completed:
            timeout -= self._sleep_time
            time.sleep(self._sleep_time)
            if timeout <= 0:
                logger.error("Order {} is taking too long to complete".format(order_id))
                return False

            # Temporary origin market checking until abstracted
            if market == "LIQUI":
                order_info = self.liqui.order_info(order_id)
                status = order_info.get(order_id).get("status")
                if status != 0:
                    completed = True
            elif market == "BINANCE":
                pass
            else:
                logger.error("Unknown market: {}".format(market))
                return False

        logger.info("Order {} completed".format(order_id))
        return True
