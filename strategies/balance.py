import itertools
import logging
import time
import asyncio
import strategies.helpers as helpers
import database.operations as db
from database.models.trade import Trade
from database.models.coins import Coins
from dynaconf import settings
from strategies.trader import Trader
from strategies.watchdog import WatchDog
from strategies.analyser import Analyser

logger = logging.getLogger(__name__)


class Analysis:
    def __init__(self, buy, sell, exposure):
        self.buy = buy
        self.sell = sell
        self.exposure = exposure


class Balance(object):
    def __init__(self, coin, market1, market2):
        self.trader = Trader()
        self.analyser = Analyser()
        self.coin = coin
        self.markets = [market1, market2]
        self.running = True

    def run(self):
        logger.debug("Starting balance strategy of {}".format(self.coin))
        self.running = True
        loop = asyncio.get_event_loop()

        while self.running:
            logger.info("Balance started for coin {}".format(self.coin))

            # Get latest prices
            depth_tasks = [self.analyser.get_latest_depth(i, self.coin, {'limit': 5}) for i in self.markets]
            depth_results = loop.run_until_complete(asyncio.gather(*depth_tasks))
            depth = dict(zip(self.markets, depth_results))

            # Analyse best offer
            asks = dict(zip(self.markets, [depth.get(i).get("asks")[0] for i in self.markets]))
            bids = dict(zip(self.markets, [depth.get(i).get("bids")[0] for i in self.markets]))

            analyses = [
                Analysis(self.markets[0], self.markets[1], bids.get(self.markets[1])[0]/asks.get(self.markets[0])[0]),
                Analysis(self.markets[1], self.markets[0], bids.get(self.markets[0])[0]/asks.get(self.markets[1])[0])
            ]

            # Perform balance
            for analysis in analyses:
                logger.debug("Exposure: {}".format(analysis.exposure))

                # Check profit
                if analysis.exposure < settings.PROFIT_FACTOR:
                    continue

                # Check available volume
                volumes = {
                    'ask': asks.get(analysis.buy)[1],
                    'bid': bids.get(analysis.sell)[1]
                }

                volumes_wanted = {
                    'buy': round(settings.AMOUNT_TO_TRADE/asks.get(analysis.buy)[0], 6),
                    'sell': round(settings.AMOUNT_TO_TRADE/bids.get(analysis.sell)[0], 6)
                }

                if volumes.get('ask') < volumes_wanted.get('buy'):
                    continue

                if volumes.get('bid') < volumes_wanted.get('sell'):
                    continue

                # Buy and sell
                input("Press Enter to buy/sell...")
                buy_order = self.trader.buy(analysis.buy, self.coin, volumes_wanted.get('buy'), asks.get(analysis.buy)[0])
                sell_order = self.trader.sell(analysis.sell, self.coin, volumes_wanted.get('sell'), bids.get(analysis.sell)[0])

                print(buy_order)
                print(sell_order)

                input("Press Enter to continue...")

            logger.info("Balance done for coin {}".format(self.coin))



            # Sleep
            time.sleep(1)

