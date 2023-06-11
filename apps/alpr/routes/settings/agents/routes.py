import logging
from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from apps import db
from apps.alpr.models.settings import AgentSettings
from apps.alpr.routes.settings.agents import blueprint
from apps.authentication.routes import ROLE_ADMIN
import apps.helpers as helper
from apps.helpers import message


@blueprint.route('/search', methods=["GET"])
@login_required
def search():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    query = AgentSettings.query

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(AgentSettings.agent_uid.like(f'%{search}%'), AgentSettings.agent_label.like(f'%{search}%')))
    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helper.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'agent_uid': record.agent_uid,
            'agent_label': record.agent_label,
            'ip_hostname': record.ip_hostname,
            'port': record.port,
            'created': dt.astimezone(record.created),
            'last_seen': dt.astimezone(record.last_seen)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/edit', methods=['GET', 'PUT'])
@login_required
def edit():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'GET':
        agent = AgentSettings.filter_by_id(request.args.get('id'))

        dt = helper.Timezone(current_user)

        if agent:
            context = {'id': agent.id, 'enabled': agent.enabled, 'agent_uid': agent.agent_uid,
                       'agent_label': agent.agent_label, 'ip_hostname': agent.ip_hostname, 'port': agent.port,
                       'created': dt.astimezone(agent.created), 'last_seen': dt.astimezone(agent.last_seen)
                       }
            return jsonify(context), 200
        else:
            return jsonify({'error': message['record_not_found']}), 404

    if request.method == 'PUT':
        data = request.form

        # Validate before proceeding
        ip_hostname = data.get('ip_hostname')
        port = data.get('port')
        enabled = bool(data.get('enabled'))

        # Check to if we can even put the values through the validators
        if len(ip_hostname) == 0:
            return jsonify({'error': message['ip_hostname_not_valid']}), 404
        if port is None:
            return jsonify({'error': message['port_not_valid']}), 404
        else:
            # Cast it as an int
            port = int(port)

        is_valid_hostname = helper.is_valid_hostname(ip_hostname)
        is_valid_ip = helper.is_valid_ip(ip_hostname)

        if not is_valid_hostname and not is_valid_ip:
            return jsonify({'error': message['ip_hostname_not_valid']}), 404
        if not helper.is_valid_port(port):
            return jsonify({'error': message['port_not_valid']}), 404

        # Lets find the agent in the db
        agent = AgentSettings.filter_by_id(data.get('id'))

        if agent:
            try:
                # Update it!
                agent.ip_hostname = ip_hostname
                agent.port = port
                agent.enabled = enabled
                agent.save()

                # Reload workers and queues. Someone may have enabled an agent which will require a worker and queue
                # dedicated to that agent
                # reload_wqs()

            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404

            return jsonify({'message': message['agent_updated']}), 200
        else:
            return jsonify({'error': message['agent_not_found']}), 404
