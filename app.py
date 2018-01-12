import logging
import sys
from database.database import Database
from strategies.balance import Balance
from strategies.trader import Trader
from strategies.analyser import Analyser
from strategies.reporter import Reporter
from strategies.helper import Helper
from logging.handlers import TimedRotatingFileHandler
from dynaconf import settings

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logFormatter = logging.Formatter("%(asctime)s %(name)-40s %(levelname)-8s %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = TimedRotatingFileHandler("logs/artis.log", when="midnight", interval=1)
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
        reporter.error("I am dead, please revive me!")

if __name__ == '__main__':
    main()
