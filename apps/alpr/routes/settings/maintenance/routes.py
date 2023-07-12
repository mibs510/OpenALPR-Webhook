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

import logging
import platform

from flask import render_template, jsonify
from flask_login import login_required, current_user

from apps.alpr.models.cache import Cache, CameraCache, AgentCache
from apps.alpr.routes.settings.maintenance import blueprint
from apps.authentication.routes import ROLE_ADMIN
from worker_manager import WorkerManager
from worker_manager_enums import WMSCommand


@blueprint.route('/init/cache', methods=["GET"])
@login_required
def init_cache_db():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    # Drop all rows from each table
    Cache.query.delete()
    AgentCache.query.delete()
    CameraCache.query.delete()

    cache = Cache.filter_by_year()
    if cache is None:
        cache = Cache()
    cache.init()

    return jsonify({'msg': 'cache_initiated'}), 200


@blueprint.route('/shutdown/wms', methods=["POST"])
@login_required
def shutdown_wms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if platform.system() != "Linux":
        return jsonify({'error': 'Unsupported platform. Redis server is not running.'}), 404

    try:
        wms = WorkerManager(WMSCommand.STOP_ALL)
        logging.debug("Sending STOP_ALL command")
        wms.send()
        wms.command = WMSCommand.STOP_SERVER
        logging.debug("Sending STOP_SERVER command")
        wms.send()
    except Exception or TimeoutError as ex:
        logging.exception(ex)
        return jsonify({'error': str(ex)}), 404

    return jsonify({'message': 'Worker Manager Server shutdown successfully!'}), 200


@blueprint.route('/restart/wms', methods=["GET"])
@login_required
def restart_wms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    try:

        wms = WorkerManager(WMSCommand.STOP_ALL)
        logging.debug("Sending STOP_ALL command")
        wms.send()
        wms.command = WMSCommand.STOP_SERVER
        logging.debug("Sending STOP_SERVER command")
        wms.send()

        from apps import start_redis_workers
        start_redis_workers()

    except Exception or TimeoutError as ex:
        logging.exception(ex)
        if TimeoutError:
            return jsonify({'error': 'Connection to Worker Manager Server timed out!'}), 404
        elif Exception:
            return jsonify({'error': 'Unknown error occurred!'}), 404

    return jsonify({'msg': 'Worker Manager Server shutdown successfully!'}), 200
