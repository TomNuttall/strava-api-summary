import datetime as dt
from functools import reduce
from dataclasses import dataclass
from modules.StravaAPI import DetailedActivity


@dataclass
class Activity:
    id: int = 0
    name: str = ''
    type: str = ''
    distance: float = 0.0
    duration: float = 0.0
    avg_heartrate: int = 0
    avg_speed: int = 0
    date: str = ''
    date_time: str = ''


@dataclass
class Summary:
    count: int = 0
    total_time: float = 0.0
    total_distance: float = 0.0


class Transformer:

    def transformActivities(self, data: list[DetailedActivity]) -> tuple[list[Activity], Summary]:
        """ Transfrom DetailedActivity list."""

        activities = list(map(self.__transform_activity, data))
        summary = reduce(self.__reduce_summary,
                         activities, Summary())

        return summary, activities

    def __transform_activity(self, activity: DetailedActivity) -> Activity:
        """ Transform activity to pull out relevant info."""

        res = Activity()
        res.id = activity.id
        res.name = activity.name
        res.type = activity.sport_type
        res.distance = round(activity.distance / 1000, 2)
        res.duration = round(activity.elapsed_time / 60, 2)
        res.avg_heartrate = activity.average_heartrate
        res.avg_speed = activity.average_speed

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
