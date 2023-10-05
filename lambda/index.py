import json
import time
import os
from functools import reduce
import datetime as dt
import boto3
import requests
from jinja2 import Environment, FileSystemLoader

AUTH_URL = 'https://www.strava.com/oauth/token'
ACTIVITIES_URL = 'https://www.strava.com/api/v3/athlete/activities'
DATE_RANGE = 7


def get_access_token():
    """ Retrive access token from Parameter store and check if refresh needed."""

    ssm = boto3.client('ssm')

    app_param = ssm.get_parameter(Name='stravaapiapp', WithDecryption=True)
    app = json.loads(app_param['Parameter']['Value'])

    token_param = ssm.get_parameter(Name='stravaapitoken', WithDecryption=True)
    api_token = json.loads(token_param['Parameter']['Value'])

    should_refresh = False
    params = {}

    if not api_token.get('expires_at'):
        should_refresh = True
        params['grant_type'] = 'authorization_code'
        params['code'] = app['code']
    elif time.time() > api_token['expires_at']:
        should_refresh = True
        params['grant_type'] = 'refresh_token'
        params['refresh_token'] = api_token['refresh_token']

    if should_refresh:
        params['client_id'] = app['client_code']
        params['client_secret'] = app['client_secret']

        res = requests.post(AUTH_URL, params)
        if res.status_code == 200:
            res_data = res.json()

            api_token['expires_at'] = res_data['expires_at']
            api_token['access_token'] = res_data['access_token']
            api_token['refresh_token'] = res_data['refresh_token']

            ssm.put_parameter(Name='stravaapitoken',
                              Value=json.dumps(api_token), Overwrite=True)

    return api_token['access_token']


def scrape_api(access_token):
    """ Get last 7 days of activities from strava api."""

    data = None

    date_obj = dt.datetime.now()
    date_obj -= dt.timedelta(days=DATE_RANGE)
    url = f'{ACTIVITIES_URL}?after={dt.datetime.timestamp(date_obj)}'
    res = requests.get(url, params={'access_token': access_token})

    if res.status_code == 200:
        data = res.json()

    return data


def generate_html(data):
    """ Use email template to generate html from data."""

    def transform_activity(activity):
        """ Transform activity to pull out relevant info."""

        res = {}
        res['name'] = activity['name']
        res['distance'] = round(activity['distance'] / 1000, 2)
        res['duration'] = round(activity['elapsed_time'] / 60, 2)

        date_obj = dt.datetime.strptime(
            activity['start_date_local'], "%Y-%m-%dT%H:%M:%SZ")
        res['date'] = date_obj.strftime("%d/%m/%Y %H:%M")

        return res

    def reduce_summary(acc, activity):
        """ Reduce activity to summary."""

        acc['count'] += 1
        acc['total_time'] += activity['duration']
        acc['total_distance'] += activity['distance']
        return acc

    parsed_data = {}
    parsed_data['activities'] = list(map(transform_activity, data))
    parsed_data['summary'] = reduce(
        reduce_summary, parsed_data['activities'], {'count': 0, 'total_time': 0, 'total_distance': 0})

    date_obj = dt.datetime.now()
    parsed_data['to_date'] = date_obj.strftime("%d/%m/%Y")
    date_obj -= dt.timedelta(days=DATE_RANGE)
    parsed_data['from_date'] = date_obj.strftime("%d/%m/%Y")

    env = Environment(loader=FileSystemLoader(
        f'{os.environ.get("LAMBDA_TASK_ROOT")}/templates/'))
    template = env.get_template('email.html')

    return 'Recent Runs', template.render(data=parsed_data)


def send_email(to_address, from_address, title, data):
    """ Use SES to send email."""

    if os.environ.get('DISABLE_EMAIL'):
        return

    ses = boto3.client('ses')
    response = ses.send_email(
        Destination={'ToAddresses': [to_address]},
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': data,
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': title,
            },
        },
        Source=from_address)
    return response


def lambda_handler(event, context):
    """ ."""

    access_token = get_access_token()
    data = scrape_api(access_token)

    if data:
        title, body = generate_html(data)
        send_email(os.environ.get('TARGET_EMAIL'),
                   os.environ.get('SEND_EMAIL'), title, body)

    return {
        'statusCode': 200,
        'body': 'Completed'
    }
