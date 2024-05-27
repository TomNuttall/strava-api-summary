import boto3
import json
import time
import requests
from strava.StravaAuth import StravaAuth, SAVED_APP_TOKEN, SAVED_AUTH_TOKEN, AUTH_URL
from moto import mock_aws


@mock_aws
def test_request_token(requests_mock, mocker):
    """ Should request a new token when no token saved."""

    # Arrange
    ssm = boto3.client('ssm', region_name='eu-west-2')

    app = {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}
    ssm.put_parameter(Name=SAVED_APP_TOKEN,
                      Value=json.dumps(app), Type="SecureString")

    ssm.put_parameter(Name=SAVED_AUTH_TOKEN,
                      Value=json.dumps({}), Type="SecureString")

    access_token = "abc123"
    json_response = {'expires_at': time.time(), 'access_token': access_token,
                     'refresh_token': 'xyz'}
    requests_mock.post(AUTH_URL,
                       json=json_response, status_code=200)
    spy = mocker.spy(requests, "post")

    stravaAuth = StravaAuth()

    # Act
    res = stravaAuth.getAuthToken()

    # Assert
    assert res == access_token
    spy.assert_called_once_with(AUTH_URL, {
                                'client_id': app['client_code'],
                                'client_secret': app['client_secret'],
                                'code': app['code'],
                                'grant_type': 'authorization_code'})


@mock_aws
def test_saved_token():
    """ Should return saved access token when expiry date is valid."""

    # Arrange
    ssm = boto3.client('ssm', region_name='eu-west-2')

    app = {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}
    ssm.put_parameter(Name=SAVED_APP_TOKEN,
                      Value=json.dumps(app), Type="SecureString")

    access_token = "abc123"
    auth = {'expires_at': time.time() + 10000, 'access_token': access_token}
    ssm.put_parameter(Name=SAVED_AUTH_TOKEN,
                      Value=json.dumps(auth), Type="SecureString")

    stravaAuth = StravaAuth()

    # Act
    res = stravaAuth.getAuthToken()

    # Assert
    assert res == access_token


@mock_aws
def test_refresh_token(requests_mock, mocker):
    """ Should request a new token with saved refresh token when token has expired."""

    # Arrange
    ssm = boto3.client('ssm', region_name='eu-west-2')

    app = {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}
    ssm.put_parameter(Name=SAVED_APP_TOKEN,
                      Value=json.dumps(app), Type="SecureString")

    auth = {'expires_at': time.time() - 10000, 'access_token': "abc123",
            'refresh_token': "123456"}
    ssm.put_parameter(Name=SAVED_AUTH_TOKEN,
                      Value=json.dumps(auth), Type="SecureString")

    new_access_token = "abc456"
    json_response = {'expires_at': time.time(),
                     'access_token': new_access_token, 'refresh_token': 'xyz'}
    requests_mock.post(AUTH_URL,
                       json=json_response,
                       status_code=200)
    spy = mocker.spy(requests, "post")

    stravaAuth = StravaAuth()

    # Act
    res = stravaAuth.getAuthToken()

    # Assert
    assert res == new_access_token
    spy.assert_called_once_with(AUTH_URL, {
                                'client_id': app['client_code'],
                                'client_secret': app['client_secret'],
                                'refresh_token': auth['refresh_token'],
                                'grant_type': 'refresh_token'})
