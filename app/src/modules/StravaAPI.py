import requests
import datetime as dt
from modules.StravaAuth import StravaAuth
from dataclasses import dataclass


ACTIVITIES_URL = 'https://www.strava.com/api/v3/athlete/activities'


@dataclass
class DetailedActivity:
    id: int
    name: str
    sport_type: str
    distance: float
    elapsed_time: int
    average_heartrate: float
    average_speed: float
    start_date_local: str


class StravaAPI:

    def __init__(self, auth: StravaAuth):
        """ Setup Auth."""

        self.auth = auth

    def getActivities(self, from_date_obj: dt.datetime) -> tuple[int, list[DetailedActivity]]:
        """ Get result from / activities endpoint."""

        access_token = self.auth.getAuthToken()
        res = requests.get(f'{ACTIVITIES_URL}?after={dt.datetime.timestamp(from_date_obj)}',
                           params={'access_token': access_token})

        data = list(map(self.__parse_response, res.json()))
        return res.status_code, data

    def __parse_response(self, raw_data: dict) -> DetailedActivity:
        """ ."""

        data = dict(
            filter(lambda x: DetailedActivity.__annotations__.get(x[0]), raw_data.items()))
        return DetailedActivity(**data)
