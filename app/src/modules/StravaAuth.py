import boto3
import json
import time
import requests
from dataclasses import dataclass, asdict

AUTH_URL = 'https://www.strava.com/oauth/token'

SAVED_APP_TOKEN = 'stravaapiapp'
SAVED_AUTH_TOKEN = 'stravaapitoken'


@dataclass
class AuthRequest:
    client_id: int = 0
    client_secret: str = ''
    grant_type: str = ''
    code: str = None
    refresh_token: str = None


@dataclass
class AuthResponse:
    expires_at: int = 0
    refresh_token: str = ''
    access_token: str = ''


class StravaAuth:
    def __init__(self):
        """ Setup saved parameters."""

        self.ssm = boto3.client('ssm', region_name='eu-west-2')

        app_param = self.ssm.get_parameter(
            Name=SAVED_APP_TOKEN, WithDecryption=True)
        self.app = json.loads(app_param['Parameter']['Value'])

        token_param = self.ssm.get_parameter(
            Name=SAVED_AUTH_TOKEN, WithDecryption=True)
        self.api_token = json.loads(token_param['Parameter']['Value'])

    def getAuthToken(self) -> str:
        """ Wrap auth token refresh login."""

        expires_at = self.api_token.get('expires_at')
        params = AuthRequest()

        if not expires_at:
            params.grant_type = 'authorization_code'
            params.code = self.app['code']
        elif time.time() > expires_at:
            params.grant_type = 'refresh_token'
            params.refresh_token = self.api_token.get('refresh_token')

        if params.grant_type:
            params.client_id = self.app['client_code']
            params.client_secret = self.app['client_secret']

            status_code, res_data = self.__requestAuthToken(params)
            if status_code == 200:
                self.api_token['expires_at'] = res_data.expires_at
                self.api_token['access_token'] = res_data.access_token
                self.api_token['refresh_token'] = res_data.refresh_token

                self.ssm.put_parameter(Name=SAVED_AUTH_TOKEN,
                                       Value=json.dumps(self.api_token), Overwrite=True)

        return self.api_token.get('access_token')

    def __requestAuthToken(self, req: AuthRequest) -> tuple[int, AuthResponse]:
        """ API auth request."""

        params = dict(filter(lambda x: x[1] != None, asdict(req).items()))
        res = requests.post(AUTH_URL, params)

        return res.status_code, self.__parse_response(res.json())

    def __parse_response(self, raw_data: dict) -> AuthResponse:
        """ ."""

        data = dict(
            filter(lambda x: AuthResponse.__annotations__.get(x[0]), raw_data.items()))
        return AuthResponse(**data)
