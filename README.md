# 🅕🅛🅐🅢🅚-🅓🅐🅝🅣🅘🅒

*Flask-Dantic* is a Python package that would enable users to use Pydantic models for validations and serialization, thus making it easy to link Flask with Pydantic.
It can validate the request params, query args and path args.

Also, the package provides a serializer that serializes the database objects using the pydantic models. 
This comes handy if you are using pydantic models for request and response in Flask.

A single serialize call will take care of validating the returned response as well as serializing it. There are options to include or exclude certain fields or exclude/include fields with null values.

[![PyPI](https://img.shields.io/pypi/v/flask-dantic?color=g)](https://pypi.org/project/flask-dantic/)
![Codecov](https://img.shields.io/codecov/c/github/vivekkeshore/flask-dantic)
[![Python package](https://github.com/vivekkeshore/flask-dantic/actions/workflows/python-package.yml/badge.svg)](https://github.com/vivekkeshore/flask-dantic/actions/workflows/python-package.yml)
![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/vivekkeshore/flask-dantic)
[![GitHub license](https://img.shields.io/github/license/vivekkeshore/flask-dantic)](https://github.com/vivekkeshore/flask-dantic)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flask-dantic)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/vivekkeshore/flask-dantic)
![GitHub repo size](https://img.shields.io/github/repo-size/vivekkeshore/flask-dantic)

----

### Compatibility


This package is compatible with Python >= 3.6

## Installation


Install with pip:

```bash
    pip install flask-dantic
```

## Examples
### Validating body parameters

```python
# Using the Pydantic model for request.
from typing import Optional

from flask import current_app as flask_app, request
from pydantic import BaseModel

from flask_dantic import pydantic_validator


class UserCreateModel(BaseModel):
    username: str
    age: Optional[int] = None
    phone: Optional[str] = None


@flask_app.route("/user/create", methods=["POST"])
@pydantic_validator(body=UserCreateModel)  # Pass the model against body kwarg.
def create_user():
    """
        Request Json to create user that will be validated against UserModel
        {
            "username": "Foo",
            "age": 42,
            "phone": "123-456-7890"
        }
    """
    user_model = request.body_model
    print(user_model.username, user_model.age, user_model.phone)
```

### Change the default validation error status code. Default status code is 422
```python

@flask_app.route("/user/create", methods=["POST"])
# Changing the default validation error status code from default 422 to 400
@pydantic_validator(body=UserCreateModel, validation_error_status_code=400)
def create_user():
    """
        Request Json to create user that will be validated against UserModel
        {
            "username": "Foo",
            "age": 42,
            "phone": "123-456-7890"
        }
    """
    user_model = request.body_model
    print(user_model.username, user_model.age, user_model.phone)
```

### Validating Query args - request.args

```python
# Using the Pydantic model for request.
from typing import Optional

from flask import current_app as flask_app, request
from pydantic import BaseModel

from flask_dantic import pydantic_validator


# Sample url - https://localhost:5000/user/get?username=Foo&age=42
# Here username and foo are pass are query args

class UserQueryModel(BaseModel):
    username: str
    age: Optional[int] = None


@flask_app.route("/user/get", methods=["GET"])
@pydantic_validator(query=UserQueryModel)  # Pass the model against query kwarg
def get_user():
    user_query_model = request.query_model
    print(user_query_model.username, user_query_model.age)
```


### Validating URL Path args

```python
# Using the Pydantic model for request.

from flask import current_app as flask_app, request
from pydantic import BaseModel, Field

from flask_dantic import pydantic_validator

# Sample url - https://localhost:5000/user/get/c55926d3-cbd0-4eea-963b-0bcfc5c40d46
# Here the uuid is the dynamic path param.

UUID_REGEX = "[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"


class UserPathParamModel(BaseModel):
    user_id: str = Field(..., regex=UUID_REGEX, description="ID of the user")


@flask_app.route("/user/get/<string:user_id>", methods=["GET"])
@pydantic_validator(path_params=UserPathParamModel)  # Pass the model against path_params
def get_user(user_id):
    path_param_model = request.path_param_model
    print(path_param_model.user_id)
```


### Serialization using Pydantic module and returning the response.


```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


db_engine = create_engine(DB_CONNECT_STRING)  # DB connection string, ex "sqlite:///my_app.db"
db = Session(db_engine)
```

```python
from http import HTTPStatus
from typing import Optional

from flask import current_app as flask_app, jsonify
from pydantic import BaseModel

from flask_dantic import serialize, pydantic_validator


class UserResponseModel(BaseModel):  # Define the pydantic model for serialization.
    username: str
    age: Optional[int] = None
    phone: Optional[str] = None


@flask_app.route("/user/list", methods=["GET"])
def get_all_users():
    users = get_all_users_from_db()

    # Pass the db records and pydantic model to serialize method. Set many as True if there are multiple records.
    serialized_users = serialize(users, UserResponseModel, many=True)  # Serialize call
    return jsonify(serialized_users), HTTPStatus.OK


@flask_app.route("/user/get/<string:user_id>", methods=["GET"])
@pydantic_validator(path_params=UserPathParamModel)  # Pass the model against path_params
def get_user(user_id):
    user = get_single_user_by_id(user_id)
    
    # Pass the db record and pydantic model to serialize method. Many is set to False by default.
    user = serialize(user, UserResponseModel)  # Serialize call
    return jsonify(user), HTTPStatus.OK
```

### Serialization - Dump directly to json. This is useful when you want to return the response as json without flask jsonify.

```python
from flask_dantic import serialize

# Taking the same example from above. Modifying the serialize call.
@flask_app.route("/user/get/<string:user_id>", methods=["GET"])
@pydantic_validator(path_params=UserPathParamModel)  # Pass the model against path_params
def get_user(user_id):
    user = get_single_user_by_id(user_id)
    
    # Pass the db record and pydantic model to serialize method. Many is set to False by default.
      # Serialize call
    return serialize(user, UserResponseModel, json_dump=True), HTTPStatus.OK
```

Tests
-----

Run tests:

```bash
    pytest
```


License
-------

Flask-Dantic is released under the MIT License. See the bundled [`LICENSE`](https://github.com/vivekkeshore/flask-dantic/blob/main/LICENSE) file
for details.
