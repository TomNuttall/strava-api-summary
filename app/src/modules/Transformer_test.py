from modules.StravaAPI import DetailedActivity
from modules.Transformer import Transformer, Summary, Activity

transformer = Transformer()


def test_transformActivites():
    """ Should transform DetailedActivity list."""

    # Arrange
    data: list[DetailedActivity] = []
    data.append(DetailedActivity(id=1, name="Morning Run", sport_type="Run", distance=1000.0,
                                 elapsed_time=3600, average_heartrate=100.0, start_date_local="2024-01-01T09:00:00Z"))
    data.append(DetailedActivity(id=2, name="Morning Run", sport_type="Run", distance=1000.0,
                                 elapsed_time=3600, average_heartrate=100.0, start_date_local="2024-01-02T09:00:00Z"))

    # Act
    summary, activities = transformer.transformActivities(data)

    # Assert
    assert summary == Summary(
        count=2, total_distance=2.0, total_time=120.0)
    assert activities[0] == Activity(
        1, "Morning Run", "Run", 1.0, 60.0, 100.0, "Monday", "09:00")
