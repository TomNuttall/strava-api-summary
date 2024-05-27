import boto3
import json
import time
import logging
from moto import mock_aws

from Controller import Controller
from modules.EmailTemplate import EmailTemplate
from modules.Mailer import Mailer
from modules.StravaAuth import StravaAuth, AUTH_URL, SAVED_APP_TOKEN, SAVED_AUTH_TOKEN
from modules.StravaAPI import StravaAPI, ACTIVITIES_URL
from modules.Transformer import Transformer


@mock_aws
def test_handler(requests_mock):
    """ Test full path."""

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

    from_email = 'from@test.com'
    ses = boto3.client('ses', region_name='eu-west-2')
    ses.verify_email_identity(EmailAddress=from_email)

    requests_mock.post(AUTH_URL,
                       json={'expires_at': time.time(), 'access_token': "abc123",
                             'refresh_token': 'xyz'},
                       status_code=200)

    response = [{"id": 1, "name": "Morning Run", "sport_type": "Run", "distance": 1000.0,
                 "elapsed_time": 60, "average_heartrate": 1.0, "average_speed": 1.0, "start_date_local": "2024-01-01T08:00:00Z"},
                {"id": 2, "name": "Morning Run", "sport_type": "Run", "distance": 1000.0,
                 "elapsed_time": 60, "average_heartrate": 1.0, "average_speed": 1.0, "start_date_local": "2024-01-02T08:00:00Z"}]

    requests_mock.get(ACTIVITIES_URL,
                      json=response,
                      status_code=200)

    emailTemplate = EmailTemplate('./templates/')
    mailer = Mailer(from_email)
    stravaAPI = StravaAPI(StravaAuth())
    transformer = Transformer()

    controller = Controller(stravaAPI, transformer, mailer, emailTemplate)

    # Act
    res = controller.handler('to@test.com')

    # Assert
    assert res == 200
