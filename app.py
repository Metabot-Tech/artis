import logging
import sys
from strategies.balance import Balance

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(name)-40s %(levelname)-8s %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    logger.debug("Creating strategy")
    strategy = Balance("TRX", "LIQUI", "BINANCE")

    logger.info("Start running current strategy")
    strategy.run()
    logger.info("Finished running current strategy")

if __name__ == '__main__':
    main()
