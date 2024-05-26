import boto3
import json
import time
from moto import mock_aws
from src.modules.StravaAuth import StravaAuth, AUTH_URL, SAVED_APP_TOKEN, SAVED_AUTH_TOKEN


@mock_aws
def test_request_token(requests_mock):
    """ Should request a new token when no token saved."""

    # Arrange
    ssm = boto3.client('ssm', region_name='eu-west-2')
    ssm.put_parameter(
        Name=SAVED_APP_TOKEN,
        Value=json.dumps(
            {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
        Type="SecureString"
    )
    ssm.put_parameter(
        Name=SAVED_AUTH_TOKEN,
        Value=json.dumps({}),
        Type="SecureString"
    )

    access_token = "abc123"
    requests_mock.post(AUTH_URL,
                       json={'expires_at': time.time(), 'access_token': access_token,
                             'refresh_token': 'xyz'},
                       status_code=200)

    stravaAuth = StravaAuth()

    # Act
    res = stravaAuth.getAuthToken()

    # Assert
    assert res == access_token


@mock_aws
def test_saved_token():
    """ Should return saved access token when expiry date is valid."""

    # Arrange
    access_token = "abc123"

    ssm = boto3.client('ssm', region_name='eu-west-2')
    ssm.put_parameter(
        Name=SAVED_APP_TOKEN,
        Value=json.dumps(
            {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
        Type="SecureString"
    )
    ssm.put_parameter(
        Name=SAVED_AUTH_TOKEN,
        Value=json.dumps({'expires_at': time.time() + 10000,
                          'access_token': access_token}),
        Type="SecureString"
    )

    stravaAuth = StravaAuth()

    # Act
    res = stravaAuth.getAuthToken()

    # Assert
    assert res == access_token


@mock_aws
def test_refresh_token(requests_mock):
    """ Should request a new token with saved refresh token when token has expired."""

    # Arrange
    access_token = "abc123"

    ssm = boto3.client('ssm', region_name='eu-west-2')
    ssm.put_parameter(
        Name=SAVED_APP_TOKEN,
        Value=json.dumps(
            {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
        Type="SecureString"
    )
    ssm.put_parameter(
        Name=SAVED_AUTH_TOKEN,
        Value=json.dumps({'expires_at': time.time() - 10000,
                          'access_token': access_token,
                          'refresh_token': access_token}),
        Type="SecureString"
    )

    access_token = "abc456"
    requests_mock.post(AUTH_URL,
                       json={'expires_at': time.time(), 'access_token': access_token,
                             'refresh_token': 'xyz'},
                       status_code=200)

    stravaAuth = StravaAuth()

    # Act
    res = stravaAuth.getAuthToken()

    # Assert
    assert res == access_token
