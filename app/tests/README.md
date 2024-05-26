# Tests

## Overview

- Uses [moto](http://docs.getmoto.org/en/latest/) for mocking aws services.
- Uses [requests-mocks](https://requests-mock.readthedocs.io) for mocking api requests.
- Uses [pytest](https://docs.pytest.org/en/8.2.x/) for unit tests.
- Uses [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/) for mocking.

## Install

VirtualEnv

```bash
python3 -m venv env
source env/bin/activate
```

Install packages

```bash
pip install -r ./requirements.txt
```

## Run

```bash
python index.py
```

## Run

```
pytest
```
