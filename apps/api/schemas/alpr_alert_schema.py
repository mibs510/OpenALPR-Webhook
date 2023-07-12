#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
