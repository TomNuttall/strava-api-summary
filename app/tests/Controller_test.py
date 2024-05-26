# import boto3
# import json
# import time
# import logging
# from moto import mock_aws

# from src.modules.EmailTemplate import EmailTemplate
# from src.modules.Mailer import Mailer
# from src.modules.StravaAuth import StravaAuth, AUTH_URL, SAVED_APP_TOKEN, SAVED_AUTH_TOKEN
# from src.modules.StravaAPI import StravaAPI, ACTIVITIES_URL
# from src.modules.Transformer import Transformer


# @mock_aws
# def test_controller(requests_mock, mocker):
#     """ Test full path."""

#     # Arrange
#     ssm = boto3.client('ssm', region_name='eu-west-2')
#     ssm.put_parameter(
#         Name=SAVED_APP_TOKEN,
#         Value=json.dumps(
#             {'code': '1', 'client_code': '124', 'client_secret': 'xyz'}),
#         Type="SecureString"
#     )
#     ssm.put_parameter(
#         Name=SAVED_AUTH_TOKEN,
#         Value=json.dumps({}),
#         Type="SecureString"
#     )

#     from_email = 'from@test.com'
#     ses = boto3.client('ses', region_name='eu-west-2')
#     ses.verify_email_identity(EmailAddress=from_email)

#     requests_mock.post(AUTH_URL,
#                        json={'expires_at': time.time(), 'access_token': "abc123",
#                              'refresh_token': 'xyz'},
#                        status_code=200)

#     response = [{"id": 1, "name": "Morning Run", "sport_type": "Run", "distance": 1000.0,
#                  "elapsed_time": 60, "average_heartrate": 1.0, "average_speed": 1.0, "start_date_local": ""},
#                 {"id": 2, "name": "Morning Run", "sport_type": "Run", "distance": 1000.0,
#                  "elapsed_time": 60, "average_heartrate": 1.0, "average_speed": 1.0, "start_date_local": ""}]

#     requests_mock.get(ACTIVITIES_URL,
#                       json=response,
#                       status_code=200)

#     emailTemplate = EmailTemplate('../src/modules')
#     mailer = Mailer(from_email)
#     stravaAPI = StravaAPI(StravaAuth())
#     transformer = Transformer()

#     # mocker.patch("modules.Helpers")
#     # mocker.patch("modules.EmailTemplate.EmailTemplate")
#     # mocker.patch("modules.Mailer.Mailer")
#     # mocker.patch("modules.StravaAPI.StravaAPI")
#     # mocker.patch("modules.Transformer.Transformer")

#     from src.Controller import Controller
#     controller = Controller(stravaAPI, transformer, mailer, emailTemplate)

#     # Act
#     res = controller.scrapeAPI('to@test.com')
#     logging.warning(res)

#     # Assert
