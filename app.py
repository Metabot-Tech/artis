import logging
import sys
from strategies.arbitrage import Arbitrage

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(name)-40s %(levelname)-8s %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main():

    logger.debug("Creating strategy")
    strategy = Arbitrage()

    logger.info("Start running current strategy")
    strategy.run()
    logger.info("Finished running current strategy")


    # Test Bittrex
    #bittrex = BittrexClient(settings.BITTREX.API_KEY, settings.BITTREX.API_SECRET)
    #balance_response = bittrex.get_balance('BTC')
    #print(balance_response.balance)

    # Test liqui
    #liqui = LiquiClient(settings.LIQUI.API_KEY, settings.LIQUI.API_SECRET)
    #balance_response = liqui.get_balances()
    #print(balance_response.funds)

if __name__ == '__main__':
    main()
