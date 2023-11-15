import json
import time
import os
from functools import reduce
import datetime as dt
import boto3
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape
import css_inline

AUTH_URL = 'https://www.strava.com/oauth/token'
ACTIVITIES_URL = 'https://www.strava.com/api/v3/athlete/activities'
DATE_RANGE = 7


def get_access_token():
    """ Retrive access token from Parameter store and check if refresh needed."""

    ssm = boto3.client('ssm', region_name='eu-west-2')

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

    return api_token.get('access_token')


def scrape_api(access_token):
    """ Get last 7 days of activities from strava api."""

    data = {}

    date_obj = dt.datetime.now()
    data['to_date'] = date_obj.strftime("%d/%m/%Y")

    date_obj -= dt.timedelta(days=DATE_RANGE)
    data['from_date'] = date_obj.strftime("%d/%m/%Y")

    res = requests.get(f'{ACTIVITIES_URL}?after={dt.datetime.timestamp(date_obj)}', params={
                       'access_token': access_token})

    if res.status_code != 200:
        return

    def transform_activity(activity):
        """ Transform activity to pull out relevant info."""

        res = {}
        res['name'] = activity['name']
        res['type'] = activity['sport_type']
        res['distance'] = round(activity['distance'] / 1000, 2)
        res['duration'] = round(activity['elapsed_time'] / 60, 2)
        res['avg_heartrate'] = activity['average_heartrate']
        res['avg_speed'] = activity['average_speed']

        date_obj = dt.datetime.strptime(
            activity['start_date_local'], "%Y-%m-%dT%H:%M:%SZ")
        res['date'] = date_obj.strftime("%d/%m/%Y")
        res['date_time'] = date_obj.strftime("%H:%M")

        return res

    def reduce_summary(acc, activity):
        """ Reduce activity to summary."""

        acc['count'] += 1
        acc['total_time'] += activity['duration']
        acc['total_distance'] += activity['distance']
        return acc

    data['title'] = 'Recent Runs'
    data['activities'] = list(map(transform_activity, res.json()))
    data['summary'] = reduce(
        reduce_summary, data['activities'], {'count': 0, 'total_time': 0, 'total_distance': 0})

    return data


def generate_html(template_root, data):
    """ Use email template to generate html from data."""

    dir = os.getcwd()

    env = Environment(loader=FileSystemLoader(
        f'{template_root}/templates/'), autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template('email.html')

    body = css_inline.inline(template.render(data=data))
    return data['title'], body


def send_email(to_address, from_address, title, body_data):
    """ Use SES to send email."""

    ses = boto3.client('ses', region_name='eu-west-2')

    res = ses.send_email(
        Destination={'ToAddresses': [to_address]},
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': body_data,
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': title,
            },
        },
        Source=from_address)

    return res


def lambda_handler(event, context):
    """ ."""

    access_token = get_access_token()
    if access_token:
        data = scrape_api(access_token)

        if data:
            title, body = generate_html(
                os.environ.get("LAMBDA_TASK_ROOT"), data)

            send_email(os.environ.get('TARGET_EMAIL'),
                       os.environ.get('SEND_EMAIL'), title, body)

    return {
        'statusCode': 200,
        'body': 'Completed'
    }
