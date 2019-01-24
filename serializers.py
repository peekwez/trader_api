# _*_ coding: utf-8 -*-

from marshmallow import fields, validate

from extensions import ma

# serializer
class TickerSchema(ma.Schema):

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(1))
    symbol = fields.String(required=True, validate=validate.Length(1))
    sector = fields.String(validate=validate.Length(1), allow_none=True)
    industry = fields.String(validate=validate.Length(1), allow_none=True)
    exchange = fields.String(validate=validate.Length(1), allow_none=True)
    market = fields.String(required=True, validate=validate.Length(1))
    type = fields.String(required=True, validate=validate.Length(1))

    class Meta:
        fields = (
            "name", "exchange","symbol", "type",
            "market","sector","industry",
        )
        ordered = True


class PriceSchema(ma.Schema):

    class Meta:
        fields  = (
            "date","open","high",
            "low","close","adj_close",
            "volume","dollar_volume"
        )
        ordered =  True


class TickerPricesSchema(ma.Schema):

    ticker = fields.Nested(TickerSchema)
    prices = fields.Nested(PriceSchema,many=True)

    class Meta:
        ordered = True


class UserSchema(ma.Schema):

    class Meta:
        fields = (
            "first_name", "last_name",
            "email","is_admin", "id",
        )
        ordered = True
