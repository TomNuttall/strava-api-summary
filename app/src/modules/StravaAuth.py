import boto3
import json
import time
import requests
from dataclasses import dataclass

AUTH_URL = 'https://www.strava.com/oauth/token'

SAVED_APP_TOKEN = 'stravaapiapp'
SAVED_AUTH_TOKEN = 'stravaapitoken'


@dataclass
class AuthRequest:
    client_id: int
    client_secret: str
    code: str
    grant_type: str
    refresh_token: str


@dataclass
class AuthResponse:
    expires_at: int
    refresh_token: str
    access_token: str


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

        params = AuthRequest(
            self.app['client_code'], self.app['client_secret'], self.app['code'], None, self.api_token.get('refresh_token'))

        if not self.api_token.get('expires_at'):
            params.grant_type = 'authorization_code'
        elif time.time() > self.api_token.get('expires_at'):
            params.grant_type = 'refresh_token'

        if params.grant_type:
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

        params = {'client_id': req.client_id,
                  'client_secret': req.client_secret,
                  'grant_type': req.grant_type}

        if req.grant_type == 'authorization_code':
            params['code'] = req.code
        if req.grant_type == 'refresh_token':
            params['refresh_token'] = req.refresh_token

        res = requests.post(AUTH_URL, params)

        data = res.json()
        return res.status_code, AuthResponse(expires_at=data['expires_at'], refresh_token=data['refresh_token'], access_token=data['access_token'])
