import os
from Controller import Controller
from modules.EmailTemplate import EmailTemplate
from modules.Mailer import Mailer
from modules.Transformer import Transformer, Activity, Summary, EmailTemplateData
from strava.StravaAuth import StravaAuth
from strava.StravaAPI import StravaAPI

emailTemplate = EmailTemplate(f'./templates/')
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


if __name__ == "__main__":
    emailTemplate = EmailTemplate("./templates")

    activities: list[Activity] = []
    activities.append(Activity(id=1, name='Morning Run', type='Ride', distance=0.0,
                               duration=20.0, avg_heartrate=100,
                               date='Monday', date_time='09:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Ride', distance=0.0,
                               duration=25.0, avg_heartrate=100,
                               date='Tuesday', date_time='12:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=4.0,
                               duration=21.0, avg_heartrate=100,
                               date='Wednesday', date_time='12:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=6.0,
                               duration=22.0, avg_heartrate=100,
                               date='Thursday', date_time='12:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=4.0,
                               duration=20.0, avg_heartrate=100,
                               date='Friday', date_time='12:00'))

    data = EmailTemplateData(athlete_id=1,
                             date='1st Jan - 7th Jan',
                             summary=Summary(
                                 count=1, total_distance=10.0, total_time=136.2),
                             activities=activities)

    body = emailTemplate.generateHTML(data)
    with open('../example_email.html', 'w') as file:
        file.write(body)
