from marshmallow import Schema, fields, post_load

from network.models.Liqui.ApiKeyRights import ApiKeyRights


class ApiKeyRightsSchema(Schema):
    info = fields.Boolean()
    trade = fields.Boolean()
    withdraw = fields.Boolean()

    @post_load()
    def make_api_key_rights(self, data):
        return ApiKeyRights(**data)
