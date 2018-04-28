import logging
import sys
from .database.database import Database
from .strategies.balance import Balance
from .traders.trader import Trader
from .analysers.analyser import Analyser
from .helpers.reporter import Reporter
from .helpers.helper import Helper
from logging.handlers import TimedRotatingFileHandler
from dynaconf import settings

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logFormatter = logging.Formatter("%(asctime)s %(name)-40s %(levelname)-8s %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = TimedRotatingFileHandler("logs/artis{}.log".format(settings.SERVICE_NUMBER), when="midnight", interval=1)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

logger = logging.getLogger(__name__)


def main():
    reporter = Reporter()
    try:
        logger.info("Creating strategy")
        strategy = Balance(settings.COIN, "LIQUI", "BINANCE", Trader(), Analyser(), reporter, Database(), Helper())

        logger.info("Start running current strategy")
        strategy.run()
        logger.info("Finished running current strategy")
    except:
        logger.exception("")
        reporter.error("Service {} is dead, please revive it!".format(settings.SERVICE_NUMBER))

if __name__ == '__main__':
    main()
