from dynaconf import settings
from clients.BittrexClient import BittrexClient
from clients.LiquiClient import LiquiClient
from settings.setup import setup_settings


def main():
    setup_settings()

    # Test Bittrex
    bittrex = BittrexClient(settings.BITTREX.API_KEY, settings.BITTREX.API_SECRET)
    balance_response = bittrex.get_balance('BTC')
    print(balance_response.balance)

    # Test liqui
    liqui = LiquiClient(settings.LIQUI.API_KEY, settings.LIQUI.API_SECRET)
    balance_response = liqui.get_balances()
    print(balance_response.funds)

if __name__ == '__main__':
    main()
