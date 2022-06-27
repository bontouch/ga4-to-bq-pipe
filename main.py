from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest
from google.cloud import firestore


def handle_update(request):
    req_data = request.get_json(silent=True)
    cherry_picked_apps = None
    """if req_data is not None and 'includedApps' in req_data:
        cherry_picked_apps = req_data['includedApps']
    if req_data is not None and ('startMonth' in req_data) and ('endMonth' in req_data):
        update_downloads(datetime.datetime.strptime(req_data['startMonth'], "%Y%m"),
                         datetime.datetime.strptime(req_data['endMonth'], "%Y%m"),
                         cherry_picked_apps)
    else:
        print("Fetching last month's report.")
        update_downloads(cherry_picked_apps=cherry_picked_apps)
    """
    return "Success!", 200


print("Running!")