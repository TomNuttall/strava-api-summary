import os
from Controller import Controller
from modules.EmailTemplate import EmailTemplate
from modules.Mailer import Mailer
from modules.Transformer import Transformer, Activity, Summary, EmailTemplateData
from strava.StravaAuth import StravaAuth
from strava.StravaAPI import StravaAPI

emailTemplate = EmailTemplate(
    f'./templates/', os.environ.get('ASSET_URL', 'assets/email/'))
mailer = Mailer(os.environ.get('SEND_EMAIL'))
stravaAPI = StravaAPI(StravaAuth())
transformer = Transformer()
controller = Controller(stravaAPI, transformer, mailer, emailTemplate)


def lambda_handler(event, context):
    """ ."""

    controller.handler(os.environ.get('ATHLETE_ID'),
                       os.environ.get('TARGET_EMAIL'))

    return {
        'statusCode': 200,
        'body': 'Completed'
    }
