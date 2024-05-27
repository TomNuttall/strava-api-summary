import os
from Controller import Controller
from modules.EmailTemplate import EmailTemplate
from modules.Mailer import Mailer
from modules.StravaAuth import StravaAuth
from modules.StravaAPI import StravaAPI
from modules.Transformer import Transformer

emailTemplate = EmailTemplate(f'./templates/')
mailer = Mailer(os.environ.get('TARGET_EMAIL'))
stravaAPI = StravaAPI(StravaAuth())
transformer = Transformer()
controller = Controller(stravaAPI, transformer, mailer, emailTemplate)


def lambda_handler(event, context):
    """ ."""

    controller.handler(os.environ.get('SEND_EMAIL'))

    return {
        'statusCode': 200,
        'body': 'Completed'
    }


if __name__ == "__main__":
    lambda_handler({}, {})
