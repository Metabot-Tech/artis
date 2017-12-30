import logging
import sys
import datetime
from strategies.balance import Balance

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
    strategy = Balance("TRX", "LIQUI", "BINANCE")

    logger.info("Start running current strategy")
    strategy.run()
    logger.info("Finished running current strategy")

if __name__ == '__main__':
    main()
