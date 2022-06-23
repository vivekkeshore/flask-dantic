# 🅕🅛🅐🅢🅚-🅟🅨🅓🅐🅝🅣🅘🅒-🅢🅔🅡🅘🅐🅛🅘🅩🅔🅡

*Flask-Pydantic* is a Python package that would validate the request params, query args and path args.
Also, the package provides a serializer that serializes the database objects using the pydantic models. 
This comes handy if you are using pydantic models for request and response in Flask.

A single serialize call will take care of validating the returned response as well as serializing it. There are options to include or exclude certain fields or exclude/include fields with null values.

[![PyPI](https://img.shields.io/pypi/v/flask-pydantic-serializer?color=g)](https://pypi.org/project/flask-pydantic-serializer/)
![Codecov](https://img.shields.io/codecov/c/github/vivekkeshore/flask-pydantic-serializer)
[![Python package](https://github.com/vivekkeshore/flask-pydantic-serializer/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/vivekkeshore/flask-pydantic-serializer/actions/workflows/python-package.yml)
![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/vivekkeshore/flask-pydantic-serializer)
[![GitHub license](https://img.shields.io/github/license/vivekkeshore/flask-pydantic-serializer)](https://github.com/vivekkeshore/flask-pydantic-serializer/blob/main/LICENSE)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-pydantic-serializer)

----

### Compatibility


This package is compatible with Python >= 3.6

### Basic Usage


Install with pip:

```bash
    pip install flask-pydantic-serializer
```


```python
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session


    db_engine = create_engine(DB_CONNECT_STRING)  # DB connection string, ex "sqlite:///my_app.db"
    db = Session(db_engine)
```

```python
from flask_dantic import serialize
from typing import Optional
from pydantic import BaseModel


class UserResponseModel(BaseModel):  # Define the pydantic model for serialization.
    username: str
    age: Optional[int] = None
    phone: Optional[str] = None


users = db.query(User).all()  # Multiple records. User is an example db model. Replace User with your db model.    
res = serialize(users, UserResponseModel,
                many=True)  # Pass the db records, pydantic model. Set many as True if there are multiple records.

user = db.query(User).first()  # Single record. User is an example db model. Replace User with your db model.
res = serialize(user, UserResponseModel)  # Pass the db record, pydantic model. Many is set to False by default.
```

Tests
-----

Run tests:

```bash
    pytest
```


License
-------

Flask-Pydantic-Serializer is released under the MIT License. See the bundled [`LICENSE`](https://github.com/vivekkeshore/flask-pydantic-serializer/blob/main/LICENSE) file
for details.
