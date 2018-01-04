import logging

logger = logging.getLogger(__name__)


def intersect(a, b):
    return list(set(a) & set(b))


class Helper(object):
    @staticmethod
    def safe_call(method, args, retry=5):
        for i in range(retry):
            try:
                return method(*args)
            except:
                logger.exception("Exception during method call")
        raise Exception("Impossible to call method")

    @staticmethod
    def biggest_coin(amount1, amount2, price):
        return max([amount1, amount2]) / price


