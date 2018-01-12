import unittest
import os
from tests.orders import *
from strategies.analyser import Analyser
from database.models.types import Types
from database.models.status import Status
from dynaconf import settings

LIQUI = "LIQUI"
BINANCE = "BINANCE"
TOTO = "TOTO"
PRICE = 0.000085
VOLUME = 10000


class TestAnalyser(unittest.TestCase):
    def setUp(self):
        settings.configure(settings_module=os.path.dirname(os.path.realpath(__file__)) + '/settings.yml')

    # TESTS TYPE
    def test_extract_type_liqui(self):
        type = Analyser.extract_type(LIQUI_BUY_ORDER, LIQUI)

        assert type == Types.BUY

    def test_extract_type_binance(self):
        type = Analyser.extract_type(BINANCE_SELL_ORDER, BINANCE)

        assert type == Types.SELL

    def test_extract_type_unknown(self):
        type = Analyser.extract_type({}, TOTO)

        assert type == Types.UNKNOWN

    def test_extract_type_liqui_order(self):
        type = Analyser.extract_type(LIQUI_FETCH_BUY_ORDER, LIQUI)

        assert type == Types.BUY

    def test_extract_type_binance_order(self):
        type = Analyser.extract_type(BINANCE_FETCH_SELL_ORDER, BINANCE)

        assert type == Types.SELL

    # TESTS START AMOUNT
    def test_extract_start_amount_liqui(self):
        amount = Analyser.extract_start_amount(LIQUI_BUY_ORDER, LIQUI)

        assert amount == 199

    def test_extract_start_amount_binance(self):
        amount = Analyser.extract_start_amount(BINANCE_SELL_ORDER, BINANCE)

        assert amount == 192

    def test_extract_start_amount_unknown(self):
        amount = Analyser.extract_start_amount({}, TOTO)

        assert amount == 0

    def test_extract_start_amount_liqui_order(self):
        amount = Analyser.extract_start_amount(LIQUI_FETCH_BUY_ORDER, LIQUI)

        assert amount == 199

    def test_extract_start_amount_binance_order(self):
        amount = Analyser.extract_start_amount(BINANCE_FETCH_SELL_ORDER, BINANCE)

        assert amount == 192

    # TESTS REMAINING AMOUNT
    def test_extract_remaining_amount_liqui(self):
        amount = Analyser.extract_remaining_amount2(LIQUI_BUY_ORDER, LIQUI)

        assert amount == 10

    def test_extract_remaining_amount_binance(self):
        amount = Analyser.extract_remaining_amount2(BINANCE_SELL_ORDER, BINANCE)

        assert amount == 20

    def test_extract_remaining_amount_unknown(self):
        amount = Analyser.extract_remaining_amount2({}, TOTO)

        assert amount == 0

    def test_extract_remaining_amount_liqui_order(self):
        amount = Analyser.extract_remaining_amount_order(LIQUI_FETCH_BUY_ORDER, LIQUI)

        assert amount == 10

    def test_extract_remaining_amount_binance_order(self):
        amount = Analyser.extract_remaining_amount_order(BINANCE_FETCH_SELL_ORDER, BINANCE)

        assert amount == 20

    def test_extract_remaining_amount_unknown_order(self):
        amount = Analyser.extract_remaining_amount_order({}, TOTO)

        assert amount == 0

    # TESTS PRICE
    def test_extract_price_liqui(self):
        price = Analyser.extract_price2(LIQUI_BUY_ORDER, LIQUI)

        assert price == 0.00008469

    def test_extract_price_binance(self):
        price = Analyser.extract_price2(BINANCE_SELL_ORDER, BINANCE)

        assert price == 0.00008762

    def test_extract_price_unknown(self):
        price = Analyser.extract_price2({}, TOTO)

        assert price == 0

    def test_extract_price_liqui_order(self):
        price = Analyser.extract_price2(LIQUI_FETCH_BUY_ORDER, LIQUI)

        assert price == 0.00008469

    def test_extract_price_binance_order(self):
        price = Analyser.extract_price2(BINANCE_FETCH_SELL_ORDER, BINANCE)

        assert price == 0.00008762

    # TESTS STATUS
    def test_extract_status_liqui(self):
        status = Analyser.extract_status(LIQUI_BUY_ORDER, LIQUI)

        assert status == Status.ONGOING

    def test_extract_status_binance(self):
        status = Analyser.extract_status(BINANCE_SELL_ORDER, BINANCE)

        assert status == Status.DONE

    def test_extract_status_unknown(self):
        status = Analyser.extract_status({}, TOTO)

        assert status == Status.UNKNOWN

    def test_extract_status_liqui_order(self):
        status = Analyser.extract_status_order(LIQUI_FETCH_BUY_ORDER, LIQUI)

        assert status == Status.ONGOING

    def test_extract_status_binance_order(self):
        status = Analyser.extract_status_order(BINANCE_FETCH_SELL_ORDER, BINANCE)

        assert status == Status.DONE

    def test_extract_status_unknown_order(self):
        status = Analyser.extract_status_order({}, TOTO)

        assert status == Status.UNKNOWN

    #TESTS EXTRACT ORDER
    def test_extract_good_order(self):
        depth = [[PRICE, VOLUME]]
        analyser = Analyser()

        order = analyser.extract_good_order(depth)

        assert order[0] == PRICE
        assert order[1] == VOLUME

    def test_extract_no_good_order(self):
        depth = [[PRICE, 1]]
        analyser = Analyser()

        order = analyser.extract_good_order(depth)

        assert order[0] == PRICE
        assert order[1] == 0
