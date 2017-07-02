import requests
import hashlib
import hmac
import time

from urllib.parse import urlencode
from clients.BaseClient import BaseClient
from schemas.Bittrex.BalanceSchema import BalanceSchema

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

PUBLIC_SET = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getorderbook',
              'getmarkethistory']

MARKET_SET = ['getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit']

ACCOUNT_SET = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw',
               'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']


class BittrexClient(BaseClient):
    _base_url = 'https://bittrex.com/api/v1.1/%s/'

    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''

    def api_query(self, method, options=None):
        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))
        request_url = ''

        if method in PUBLIC_SET:
            request_url = (BittrexClient._base_url % 'public') + method + '?'
        elif method in MARKET_SET:
            request_url = (BittrexClient._base_url % 'market') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        elif method in ACCOUNT_SET:
            request_url = (BittrexClient._base_url % 'account') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'

        request_url += urlencode(options)

        signature = hmac.new(bytearray(self.api_secret, 'utf8'), request_url.encode('utf8'), hashlib.sha512).hexdigest()

        headers = {"apisign": signature}

        ret = requests.get(request_url, headers=headers)

        return ret.json()

    def get_balance(self, currency):
        response = self.api_query('getbalance', {'currency': currency})
        return BalanceSchema().load(response['result']).data

    def get_balances(self):
        pass
