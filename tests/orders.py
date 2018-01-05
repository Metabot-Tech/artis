LIQUI_BUY_ORDER = {
    'info': {'success': 1, 'return': {
        'received': 199.00,
        'remains': 10.0,
        'init_order_id': 183892657,
        'order_id': 111111,
        'funds': {'trx': 70398.33970153626, 'eth': 2.790871143206755},
        'trades': [{
            'trade_id': 56384073,
            'pair': None,
            'type': 'buy',
            'amount': 189.00,
            'rate': 8.469e-05,
            'order_id': 183892657,
            'is_your_order': True,
            'timestamp': 0,
            }],
        }, 'stat': {
        'isSuccess': True,
        'serverTime': '00:00:00.0185063',
        'time': '00:00:00.0361195',
        'errors': None,
        }},
    'id': '183892657',
    'timestamp': 1514962677426,
    'datetime': '2018-01-03T06:57:57.426Z',
    'status': 'open',
    'symbol': 'TRX/ETH',
    'type': 'limit',
    'side': 'buy',
    'price': 8.469e-05,
    'cost': 0.0168873379855209,
    'amount': 199.00,
    'remaining': 189.00,
    'filled': 10.0,
    'fee': None,
}

BINANCE_SELL_ORDER = {
    'info': {
        'symbol': 'TRXETH',
        'orderId': 5256209,
        'clientOrderId': '1hr4NbO0tBuyQ7CiLUV85f',
        'transactTime': 1514962677490,
        'price': '0.00008762',
        'origQty': '192.00000000',
        'executedQty': '172.00000000',
        'status': 'FILLED',
        'timeInForce': 'GTC',
        'type': 'LIMIT',
        'side': 'SELL',
    }, 'id': '5256209'
}

BINANCE_ANOTHER_SELL_ORDER = {
    'info': {
        'symbol': 'TRXETH',
        'orderId': 6183482,
        'clientOrderId': 'tRLWnGuSPmzDIInEem3XeW',
        'transactTime': 1515088771607,
        'price': '0.00020749',
        'origQty': '202.00000000',
        'executedQty': '202.00000000',
        'status': 'FILLED',
        'timeInForce': 'GTC',
        'type': 'LIMIT',
        'side': 'SELL',
    }, 'id': '6183482'
}

LIQUI_FETCH_BUY_ORDER = {
    'amount': 199.00,
    'cost': None,
    'datetime': '2018-01-03T06:57:57.000Z',
    'fee': None,
    'filled': None,
    'id': '183892657',
    'info': {
          'amount': 10.0,
          'id': '183892657',
          'pair': 'trx_eth',
          'rate': 8.469e-05,
          'start_amount': 199.00,
          'status': 0,
          'timestamp_created': 1514962677,
          'type': 'buy'},
    'price': 8.469e-05,
    'remaining': None,
    'side': 'buy',
    'status': 'open',
    'symbol': 'TRX/ETH',
    'timestamp': 1514962677000,
    'type': 'limit'
}

BINANCE_FETCH_SELL_ORDER = {
    'amount': 192.0,
    'cost': 0.01682304,
    'datetime': '2018-01-03T06:57:57.490Z',
    'fee': None,
    'filled': 192.0,
    'id': '5256209',
    'info': {
        'clientOrderId': '1hr4NbO0tBuyQ7CiLUV85f',
        'executedQty': '172.00000000',
        'icebergQty': '0.00000000',
        'isWorking': True,
        'orderId': 5256209,
        'origQty': '192.00000000',
        'price': '0.00008762',
        'side': 'SELL',
        'status': 'FILLED',
        'stopPrice': '0.00000000',
        'symbol': 'TRXETH',
        'time': 1514962677490,
        'timeInForce': 'GTC',
        'type': 'LIMIT'},
    'price': 8.762e-05,
    'remaining': 0.0,
    'side': 'sell',
    'status': 'closed',
    'symbol': 'TRX/ETH',
    'timestamp': 1514962677490,
    'type': 'limit'
}
