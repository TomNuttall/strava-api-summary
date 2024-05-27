import datetime as dt
from strava.StravaAPI import StravaAPI, ACTIVITIES_URL
from strava.StravaAuth import StravaAuth


class MockAuth:
    def getAuthToken(self) -> str:
        return "mock_token"


def test_get_activities(requests_mock, mocker):
    """ Should successfuly get activities."""

    # Arrange
    mocker.patch.object(StravaAuth, "__new__",
                        return_value=MockAuth())
    mocker.patch.object(StravaAuth,
                        "getAuthToken", return_value="abc123")

    response = [{"id": 1, "name": "Morning Run", "sport_type": "Run", "distance": 1000.0,
                 "elapsed_time": 60, "average_heartrate": 1.0, "average_speed": 1.0, "start_date_local": "2024-01-01T08:00:00Z"},
                {"id": 2, "name": "Morning Run", "sport_type": "Run", "distance": 1000.0,
                 "elapsed_time": 60, "average_heartrate": 1.0, "average_speed": 1.0, "start_date_local": "2024-01-02T08:00:00Z"}]

    requests_mock.get(ACTIVITIES_URL,
                      json=response,
                      status_code=200)

    stravaAPI = StravaAPI(StravaAuth())

    # Act
    status_code, res = stravaAPI.getActivities(dt.datetime.now())

    # Assert
    assert status_code == 200
    assert len(res) == 2


def test_get_activities_fail(requests_mock, mocker):
    """ Should return no activities."""

    # Arrange
    mocker.patch.object(StravaAuth, "__new__",
                        return_value=MockAuth())
    mocker.patch.object(StravaAuth,
                        "getAuthToken", return_value="abc123")

    response = []
    requests_mock.get(ACTIVITIES_URL,
                      json=response,
                      status_code=500)

    stravaAPI = StravaAPI(StravaAuth())

    # Act
    status_code, res = stravaAPI.getActivities(dt.datetime.now())

    # Assert
    assert status_code == 500
    assert len(res) == 0
