from apps.alpr.enums import ChartType
from apps.alpr.models.cache import Cache
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.alpr_alert import ALPRAlert
from apps.alpr.models.custom_alert import CustomAlert

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound


@blueprint.route('/dashboard')
@login_required
def index():
    cache = Cache().filter_by_year()
    alpr_group_records = ALPRGroup().get_dashboard_records()
    alpr_alert_records = ALPRAlert().get_dashboard_records()
    custom_alerts = CustomAlert().get_dashboard_records(current_user)

    return render_template('home/index.html', segment='index', alpr_group_records=alpr_group_records,
                           alpr_alert_records=alpr_alert_records, custom_alerts=custom_alerts,
                           quick_stats=cache.get_quick_stats(), regions=cache.get_us_map_regions(),
                           us_map_regions=cache.get_us_map_series(),
                           plates_captured_chart_series=cache.get_chart_series(ChartType.PLATES_CAPTURED_CHART),
                           alert_chart_series=cache.get_chart_series(ChartType.ALERT_CHART),
                           top_region_chart_series=cache.get_chart_series(ChartType.TOP_REGION_CHART),
                           plates_captured_alerts_chart_labels=cache.get_chart_labels(),
                           top_region_chart_labels=cache.get_chart_labels(ChartType.TOP_REGION_CHART),
                           number_of_records=cache.get_number_of_records(),
                           size_of_databases=cache.get_all_db_file_sizes(), top_cameras=cache.get_top_cameras(),
                           number_of_records_raw=cache.get_number_of_records(raw=True),
                           size_of_databases_raw=cache.get_all_db_file_sizes(raw=True))


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment
    except:
        return None
