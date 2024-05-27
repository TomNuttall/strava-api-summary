import datetime as dt
import modules.Helpers as Helpers
from modules.EmailTemplate import EmailTemplate, EmailSummary
from modules.Mailer import Mailer
from modules.StravaAPI import StravaAPI
from modules.Transformer import Transformer

DATE_RANGE = 7


class Controller:

    def __init__(self, stravaApi: StravaAPI, transformer: Transformer, mailer: Mailer, emailTemplate: EmailTemplate):
        """ ."""

        self.stravaApi = stravaApi
        self.transformer = transformer
        self.mailer = mailer
        self.emailTemplate = emailTemplate

    def handler(self, send_to_email: str):
        """ Get last 7 days of activities from strava api."""

        to_date_obj = dt.datetime.now()
        from_date_obj = to_date_obj - dt.timedelta(days=DATE_RANGE)

        status_code, res_data = self.stravaApi.getActivities(from_date_obj)
        if status_code != 200:
            return

        data = EmailSummary()
        from_date_str = Helpers.date_ordinal(from_date_obj.strftime("%d %b"))
        to_date_str = Helpers.date_ordinal(to_date_obj.strftime("%d %b"))
        data.date = f'{from_date_str} - {to_date_str}'

        data.summary, data.activities = self.transformer.transformActivities(
            res_data)

        body = self.emailTemplate.generateHTML(data)
        res = self.mailer.sendEmail(send_to_email, 'Weekly Report', body)
        return res
