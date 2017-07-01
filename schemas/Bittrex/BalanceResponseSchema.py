from marshmallow import Schema, fields, post_load
from schemas.Bittrex.BalanceSchema import BalanceSchema
from models.Bittrex.BalanceResponse import BalanceResponse


class BalanceResponseSchema(Schema):
    success = fields.Boolean()
    message = fields.String()
    result = fields.Nested(BalanceSchema)

    @post_load
    def make_balance_response(self, data):
        return BalanceResponse(**data)
