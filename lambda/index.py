import json
import time
import boto3
import requests

ses = boto3.client('ses', region_name='eu-west-2')
ssm = boto3.client('ssm', region_name='eu-west-2')


def get_access_token():
    token_param = ssm.get_parameter(Name='stravaapitoken', WithDecryption=True)
    api_token = json.loads(token_param['Parameter']['Value'])

    should_refresh = False
    params = {}

    if not api_token.get('expires_at'):
        should_refresh = True
        params['grant_type'] = 'authorization_code'
        params['code'] = api_token['code']
    elif time.time() > api_token['expires_at']:
        should_refresh = True
        params['grant_type'] = 'refresh_token'
        params['refresh_token'] = api_token['refresh_token']

    if should_refresh:
        params['client_id'] = api_token['client_code']
        params['client_secret'] = api_token['client_secret']

        auth_url = 'https://www.strava.com/oauth/token'
        res = requests.post(auth_url, params)
        res_data = res.json()

        api_token['expires_at'] = res_data['expires_at']
        api_token['access_token'] = res_data['access_token']
        api_token['refresh_token'] = res_data['refresh_token']

        ssm.put_parameter(Name='stravaapitoken',
                          Value=json.dumps(api_token), Overwrite=True)

    return api_token['access_token']


def lambda_handler(event, context):
    access_token = get_access_token()

    return {
        'statusCode': 200,
        'body': 'Success'
    }
