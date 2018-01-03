import unittest
import unittest.mock as mock
from strategies.balance import Balance
from strategies.balance import Analysis
from strategies.trader import Trader
from strategies.analyser import Analyser
from strategies.reporter import Reporter
from database.database import Database
from database.models.trade import Trade
from database.models.types import Types
from database.models.coins import Coins
from database.models.markets import Markets
from database.models.status import Status

ETH = "ETH"
COIN = "TRX"
MARKET1 = "LIQUI"
MARKET2 = "BINANCE"
AMOUNT_COIN = 1000
AMOUNT_ETH = 0.5
PRICE_ASK = 0.00005
PRICE_BID = 0.00006
ORDER_ID = 1111
ANOTHER_ORDER_ID = 2222
ORDER_AMOUNT = 5000
EXPOSURE = 1.05


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class TestBalance(unittest.TestCase):
    def setUp(self):
        self.mock_trader = mock.create_autospec(Trader)
        self.mock_analyser = mock.create_autospec(Analyser)
        self.mock_reporter = mock.create_autospec(Reporter)
        self.mock_database = mock.create_autospec(Database)

        self.strategy = Balance(COIN, MARKET1, MARKET2,
                                self.mock_trader,
                                self.mock_analyser,
                                self.mock_reporter,
                                self.mock_database)

    # TESTS UPDATE
    def test_update_pending_sells(self):
        trade = Trade(None, Markets[MARKET1], Types.SELL, Coins[COIN], AMOUNT_COIN, PRICE_ASK, ORDER_ID, Status.ONGOING)
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
        assert self.strategy.balance_eth.get(MARKET1) == AMOUNT_ETH
        assert self.strategy.balance_eth.get(MARKET2) == AMOUNT_ETH
        assert self.strategy.balance_coin.get(MARKET1) == AMOUNT_COIN
        assert self.strategy.balance_coin.get(MARKET2) == AMOUNT_COIN

    # TESTS BUY
    def test_buy_filled(self):
        self.mock_trader.buy.return_value = {'id': ORDER_ID}
        self.mock_analyser.is_filled.return_value = True

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {MARKET1: [PRICE_ASK]}
        done, order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(MARKET1, COIN, ORDER_AMOUNT, PRICE_ASK)
        self.mock_trader.cancel_order.assert_not_called()
        assert done is True
        assert order.get('id') == ORDER_ID

    def test_buy_exception(self):
        self.mock_trader.buy.side_effect = Exception('timeout')

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {MARKET1: [PRICE_ASK]}
        done, order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(MARKET1, COIN, ORDER_AMOUNT, PRICE_ASK)
        assert done is False
        assert order is None

    def test_buy_cancellation(self):
        self.mock_trader.buy.return_value = {'id': ORDER_ID}
        self.mock_trader.cancel_order.return_value = {}
        self.mock_analyser.is_filled.return_value = False

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {MARKET1: [PRICE_ASK]}
        done, order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(MARKET1, COIN, ORDER_AMOUNT, PRICE_ASK)
        self.mock_trader.cancel_order.assert_called_once_with(MARKET1, COIN, ORDER_ID)
        assert done is False
        assert order.get('id') == ORDER_ID

    def test_buy_cancellation_exception(self):
        self.mock_trader.buy.return_value = {'id': ORDER_ID}
        self.mock_trader.cancel_order.side_effect = Exception('Order does not exist')
        self.mock_analyser.is_filled.return_value = False

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'buy': ORDER_AMOUNT}
        asks = {MARKET1: [PRICE_ASK]}
        done, order = self.strategy._buy(analysis, volumes_wanted, asks)

        self.mock_trader.buy.assert_called_once_with(MARKET1, COIN, ORDER_AMOUNT, PRICE_ASK)
        self.mock_trader.cancel_order.assert_called_once_with(MARKET1, COIN, ORDER_ID)
        assert done is False
        assert order.get('id') == ORDER_ID

    # TESTS SELL
    def test_sell_filled(self):
        self.mock_trader.sell.return_value = {'id': ORDER_ID}
        self.mock_analyser.is_filled.return_value = True

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'sell': ORDER_AMOUNT}
        bids = {MARKET2: [PRICE_BID]}
        asks = {MARKET1: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._sell(analysis, volumes_wanted, bids, asks)

        self.mock_trader.sell.assert_called_once_with(MARKET2, COIN, ORDER_AMOUNT, PRICE_BID)
        self.mock_trader.cancel_order.assert_not_called()
        assert done is True
        assert order.get('id') == ORDER_ID
        assert cancelled_order is None

    def test_miss_sell(self):
        initial_order = {'id': ORDER_ID}
        self.mock_trader.sell.return_value = initial_order
        self.mock_analyser.is_filled.return_value = False
        self.strategy._handle_miss_sell = mock.Mock(return_value=(True, initial_order, None))

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'sell': ORDER_AMOUNT}
        bids = {MARKET2: [PRICE_BID]}
        asks = {MARKET1: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._sell(analysis, volumes_wanted, bids, asks)

        self.mock_trader.sell.assert_called_once_with(MARKET2, COIN, ORDER_AMOUNT, PRICE_BID)
        self.strategy._handle_miss_sell.assert_called_once_with(order, analysis, asks)
        assert done is True
        assert order.get('id') == ORDER_ID
        assert cancelled_order is None

    def test_sell_exception(self):
        self.mock_trader.sell.side_effect = Exception("Market timeout")

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        volumes_wanted = {'sell': ORDER_AMOUNT}
        bids = {MARKET2: [PRICE_BID]}
        asks = {MARKET1: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._sell(analysis, volumes_wanted, bids, asks)

        self.mock_trader.sell.assert_called_once_with(MARKET2, COIN, ORDER_AMOUNT, PRICE_BID)
        self.mock_trader.cancel_order.assert_not_called()
        assert done is False
        assert order is None
        assert cancelled_order is None

    # TESTS handle miss sell
    def test_handle_miss_sell(self):
        initial_order = {'id': ORDER_ID}
        fetched_order = "This is a fetched order"
        self.mock_trader.fetch_order.return_value = fetched_order
        self.mock_analyser.is_order_filled.return_value = True

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        asks = {MARKET1: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._handle_miss_sell(initial_order, analysis, asks)

        self.mock_trader.fetch_order.assert_called_once_with(MARKET2, COIN, ORDER_ID)
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

        analysis = Analysis(MARKET1, MARKET2, EXPOSURE)
        asks = {MARKET2: [PRICE_ASK]}
        done, order, cancelled_order = self.strategy._handle_miss_sell(initial_order, analysis, asks)

        self.mock_trader.fetch_order.assert_called_with(MARKET2, COIN, ORDER_ID)
        self.mock_trader.cancel_order.assert_called_once_with(MARKET2, COIN, ORDER_ID)
        assert done is True
        assert order.get('id') == ANOTHER_ORDER_ID
        assert cancelled_order.get('id') == ORDER_ID

    def test_handle_miss_sell_cancellation_exception(self):
        pass

    def test_handle_miss_sell_resell_exception(self):
        pass



