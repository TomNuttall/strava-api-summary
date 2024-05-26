import requests
import datetime as dt
from dataclasses import dataclass
from .StravaAuth import StravaAuth

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

    def __init__(self, *args, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.sport_type = kwargs['sport_type']
        self.distance = kwargs['distance']
        self.elapsed_time = kwargs['elapsed_time']
        self.average_heartrate = kwargs['average_heartrate']
        self.average_speed = kwargs['average_speed']
        self.start_date_local = kwargs['start_date_local']


class StravaAPI:

    def __init__(self, auth: StravaAuth):
        """ Setup Auth."""

        self.auth = auth

    def getActivities(self, from_date_obj: dt.datetime) -> tuple[int, list[DetailedActivity]]:
        """ Get result from / activities endpoint."""

        access_token = self.auth.getAuthToken()
        res = requests.get(f'{ACTIVITIES_URL}?after={dt.datetime.timestamp(from_date_obj)}',
                           params={'access_token': access_token})

        data = list(map(lambda item: DetailedActivity(**item), res.json()))
        return res.status_code, data
