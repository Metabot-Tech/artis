import unittest
import unittest.mock as mock
from strategies.balance import Balance
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
PRICE = 0.00005
ORDER_ID = 1111


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

    def test_update_pending_sells(self):
        trade = Trade(None, Markets[MARKET1], Types.SELL, Coins[COIN], AMOUNT_COIN, PRICE, ORDER_ID, Status.ONGOING)
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
