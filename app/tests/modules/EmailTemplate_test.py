from bs4 import BeautifulSoup
from src.modules.EmailTemplate import EmailTemplate, EmailSummary
from src.modules.Transformer import Activity, Summary


emailTemplate = EmailTemplate('../src/modules')


def test_generate_html():
    """ Should generate email html from activity list."""

    # Arrange
    activities: list[Activity] = []
    activities.append(Activity(id=1, name='Morning Run', type='Run', distance=1000.0,
                               duration=120.0, avg_heartrate=100, avg_speed=1,
                               date='Monday', date_time='12:00'))

    data = EmailSummary(date='1st Jan - 7th Jan',
                        summary=Summary(
                            count=1, total_distance=10.0, total_time=1.0),
                        activities=activities)

    # Act
    body = emailTemplate.generateHTML(data)

    # Assert
    res = bool(BeautifulSoup(body, "html.parser").find())
    assert res == True
