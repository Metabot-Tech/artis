import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from network.clients.BaseClient import *
from network.schemas.Liqui import AccountSchema

PUBLIC_SET = ['info', 'ticker', 'depth', 'trades']

TRADE_SET = ['getInfo', 'Trade', 'ActiveOrders', 'OrderInfo', 'CancelOrder']


class LiquiClient(BaseClient):
    _base_url = 'https://api.liqui.io/%s'

    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''

    def api_query(self, method, options=None):
        if not options:
            options = {}
        nonce = str(int(time.time()))

        if method in PUBLIC_SET:
            request_url = (LiquiClient._base_url % 'api/3/') + method + '?' + urlencode(options)
            ret = requests.get(request_url)
            return ret.json()
        elif method in TRADE_SET:
            parameters = {'method': method, "nonce": nonce}
            parameters.update(options)
            request_url = (LiquiClient._base_url % 'tapi')

            signature = hmac.new(bytearray(self.api_secret, 'utf8'), urlencode(parameters).encode('utf8'), hashlib.sha512).hexdigest()
            headers = {'Sign': signature, 'Key': self.api_key}
            ret = requests.post(request_url, data=parameters, headers=headers)
            return ret.json()
        else:
            raise Exception('Method not found for current client')

    def get_balance(self, currency):
        pass

    def get_balances(self):
        response = self.api_query('getInfo')
        return AccountSchema().load(response['return']).data
