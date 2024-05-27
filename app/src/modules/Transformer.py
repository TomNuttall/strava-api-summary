import datetime as dt
from functools import reduce
from dataclasses import dataclass, field
from strava.StravaAPI import DetailedActivity


@dataclass
class Activity:
    id: int = 0
    name: str = ''
    type: str = ''
    distance: float = 0.0
    duration: float = 0.0
    avg_heartrate: int = 0
    date: str = ''
    date_time: str = ''


@dataclass
class Summary:
    count: int = 0
    total_time: float = 0.0
    total_distance: float = 0.0


@dataclass
class EmailTemplateData:
    athlete_id: int = 0
    date: str = ''
    activities: list[Activity] = field(default_factory=list)
    summary: Summary = field(default_factory=Summary)


class Transformer:

    def transformActivities(self, data: list[DetailedActivity], athlete_id: int, date: str) -> EmailTemplateData:
        """ Transfrom DetailedActivity list."""

        res = EmailTemplateData()

        res.athlete_id = athlete_id
        res.date = date
        res.activities = list(map(self.__transform_activity, data))
        res.summary = reduce(self.__reduce_summary, res.activities, Summary())

        return res

    def __transform_activity(self, activity: DetailedActivity) -> Activity:
        """ Transform activity to pull out relevant info."""

        res = Activity()
        res.id = activity.id
        res.name = activity.name
        res.type = activity.sport_type
        res.distance = round(activity.distance / 1000, 2)
        res.duration = round(activity.elapsed_time / 60, 2)
        res.avg_heartrate = activity.average_heartrate

        date_obj = dt.datetime.strptime(
            activity.start_date_local, "%Y-%m-%dT%H:%M:%SZ")
        res.date = date_obj.strftime("%A")
        res.date_time = date_obj.strftime("%H:%M")

        return res

    def __reduce_summary(self, acc: Summary, activity: Activity) -> Summary:
        """ Reduce activity to summary."""

        acc.count += 1
        acc.total_time += activity.duration
        acc.total_distance += activity.distance
        return acc
