import os
from modules.EmailTemplate import EmailTemplate
from modules.Transformer import Activity, Summary, EmailTemplateData


emailTemplate = EmailTemplate(
    f'./templates/', os.environ.get('ASSET_URL', '../../assets/email/'))


if __name__ == "__main__":

    activities: list[Activity] = []
    activities.append(Activity(id=1, name='Morning Run', type='Ride', distance=0.0,
                               duration=20.0, avg_heartrate=100,
                               date='Monday', date_time='09:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Ride', distance=0.0,
                               duration=20.0, avg_heartrate=100,
                               date='Tuesday', date_time='09:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=5.0,
                               duration=30.0, avg_heartrate=100,
                               date='Wednesday', date_time='18:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=5.0,
                               duration=30.0, avg_heartrate=100,
                               date='Thursday', date_time='09:00'))
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=5.0,
                               duration=30.0, avg_heartrate=100,
                               date='Friday', date_time='09:00'))

    data = EmailTemplateData(athlete_id=1,
                             date='1st Jan - 7th Jan',
                             summary=Summary(
                                 count=5, total_distance=14.0, total_time=108.0),
                             activities=activities)

    body = emailTemplate.generateHTML(data)
    with open('example_email.html', 'w') as file:
        file.write(body)
