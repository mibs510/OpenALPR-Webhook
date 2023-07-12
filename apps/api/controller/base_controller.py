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

import flask
import traceback
from flask import jsonify
from apps.api.exception import InvalidUsage

app = flask.current_app


class BaseController:

    # Set Json response
    def send_response(self, data, status_code=200):
        res = {
            "data": data,
            'status': status_code
        }
        resp = jsonify(res)
        return resp

    # Set success response.
    def success(self, data, message="", code=200):
        """form final respose format

        Args:
            data (dict/list): for single record it would be dictionary and for multiple records it would be list.
            message (str): operation response message. Defaults to "".
            code (int): Http response code. Defaults to 200.

        Returns:
            dictionary of response data
            {
                data: [],
                message: "",
                status: 200,
            }
        """
        res = {
            "data": data,
            "message": message,
            'status': code
        }
        resp = jsonify(res)
        return resp

    # Set error response.
    def error(self, e, code=422):
        msg = str(e)
        # if isinstance(e, InvalidUsage):
        #     msg = e.message

        # app.logger.error(traceback.format_exc())
        res = {
            # 'error':{
            #     'description': traceback.format_exc()
            # },
            "message": msg,
            'status': code
        }
        return res, code

    def errorGeneral(self, e, code=422):
        msg = str(e)
        # if isinstance(e, InvalidUsage):
        #     msg = e.message
        res = {
            "message": msg,
            'status': code
        }
        return res, code
        # msg = 'An exception occurred: {}'.format(error)
        # res = {
        #     'errors':msg,
        #     'status': code
        # }
        # return res

    def simple_response(self, message, status_code):
        res = {
            "message": message,
            'status': status_code
        }
        resp = jsonify(res)
        return resp
