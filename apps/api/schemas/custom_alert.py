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
