from dynaconf import settings
from clients.BittrexClient import BittrexClient
from settings.setup import setup_settings


def main():
    setup_settings()

    client = BittrexClient(settings.API_KEY, settings.API_SECRET)
    balance_response = client.get_balance('BTC')
    print(balance_response.result.balance)

if __name__ == '__main__':
    main()
