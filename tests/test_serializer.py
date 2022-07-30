import os
from typing import Optional
from unittest import mock

import pytest
from pydantic import BaseModel
from pydantic.fields import ModelField
from sqlalchemy.orm import Session
import json

from flask_dantic.pydantic_serializer import get_response_field, serialize
from tests.create_test_db import get_db_engine, User

USERNAMES = ["user1", "user2", "user3"]
AGE = 42


class FooModel(BaseModel):
    foo: str = "foo"
    bar: str = "bar"
    bla: str = "bla"


class UserModel(BaseModel):
    username: str
    age: Optional[int] = None
    phone: Optional[str] = None


class InvalidUserModel(BaseModel):
    username: str
    age: int
    phone: str  # Phone is mentioned str, whereas the actual value would be None


def test_get_response_field():
    response_field = get_response_field("foo_model", FooModel)

    assert response_field.model_config.orm_mode is True
    assert isinstance(response_field, ModelField)
    assert response_field.type_ is FooModel

    with pytest.raises(RuntimeError):
        get_response_field("foo_model", [1, 2, 3])


@mock.patch("flask_dantic.pydantic_serializer.serializer.ModelField")
def test_get_response_field_exception(mocked_model_field):
    exception = RuntimeError("Dummy Exception")
    mocked_model_field.side_effect = exception

    with pytest.raises(RuntimeError) as err:
        get_response_field("foo_model", FooModel)
        assert err.msg == "Dummy Exception"


@pytest.fixture()
def db():
    engine = get_db_engine()
    session = Session(engine)
    for username in USERNAMES:
        user = User(username=username, age=AGE)
        session.add(user)

    yield session
    session.close()
    os.unlink("test.db")


def test_serialize_encoded_objects(db):
    users = db.query(User).all()
    single_user = users[0]

    # Returns encoded serializable object.
    res = serialize(single_user, UserModel, json_dump=False)
    assert res == {"username": USERNAMES[0], "age": AGE, "phone": None}

    res = serialize(users, UserModel, many=True, json_dump=False)
    assert res == [{"username": username, "age": AGE, "phone": None} for username in USERNAMES]

    res = serialize(users, UserModel, many=True, include=["username"], json_dump=False)
    assert res == [{"username": username} for username in USERNAMES]

    res = serialize(users, UserModel, many=True, exclude=["age"], json_dump=False)
    assert res == [{"username": username, "phone": None} for username in USERNAMES]

    res = serialize(users, UserModel, many=True, exclude_none=True, json_dump=False)
    assert res == [{"username": username, "age": AGE} for username in USERNAMES]


def test_serialize_json_dumped_objects(db):
    users = db.query(User).all()
    single_user = users[0]

    # Returns dumped object.
    res = serialize(single_user, UserModel, json_dump=True)
    assert res == json.dumps({"username": USERNAMES[0], "age": AGE, "phone": None})

    res = serialize(users, UserModel, many=True, json_dump=True)
    assert res == json.dumps([{"username": username, "age": AGE, "phone": None} for username in USERNAMES])

    res = serialize(users, UserModel, many=True, include=["username"], json_dump=True)
    assert res == json.dumps([{"username": username} for username in USERNAMES])

    res = serialize(users, UserModel, many=True, exclude=["age"], json_dump=True)
    assert res == json.dumps([{"username": username, "phone": None} for username in USERNAMES])

    res = serialize(users, UserModel, many=True, exclude_none=True, json_dump=True)
    assert res == json.dumps([{"username": username, "age": AGE} for username in USERNAMES])


def test_serialize_negative(db):
    user = db.query(User).order_by(User.username).first()

    with pytest.raises(TypeError):
        serialize(user, InvalidUserModel, include=["username"])
