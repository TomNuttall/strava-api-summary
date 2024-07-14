# Lambda

## Overview

- Use SSM to retrive auth token and handle refresh token
- Get stats from Strava Api
- Generate html with inline styling for stats with Jinja2 template
- Use SES to send a summary email

### API Example

[Activity Response](https://developers.strava.com/docs/reference/#api-models-DetailedActivity)

## Install

VirtualEnv

```bash
python3 -m venv env
source env/bin/activate
```

Install packages

```bash
pip install -r ./requirements-dev.txt
```

## Run

```bash
python exanple_email.py
```

### Tests

```bash
pytest
```

- Uses [moto](http://docs.getmoto.org/en/latest/) for mocking aws services.
- Uses [requests-mocks](https://requests-mock.readthedocs.io) for mocking api requests.
- Uses [pytest](https://docs.pytest.org/en/8.2.x/) for unit tests.
- Uses [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/) for mocking.
