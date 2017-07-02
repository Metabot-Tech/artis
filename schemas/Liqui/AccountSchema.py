from marshmallow import Schema, fields, post_load
from schemas.Liqui.ApiKeyRightsSchema import ApiKeyRightsSchema
from models.Liqui.Account import Account


class AccountSchema(Schema):
    funds = fields.Dict()
    rights = fields.Nested(ApiKeyRightsSchema)
    transaction_count = fields.Integer()
    open_orders = fields.Integer()
    server_time = fields.Integer()

    @post_load()
    def make_account(self, data):
        return Account(**data)
