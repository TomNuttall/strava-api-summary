import json
import time
import boto3
import requests
import os
import datetime as dt
from jinja2 import Environment, FileSystemLoader

ses = boto3.client('ses', region_name='eu-west-2')
ssm = boto3.client('ssm', region_name='eu-west-2')


def get_access_token():
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

        auth_url = 'https://www.strava.com/oauth/token'
        res = requests.post(auth_url, params)
        res_data = res.json()

        api_token['expires_at'] = res_data['expires_at']
        api_token['access_token'] = res_data['access_token']
        api_token['refresh_token'] = res_data['refresh_token']

        ssm.put_parameter(Name='stravaapitoken',
                          Value=json.dumps(api_token), Overwrite=True)

    return api_token['access_token'], app['athlete']['id']


def send_email(to_address, from_address, title, data):
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


def generate_html(data):
    env = Environment(loader=FileSystemLoader(
        f'{os.environ.get("LAMBDA_TASK_ROOT")}/templates/'))
    template = env.get_template('email.html')

    return template.render(data=data)


def lambda_handler(event, context):
    access_token, athlete = get_access_token()

    date_obj = dt.datetime.now()
    date_obj -= dt.timedelta(days=7)
    url = f'https://www.strava.com/api/v3/athlete/activities?after={dt.datetime.timestamp(date_obj)}'
    res = requests.get(url, params={'access_token': access_token})

    if res.status_code == 200:
        body = generate_html(res.json())

        if not os.environ.get('DISABLE_EMAIL'):
            send_email(os.environ.get('TARGET_EMAIL'), os.environ.get(
                'SEND_EMAIL'), 'Recent Runs', body)

    return {
        'statusCode': 200,
        'body': 'Success'
    }
