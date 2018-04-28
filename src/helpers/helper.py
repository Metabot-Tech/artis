import logging
import math
from decimal import Decimal

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
    def round_down(amount, precision=0):
        return float(math.floor(Decimal.from_float(amount) * Decimal(10 ** precision)) / Decimal(10 ** precision))


