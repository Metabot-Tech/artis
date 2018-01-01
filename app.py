import logging
import sys
import datetime
from database.database import Database
from strategies.balance import Balance
from strategies.trader import Trader
from strategies.analyser import Analyser
from strategies.reporter import Reporter

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logFormatter = logging.Formatter("%(asctime)s %(name)-40s %(levelname)-8s %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("logs/logging-{}.log".format(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

logger = logging.getLogger(__name__)


def main():
    logger.debug("Creating strategy")
    strategy = Balance("TRX", "LIQUI", "BINANCE", Trader(), Analyser(), Reporter(), Database())

    logger.info("Start running current strategy")
    strategy.run()
    logger.info("Finished running current strategy")

if __name__ == '__main__':
    main()
