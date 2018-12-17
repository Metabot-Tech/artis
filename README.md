# Artis
Simple trading bot for cryptocurrencies.

We decided to open-source the bot since we are no longer using it. The main strategy used is [arbitrage](https://www.investopedia.com/terms/a/arbitrage.asp). The supported markets are [Liqui](https://liqui.io/) and [Binance](https://www.binance.com). We always traded between `ETH` and another coin. Mainly `TRX` and `ADX`.

Some of the code is legacy from other strategies or attempts. Start from [strategies/balance](https://github.com/Metabot-Tech/artis/blob/master/strategies/balance.py) if you want to analyse the code. I started a refactor in one of the branches, but I have not finished it. The main algorithm is pretty much all unit tested.

We also wanted to add automatic balancing between networks, but never got to it. There is still some code for that all around.

# Setup
It is meant to run in docker. The `docker-compose.yml` file will spawn the service and the database. It will record all the transactions made by the bot and the balance of each coin in each market.

You will need to add a `settings.yaml` file with the following information:
```yaml
DYNACONF:
    MARKETS: ['LIQUI', 'BINANCE']
    SLACK:
        TOKEN: '<YOUR TOKEN HERE>'
        CHANNEL: '#trading_bot' # Change this for the channel you want
    LIQUI:
        TIMEOUT: 30000
        SERVICE_FEE_HIGH: 0.0025 # Sometimes markets have a different fee when you place an order vs fulfill one
        SERVICE_FEE_LOW: 0.0010
        COINS: ['ADX', 'TRX'] # Supported coins
        API_KEY: <API KEY HERE>
        API_SECRET: <API SECRET HERE>
    BINANCE:
        TIMEOUT: 10000
        SERVICE_FEE_HIGH: 0.0010
        SERVICE_FEE_LOW: 0.0010
        COINS: ['ADX', 'TRX']
        API_KEY: <API KEY HERE>
        API_SECRET: <API SECRET HERE>
    DATABASE_URL: postgresql://{}:{}@localhost/{}
    COIN: "TRX" # Selected coin
    PRECISION: 0 # How many digits to use after the dot
    AMOUNT_TO_TRADE: 0.1 # Trade volume in ETH to trade each time
    MINIMUM_AMOUNT_TO_TRADE: 0.015 # Minimum volume in ETH for a trade to occur
    PROFIT_FACTOR: 1.0135 # Minimum difference (in %) in prices for a trade to occur
    PROFIT_REDUCTION: 0.005 # Reduction of profit if we missed the trade
    SERVICE_NUMBER: 1
    SLEEP_TIME: 0.05 # Sleep between iterations (avoid too many API requests)
```
