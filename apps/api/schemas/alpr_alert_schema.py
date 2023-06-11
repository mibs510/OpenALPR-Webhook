from ...alpr.models.alpr_alert import ALPRAlert
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import ModelSchema
from apps import db

# Defaults & missing
default_missing_custom_data = {"API_KEY": ""}


class ALPRAlertSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        fields = ("id", "data_type", "version", "epoch_time", "agent_uid", "alert_list", "alert_list_id", "site_name",
                  "camera_name", "camera_number", "plate_number", "description", "list_type", "group", "custom_data")
        model = ALPRAlert
        unknown = EXCLUDE
        sqla_session = db.session
    data_type = fields.String(default=None, missing=None)
    version = fields.Integer(default=None, missing=None)
    epoch_time = fields.Integer(default=None, missing=None)
    agent_uid = fields.String(default=None, missing=None)
    alert_list = fields.String(default=None, missing=None)
    alert_list_id = fields.Integer(default=None, missing=None)
    site_name = fields.String(default=None, missing=None)
    camera_name = fields.String(default=None, missing=None)
    camera_number = fields.Integer(default=None, missing=None)
    plate_number = fields.String(default=None, missing=None)
    description = fields.String(default=None, missing=None)
    list_type = fields.String(default=None, missing=None)
    group = fields.Dict(default=None, missing=None)
    custom_data = fields.Dict(default=default_missing_custom_data, missing=default_missing_custom_data)
