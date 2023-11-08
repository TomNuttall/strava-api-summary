import boto3
import json
import time
import datetime as dt
from bs4 import BeautifulSoup
from moto import mock_ses, mock_ssm
from app.index import get_access_token, scrape_api, generate_html, send_email, AUTH_URL, ACTIVITIES_URL


class TestAccessToken:
    @mock_ssm
    def test_request_token(self, requests_mock):
        """ Should request a new token."""

        # Arrange
        ssm = boto3.client('ssm', 'eu-west-2')
        ssm.put_parameter(
            Name="stravaapiapp",
            Value=json.dumps(
                {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
            Type="SecureString"
        )
        ssm.put_parameter(
            Name="stravaapitoken",
            Value=json.dumps({}),
            Type="SecureString"
        )

        access_token = "abc123"
        requests_mock.post(AUTH_URL,
                           json={'expires_at': time.time(), 'access_token': access_token,
                                 'refresh_token': 'xyz'},
                           status_code=200)

        # Act
        res = get_access_token()

        # Assert
        assert res == access_token

    @mock_ssm
    def test_saved_token(self, requests_mock):
        """ Should return saved access token."""

        # Arrange
        access_token = "abc123"

        ssm = boto3.client('ssm', 'eu-west-2')
        ssm.put_parameter(
            Name="stravaapiapp",
            Value=json.dumps(
                {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
            Type="SecureString"
        )
        ssm.put_parameter(
            Name="stravaapitoken",
            Value=json.dumps({'expires_at': time.time() + 10000,
                             'access_token': access_token}),
            Type="SecureString"
        )

        # Act
        res = get_access_token()

        # Assert
        assert res == access_token

    @mock_ssm
    def test_refresh_token(self, requests_mock):
        """ Should request a new token with saved refresh token."""

        # Arrange
        access_token = "abc123"

        ssm = boto3.client('ssm', 'eu-west-2')
        ssm.put_parameter(
            Name="stravaapiapp",
            Value=json.dumps(
                {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
            Type="SecureString"
        )
        ssm.put_parameter(
            Name="stravaapitoken",
            Value=json.dumps({'expires_at': time.time() - 10000,
                             'access_token': access_token,
                              'refresh_token': access_token}),
            Type="SecureString"
        )

        access_token = "abc123"
        requests_mock.post(AUTH_URL,
                           json={'expires_at': time.time(), 'access_token': access_token,
                                 'refresh_token': 'xyz'},
                           status_code=200)

        # Act
        res = get_access_token()

        # Assert
        assert res == access_token


class TestScrapeApi:
    def test_api_success(self, requests_mock):
        """ Should call api with success."""

        # Arrange
        access_token = "abc123"
        date_string = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        activities = []
        activities.append({'name': 'Run', 'distance': 1000, 'elapsed_time': 60,
                           'start_date_local': date_string})

        requests_mock.get(ACTIVITIES_URL,
                          json=activities,
                          status_code=200)

        # Act
        res = scrape_api(access_token)

        # Assert
        assert res['summary']['count'] == 1

    def test_api_fail(self, requests_mock):
        """ Should call api with error."""

        # Arrange
        access_token = "abc123"
        requests_mock.get(ACTIVITIES_URL,
                          json={},
                          status_code=500)

        # Act
        res = scrape_api(access_token)

        # Assert
        assert res == None


class TestGenerateHTML:
    def test_generate_html(self):
        """ Should generate some html from data."""

        # Arrange
        data = {'title': 'Runs', 'summary': {'count': 0,
                                             'total_distance': 10, 'total_time': 0}, 'activities': []}

        # Act
        title, body = generate_html('app', data)
        res = bool(BeautifulSoup(body, "html.parser").find())

        # Assert
        assert res == True


class TestSendEmail:
    @mock_ses
    def test_send_email(self):
        """ Should successfuly send email."""

        # Arrange
        to_email = 'to@test.com'
        from_email = 'from@test.com'

        ses = boto3.client('ses', 'eu-west-2')
        ses.verify_email_identity(EmailAddress=to_email)
        ses.verify_email_identity(EmailAddress=from_email)

        # Act
        res = send_email(to_email, from_email, 'Title', '<div></div>')

        # Assert
        assert res['ResponseMetadata']['HTTPStatusCode'] == 200
