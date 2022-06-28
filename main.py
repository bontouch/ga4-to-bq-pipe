from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest
from google.cloud import firestore, bigquery
from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar
import pandas as pd
import pandas_gbq

PROJECT_ID = "bondigest-318608"
db = firestore.Client(project=PROJECT_ID)
bq_client = bigquery.Client(project=PROJECT_ID)


def get_apps_from_config() -> [dict]:
    docs = db.collection(u'bondigest').stream()
    docs_ = []
    for doc in docs:
        doc_ = doc.to_dict()
        doc_["id"] = doc.id
        docs_.append(doc_)
    return docs_


def ga4_response_to_df(response):
    dim_len = len(response.dimension_headers)
    metric_len = len(response.metric_headers)
    all_data = []
    for row in response.rows:
        row_data = {}
        for i in range(0, dim_len):
            row_data.update({response.dimension_headers[i].name: row.dimension_values[i].value})
        for i in range(0, metric_len):
            row_data.update({response.metric_headers[i].name: row.metric_values[i].value})
        all_data.append(row_data)
    df = pd.DataFrame(all_data)
    return df


def get_ga4_report_df(property_id, dimensions, metrics, start_date, end_date):
    dimensions_ga4 = []
    for dimension in dimensions:
        dimensions_ga4.append(Dimension(name=dimension))
    metrics_ga4 = []
    for metric in metrics:
        metrics_ga4.append(Metric(name=metric))
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(property=f"properties/{property_id}",
                               dimensions=dimensions_ga4,
                               metrics=metrics_ga4,
                               date_ranges=[DateRange(start_date=start_date, end_date=end_date)])
    response = client.run_report(request)
    return ga4_response_to_df(response)


def update(req_data):
    table_id = "{}.ccdata.{}".format(PROJECT_ID, req_data['targetTable'])

    if 'dataFromLast' in req_data:
        if req_data['dataFromLast'] == 'month':
            start_date = (datetime.today().date() - relativedelta(months=1)).replace(day=1)
            end_date = start_date.replace(day=calendar.monthrange(start_date.year, start_date.month)[1]).strftime(
                "%Y-%m-%d")
            start_date = start_date.strftime("%Y-%m-%d")

        if req_data['dataFromLast'] == 'day':
            start_date = (datetime.today().date() - relativedelta(days=1)).strftime("%Y-%m-%d")
            end_date = start_date
    else:
        end_date = req_data['endDate']
        start_date = req_data['startDate']

    print("Start date: " + start_date)
    print("End date: " + end_date)

    for app in get_apps_from_config():
        print("Running for ", app['app'], "...")
        try:
            if 'includedApps' in req_data and app not in req_data['includedApps']:
                continue

            df = get_ga4_report_df(app['property_id'], req_data['dimensions'], req_data['metrics'],
                                   start_date, end_date)
            df['app'] = app['app']
            pandas_gbq.to_gbq(df, table_id, PROJECT_ID, if_exists="append")
        except Exception as e:
            print(e)
            print(app['app'] + " failed.")


def handle_update(request):
    req_data = request.get_json(silent=True)
    update(req_data)
    return "Success!", 200


print("Running!")