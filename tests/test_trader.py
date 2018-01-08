import unittest
from strategies.trader import Trader
from dynaconf import settings

EXPOSURE = 1.0135
HIGH_EXPOSURE = 1.0685


class TestTrader(unittest.TestCase):
    def setUp(self):
        settings.PROFIT_FACTOR = 1.0135
        settings.PROFIT_REDUCTION = 0.005

    def test_new_exposure(self):
        exposure = Trader.new_exposure(EXPOSURE)

        assert exposure == 1.008500

    def test_new_exposure_greater(self):
        exposure = Trader.new_exposure(HIGH_EXPOSURE)

        assert exposure == 1.043130