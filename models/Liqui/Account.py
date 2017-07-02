class Account:
    def __init__(self, funds, rights, transaction_count, open_orders, server_time):
        self.funds = funds
        self.rights = rights
        self.transaction_count = transaction_count
        self.open_orders = open_orders
        self.server_time = server_time
