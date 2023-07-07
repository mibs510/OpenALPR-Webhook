from flask import render_template
from flask_login import login_required


from apps.alpr.routes.alerts import blueprint


@blueprint.route('/custom', methods=["GET"])
@login_required
def custom():
    return render_template('home/custom-alerts.html', segment='alerts-custom-alerts')


@blueprint.route('/rekor', methods=["GET"])
@login_required
def rekor():
    return render_template('home/alerts.html', segment='alerts-rekor-scout')
