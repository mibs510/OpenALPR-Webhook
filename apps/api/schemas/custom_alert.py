from ...alpr.models.custom_alert import CustomAlert
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import ModelSchema
from apps import db


class CustomAlertSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        fields = ("id", "alpr_group_id", "license_plate", "region_match", "description", "notify_user_ids",
                  "submitted_by_user_id")
        model = CustomAlert
        unknown = EXCLUDE
        sqla_session = db.session
    alpr_group_id = fields.Integer(default=None, missing=None)
    license_plate = fields.String(default=None, missing=None)
    region_match = fields.Boolean(default=None, missing=None)
    description = fields.String(default=None, missing=None)
    notify_user_ids = fields.Dict(default=None, missing=None)
    submitted_by_user_id = fields.Integer(default=None, missing=None)
