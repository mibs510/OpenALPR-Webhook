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
    custom_alerts = CustomAlert().get_dashboard_records()

    return render_template('home/index.html', segment='index', alpr_group_records=alpr_group_records,
                           alpr_alert_records=alpr_alert_records, custom_alerts=custom_alerts,
                           quick_stats=cache.get_quick_stats(), regions=cache.get_us_map_regions(),
                           us_map_regions=cache.get_us_map_series(),
                           plates_captured_chart_series=cache.get_chart_series(ChartType.PLATES_CAPTURED_CHART),
                           alert_chart_series=cache.get_chart_series(ChartType.ALERT_CHART),
                           custom_alert_chart_series=cache.get_chart_series(ChartType.CUSTOM_ALERT),
                           top_region_chart_series=cache.get_chart_series(ChartType.TOP_SECOND_REGION_CHART),
                           plates_captured_alerts_chart_labels=cache.get_chart_labels(),
                           top_region_chart_labels=cache.get_chart_labels(ChartType.TOP_SECOND_REGION_CHART),
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
