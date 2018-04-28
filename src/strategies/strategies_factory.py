from .balance import Balance


class StrategiesFactory(object):
    @staticmethod
    def create_strategy(strategy_name, *args):
        if strategy_name == "BALANCE":
            return Balance(*args)
        raise Exception("Unknown strategy: {}".format(strategy_name))
