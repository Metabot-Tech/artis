import unittest
import unittest.mock as mock
from strategies.balance import Balance
from strategies.balance import Analysis
from strategies.trader import Trader
from strategies.analyser import Analyser
from strategies.reporter import Reporter
from strategies.helper import Helper
from database.database import Database
from database.models.trade import Trade
from database.models.types import Types
from database.models.coins import Coins
from database.models.markets import Markets
from database.models.status import Status
from tests.orders import *
from dynaconf import settings

ETH = "ETH"
COIN = "TRX"
LIQUI = "LIQUI"
BINANCE = "BINANCE"
AMOUNT_COIN = 1000
SMALL_AMOUNT_COIN = 100
AMOUNT_ETH = 0.5
SMALL_AMOUNT_ETH = 0.01
PRICE_ASK = 0.000052
PRICE_BID = 0.000055
ORDER_ID = '183892657'
ANOTHER_ORDER_ID = 2222
ORDER_AMOUNT = 5000
EXPOSURE = 1.057692308
VOLUME_BUY = 600
SMALL_VOLUME_BUY = 100
VOLUME_SELL = 500
SMALL_VOLUME_SELL = 110



class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class TestBalance(unittest.TestCase):
    def setUp(self):
        self.mock_trader = mock.create_autospec(Trader)
        self.mock_analyser = mock.create_autospec(Analyser)
        self.mock_reporter = mock.create_autospec(Reporter)
        self.mock_database = mock.create_autospec(Database)
        self.mock_helper = mock.create_autospec(Helper)

        self.strategy = Balance(COIN, LIQUI, BINANCE,
                                self.mock_trader,
                                self.mock_analyser,
                                self.mock_reporter,
                                self.mock_database,
                                self.mock_helper)

    # TESTS UPDATE
    def test_update_pending_sells(self):
        trade = Trade(None, Markets[LIQUI], Types.SELL, Coins[COIN], AMOUNT_COIN, PRICE_ASK, ORDER_ID, Status.ONGOING)
        self.mock_database.fetch_pending_sells.return_value = [trade]
        self.mock_trader.fetch_order.return_value = {}
        self.mock_analyser.is_filled.return_value = True

        pending_sells = self.strategy._update_pending_sells()

        self.mock_database.upsert_trade.assert_called_once()
        assert trade.status == Status.DONE
        assert pending_sells == 0

    def test_update_balance_without_transaction(self):
        self.mock_analyser.get_balance = AsyncMock(return_value={ETH: {"free": AMOUNT_ETH}, COIN: {"free": AMOUNT_COIN}})

        self.strategy._update_balance()

        self.mock_database.upsert_balance.assert_not_called()
        assert self.strategy.balance_eth.get(LIQUI) == AMOUNT_ETH
        assert self.strategy.balance_eth.get(BINANCE) == AMOUNT_ETH
        assert self.strategy.balance_coin.get(LIQUI) == AMOUNT_COIN
        assert self.strategy.balance_coin.get(BINANCE) == AMOUNT_COIN

    # TESTS BUY
    def test_buy_filled(self):
        self.mock_trader.buy.return_value = LIQUI_BUY_ORDER
        self.mock_analyser.is_filled.return_value = True

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {LIQUI: [PRICE_ASK]}
        order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(LIQUI, COIN, ORDER_AMOUNT, PRICE_ASK)
        self.mock_trader.cancel_order.assert_not_called()
        assert order.id == ORDER_ID

    def test_buy_exception(self):
        self.mock_trader.buy.side_effect = Exception('timeout')

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {LIQUI: [PRICE_ASK]}
        order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(LIQUI, COIN, ORDER_AMOUNT, PRICE_ASK)
        assert order is None

    def test_miss_buy(self):
        self.mock_trader.buy.return_value = LIQUI_BUY_ORDER
        self.mock_analyser.is_filled.return_value = False
        self.strategy._handle_miss_buy = mock.Mock(return_value=Trader.fill_fetch_order(LIQUI_FETCH_BUY_ORDER, LIQUI))

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {LIQUI: [PRICE_ASK]}
        order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(LIQUI, COIN, ORDER_AMOUNT, PRICE_ASK)
        self.strategy._handle_miss_buy.assert_called_once_with(LIQUI_BUY_ORDER, analysis.buy)
        assert order.id == ORDER_ID

    # TESTS HANDLE MISS BUY
    def test_handle_miss_buy(self):
        self.mock_trader.cancel_order.return_value = {}
        self.mock_trader.fetch_order.return_value = LIQUI_FETCH_BUY_ORDER

        order = self.strategy._handle_miss_buy(LIQUI_BUY_ORDER, LIQUI)

        self.mock_trader.cancel_order.assert_called_once_with(LIQUI, COIN, ORDER_ID)
        self.mock_trader.fetch_order.assert_called_once_with(LIQUI, COIN, ORDER_ID)
        assert order.id == ORDER_ID

    def test_handle_miss_buy_cancellation_exception(self):
        self.mock_trader.cancel_order.side_effect = Exception('Order does not exist')
        self.mock_trader.fetch_order.return_value = LIQUI_FETCH_BUY_ORDER

        order = self.strategy._handle_miss_buy(LIQUI_BUY_ORDER, LIQUI)

        self.mock_trader.cancel_order.assert_called_once_with(LIQUI, COIN, ORDER_ID)
        self.mock_trader.fetch_order.assert_called_once_with(LIQUI, COIN, ORDER_ID)
        assert order.id == ORDER_ID

    # TESTS SELL
    def test_sell_filled(self):
        self.mock_trader.sell.return_value = {'id': ORDER_ID}
        self.mock_analyser.is_filled.return_value = True

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        volumes_wanted = {'sell': ORDER_AMOUNT}
        bids = {BINANCE: [PRICE_BID]}
        asks = {LIQUI: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._sell(analysis, volumes_wanted, bids, asks)

        self.mock_trader.sell.assert_called_once_with(BINANCE, COIN, ORDER_AMOUNT, PRICE_BID)
        self.mock_trader.cancel_order.assert_not_called()
        assert done is True
        assert order.get('id') == ORDER_ID
        assert cancelled_order is None

    def test_miss_sell(self):
        initial_order = {'id': ORDER_ID}
        self.mock_trader.sell.return_value = initial_order
        self.mock_analyser.is_filled.return_value = False
        self.strategy._handle_miss_sell = mock.Mock(return_value=(True, initial_order, None))

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        volumes_wanted = {'sell': ORDER_AMOUNT}
        bids = {BINANCE: [PRICE_BID]}
        asks = {LIQUI: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._sell(analysis, volumes_wanted, bids, asks)

        self.mock_trader.sell.assert_called_once_with(BINANCE, COIN, ORDER_AMOUNT, PRICE_BID)
        self.strategy._handle_miss_sell.assert_called_once_with(order, analysis, asks)
        assert done is True
        assert order.get('id') == ORDER_ID
        assert cancelled_order is None

    def test_sell_exception(self):
        self.mock_trader.sell.side_effect = Exception("Market timeout")

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        volumes_wanted = {'sell': ORDER_AMOUNT}
        bids = {BINANCE: [PRICE_BID]}
        asks = {LIQUI: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._sell(analysis, volumes_wanted, bids, asks)

        self.mock_trader.sell.assert_called_once_with(BINANCE, COIN, ORDER_AMOUNT, PRICE_BID)
        self.mock_trader.cancel_order.assert_not_called()
        assert done is False
        assert order is None
        assert cancelled_order is None

    # TESTS HANDLE MISS SELL
    def test_handle_miss_sell(self):
        initial_order = {'id': ORDER_ID}
        fetched_order = "This is a fetched order"
        self.mock_trader.fetch_order.return_value = fetched_order
        self.mock_analyser.is_order_filled.return_value = True

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        asks = {LIQUI: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._handle_miss_sell(initial_order, analysis, asks)

        self.mock_trader.fetch_order.assert_called_once_with(BINANCE, COIN, ORDER_ID)
        self.mock_trader.cancel_order.assert_not_called()
        assert done is True
        assert order.get('id') == ORDER_ID
        assert cancelled_order is None

    def test_handle_miss_sell_fetch_throw(self):
        pass

    @mock.patch('time.sleep', return_value=None)
    def test_handle_miss_sell_cancellation(self, mock_sleep):
        initial_order = {'id': ORDER_ID}
        fetched_order = "This is a fetched order"
        self.mock_trader.fetch_order.return_value = fetched_order
        self.mock_trader.sell.return_value = {'id': ANOTHER_ORDER_ID}
        self.mock_analyser.is_order_filled.return_value = False

        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)
        asks = {BINANCE: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._handle_miss_sell(initial_order, analysis, asks)

        self.mock_trader.fetch_order.assert_called_with(BINANCE, COIN, ORDER_ID)
        self.mock_trader.cancel_order.assert_called_once_with(BINANCE, COIN, ORDER_ID)
        assert done is True
        assert order.get('id') == ANOTHER_ORDER_ID
        assert cancelled_order.get('id') == ORDER_ID

    def test_handle_miss_sell_cancellation_exception(self):
        pass

    def test_handle_miss_sell_resell_exception(self):
        pass

    # TESTS GET TRADE VOLUMES
    def test_get_trade_volumes_no_reduction(self):
        settings.AMOUNT_TO_TRADE = 0.02
        self.strategy.balance_eth = {"LIQUI": 1, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": 10000}

        asks = {LIQUI: [PRICE_ASK, VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted.get('buy') == round(settings.AMOUNT_TO_TRADE / PRICE_ASK)
        assert volumes_wanted.get('sell') == round(settings.AMOUNT_TO_TRADE / PRICE_BID)

    def test_get_trade_volumes_ask_too_small(self):
        settings.AMOUNT_TO_TRADE = 0.02
        self.strategy.balance_eth = {"LIQUI": 1, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": 10000}

        asks = {LIQUI: [PRICE_ASK, SMALL_VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted.get('buy') == SMALL_VOLUME_BUY
        assert volumes_wanted.get('sell') == round(SMALL_VOLUME_BUY / EXPOSURE)

    def test_get_trade_volumes_bid_too_small(self):
        settings.AMOUNT_TO_TRADE = 0.02
        self.strategy.balance_eth = {"LIQUI": 1, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": 10000}

        asks = {LIQUI: [PRICE_ASK, VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, SMALL_VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted.get('buy') == round(SMALL_VOLUME_SELL * EXPOSURE)
        assert volumes_wanted.get('sell') == SMALL_VOLUME_SELL

    def test_get_trade_volumes_wallet_eth_too_small(self):
        settings.AMOUNT_TO_TRADE = 0.02
        settings.MINIMUM_AMOUNT_TO_TRADE = 0.001

        self.strategy.balance_eth = {"LIQUI": SMALL_AMOUNT_ETH, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": 10000}

        asks = {LIQUI: [PRICE_ASK, VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted.get('buy') == round(SMALL_AMOUNT_ETH / PRICE_ASK)
        assert volumes_wanted.get('sell') == round(SMALL_AMOUNT_ETH / PRICE_ASK / EXPOSURE)

    def test_get_trade_volumes_wallet_coin_too_small(self):
        settings.AMOUNT_TO_TRADE = 0.02
        settings.MINIMUM_AMOUNT_TO_TRADE = 0.001

        self.strategy.balance_eth = {"LIQUI": 1, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": SMALL_AMOUNT_COIN}

        asks = {LIQUI: [PRICE_ASK, VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted.get('buy') == round(SMALL_AMOUNT_COIN * EXPOSURE)
        assert volumes_wanted.get('sell') == round(SMALL_AMOUNT_COIN)

    def test_get_trade_volumes_wallet_eth_below_minimum(self):
        settings.AMOUNT_TO_TRADE = 0.02
        settings.MINIMUM_AMOUNT_TO_TRADE = 0.001

        self.strategy.balance_eth = {"LIQUI": 0.0005, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": 10000}

        asks = {LIQUI: [PRICE_ASK, VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted is None

    def test_get_trade_volumes_wallet_coin_below_minimum(self):
        settings.AMOUNT_TO_TRADE = 0.02
        settings.MINIMUM_AMOUNT_TO_TRADE = 0.01

        self.strategy.balance_eth = {"LIQUI": 1, "BINANCE": 1}
        self.strategy.balance_coin = {"LIQUI": 10000, "BINANCE": 30}

        asks = {LIQUI: [PRICE_ASK, VOLUME_BUY]}
        bids = {BINANCE: [PRICE_BID, VOLUME_SELL]}
        analysis = Analysis(LIQUI, BINANCE, EXPOSURE)

        volumes_wanted = self.strategy._get_trade_volumes(asks, bids, analysis)

        assert volumes_wanted is None





