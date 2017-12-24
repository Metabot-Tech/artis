from marshmallow import Schema, fields, post_load

from network.models.Bittrex.Balance import Balance


class BalanceSchema(Schema):
    Currency = fields.String()
    Balance = fields.Decimal()
    Available = fields.Decimal()
    Pending = fields.Decimal()
    CryptoAddress = fields.String(allow_none=True)

    @post_load
    def make_balance(self, data):
        return Balance(**data)
