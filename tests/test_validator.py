from http import HTTPStatus
from typing import Optional

from flask import make_response
from pydantic import BaseModel, Extra

from flask_dantic.request_validator.validator import pydantic_validator


class MockRequest:
    def __init__(self, args={}, body={}):
        self.args = args
        self.json = body
        self.environ = {"wsgi.errors": None}
        self.blueprints = []
        self.blueprint = None
        self.url = ""


def application_api(request, **kwargs):
    return make_response(
        {
            "query_params": request.args,
            "body_params": request.json,
            "path_params": kwargs,
        }, HTTPStatus.OK
    )


class FooModel(BaseModel):
    foo: str
    bar: Optional[str] = None
    bla: Optional[str] = None


class UserModel(BaseModel):
    username: str
    age: Optional[int] = None
    phone: Optional[str] = None


class UserModelStrict(BaseModel, extra=Extra.forbid):
    username: str
    age: Optional[int] = None
    phone: Optional[str] = None


def test_validate_query_params(app):
    with app.test_request_context() as test_request_ctx:
        args = {"foo": "bar", "bar": "foo"}
        test_request_ctx.request = MockRequest(args=args)

        res = pydantic_validator(query=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("query_params") == args
        assert res.status_code == HTTPStatus.OK

        #  Validated Pydantic model becomes the query_model attribute of request.
        assert isinstance(test_request_ctx.request.query_model, FooModel)

        # Values got set in the Pydantic model.
        assert test_request_ctx.request.query_model.bar == "foo"

        # Actual request.args is unchanged.
        assert test_request_ctx.request.args == args


def test_validate_query_params_invalid_model(app):
    with app.test_request_context() as test_request_ctx:
        args = {"foo": "bar", "bar": "foo"}
        test_request_ctx.request = MockRequest(args=args)

        # Invalid model UserModel for above given args.
        res = pydantic_validator(query=UserModel)(application_api)(test_request_ctx.request)

        # Expected validation error.
        expected = [{'loc': ['username'], 'msg': 'field required', 'type': 'value_error.missing'}]

        assert res.json.get("validation_error")
        assert res.json.get("validation_error").get("query_params") == expected
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_query_params_invalid_params(app):
    with app.test_request_context() as test_request_ctx:
        args = ["foo", "args"]  # Invalid type for request.args
        test_request_ctx.request = MockRequest(args=args)

        res = pydantic_validator(query=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_query_params_empty_params(app):
    with app.test_request_context() as test_request_ctx:
        args = {}  # Empty args
        test_request_ctx.request = MockRequest(args=args)

        res = pydantic_validator(query=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_query_params_missing_required_field(app):
    with app.test_request_context() as test_request_ctx:
        args = {"bar": "foo"}  # "foo" is required in FooModel
        test_request_ctx.request = MockRequest(args=args)

        res = pydantic_validator(query=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_query_params_strict_model(app):
    with app.test_request_context() as test_request_ctx:
        args = {"username": "foo", "age": 42, "phone": 123}
        test_request_ctx.request = MockRequest(args=args)

        res = pydantic_validator(query=UserModelStrict)(application_api)(test_request_ctx.request)
        assert res.json.get("query_params") == args
        assert res.status_code == HTTPStatus.OK
        assert isinstance(test_request_ctx.request.query_model, UserModelStrict)
        assert test_request_ctx.request.query_model.age == 42
        assert test_request_ctx.request.args == args


def test_validate_query_params_strict_model_extra_args(app):
    with app.test_request_context() as test_request_ctx:
        args = {"username": "foo", "age": 42, "phone": 123, "foo": "bar"}  # "foo" is extra attr.
        test_request_ctx.request = MockRequest(args=args)

        res = pydantic_validator(query=UserModelStrict)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_query_params_change_default_error_status_code(app):
    with app.test_request_context() as test_request_ctx:
        args = {}  # Empty args
        test_request_ctx.request = MockRequest(args=args)

        # Changing default validation error status code from UNPROCESSABLE_ENTITY to BAD_REQUEST
        res = pydantic_validator(
            query=FooModel, validation_error_status_code=HTTPStatus.BAD_REQUEST
        )(application_api)(test_request_ctx.request)

        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.BAD_REQUEST


def test_validate_path_params(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = {"foo": "bar", "bar": "foo"}
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=FooModel)(application_api)(test_request_ctx.request, **kwargs)
        assert res.json.get("path_params") == kwargs
        assert res.status_code == HTTPStatus.OK

        #  Validated Pydantic model becomes the path_param_model attribute of request.
        assert isinstance(test_request_ctx.request.path_param_model, FooModel)
        assert test_request_ctx.request.path_param_model.bar == "foo"


def test_validate_path_params_invalid_model(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = {"foo": "bar", "bar": "foo"}
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=UserModel)(application_api)(test_request_ctx.request, **kwargs)

        # Expected validation error.
        expected = [{'loc': ['username'], 'msg': 'field required', 'type': 'value_error.missing'}]

        assert res.json.get("validation_error")
        assert res.json.get("validation_error").get("path_params") == expected
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_path_params_invalid_params(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = ["foo", "args"]  # Invalid type for kwargs
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=FooModel)(application_api)(test_request_ctx.request, kwargs)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_path_params_empty_params(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = {}  # Empty args
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=FooModel)(application_api)(test_request_ctx.request, **kwargs)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_path_params_missing_required_field(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = {"bar": "foo"}  # "foo" is required in FooModel
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=FooModel)(application_api)(test_request_ctx.request, **kwargs)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_path_params_strict_model(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = {"username": "foo", "age": 42, "phone": 123}
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=UserModelStrict)(application_api)(test_request_ctx.request, **kwargs)
        assert res.json.get("path_params") == kwargs
        assert res.status_code == HTTPStatus.OK
        assert isinstance(test_request_ctx.request.path_param_model, UserModelStrict)


def test_validate_path_params_strict_model_extra_args(app):
    with app.test_request_context() as test_request_ctx:
        kwargs = {"username": "foo", "age": 42, "phone": 123, "foo": "bar"}  # "foo" is extra attr.
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(path_params=UserModelStrict)(application_api)(test_request_ctx.request, **kwargs)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_path_params_change_default_error_status_code(app):
    with app.test_request_context() as test_request_ctx:
        args = {}  # Empty args
        test_request_ctx.request = MockRequest(args=args)

        # Changing default validation error status code from UNPROCESSABLE_ENTITY to BAD_REQUEST
        kwargs = {}  # Empty args
        test_request_ctx.request = MockRequest()

        res = pydantic_validator(
            path_params=FooModel, validation_error_status_code=HTTPStatus.BAD_REQUEST
        )(application_api)(test_request_ctx.request, **kwargs)

        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.BAD_REQUEST


def test_validate_json_body(app):
    with app.test_request_context() as test_request_ctx:
        body = {"foo": "bar", "bar": "foo"}
        test_request_ctx.request = MockRequest(body=body)

        res = pydantic_validator(body=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("body_params") == body
        assert res.status_code == HTTPStatus.OK

        #  Validated Pydantic model becomes the body_model attribute of request.
        assert isinstance(test_request_ctx.request.body_model, FooModel)

        # Values got set in the Pydantic model.
        assert test_request_ctx.request.body_model.bar == "foo"

        # Actual request.json is unchanged.
        assert test_request_ctx.request.json == body


def test_validate_json_body_invalid_model(app):
    with app.test_request_context() as test_request_ctx:
        body = {"foo": "bar", "bar": "foo"}
        test_request_ctx.request = MockRequest(body=body)

        # Invalid model UserModel for above given args.
        res = pydantic_validator(body=UserModel)(application_api)(test_request_ctx.request)

        # Expected validation error.
        expected = [{'loc': ['username'], 'msg': 'field required', 'type': 'value_error.missing'}]

        assert res.json.get("validation_error")
        assert res.json.get("validation_error").get("body_params") == expected
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_json_body_empty_params(app):
    with app.test_request_context() as test_request_ctx:
        body = {}  # Empty args
        test_request_ctx.request = MockRequest(body=body)

        res = pydantic_validator(body=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_json_body_missing_required_field(app):
    with app.test_request_context() as test_request_ctx:
        body = {"bar": "foo"}  # "foo" is required in FooModel
        test_request_ctx.request = MockRequest(body=body)

        res = pydantic_validator(body=FooModel)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_json_body_strict_model(app):
    with app.test_request_context() as test_request_ctx:
        body = {"username": "foo", "age": 42, "phone": 123}
        test_request_ctx.request = MockRequest(body=body)

        res = pydantic_validator(body=UserModelStrict)(application_api)(test_request_ctx.request)
        assert res.json.get("body_params") == body
        assert res.status_code == HTTPStatus.OK
        assert isinstance(test_request_ctx.request.body_model, UserModelStrict)
        assert test_request_ctx.request.body_model.age == 42
        assert test_request_ctx.request.json == body


def test_validate_json_body_strict_model_extra_args(app):
    with app.test_request_context() as test_request_ctx:
        body = {"username": "foo", "age": 42, "phone": 123, "foo": "bar"}  # "foo" is extra attr.
        test_request_ctx.request = MockRequest(body=body)

        res = pydantic_validator(body=UserModelStrict)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_validate_json_body_change_default_error_status_code(app):
    with app.test_request_context() as test_request_ctx:
        body = {}  # Empty args
        test_request_ctx.request = MockRequest(body=body)

        # Changing default validation error status code from UNPROCESSABLE_ENTITY to BAD_REQUEST
        res = pydantic_validator(
            body=FooModel, validation_error_status_code=HTTPStatus.BAD_REQUEST
        )(application_api)(test_request_ctx.request)

        assert res.json.get("validation_error")
        assert res.status_code == HTTPStatus.BAD_REQUEST


def test_validate_json_body_invalid_content_type(app):
    with app.test_request_context() as test_request_ctx:
        body = "abc,123"
        test_request_ctx.request = MockRequest(body=body)

        test_request_ctx.request.headers = {"Content-Type": "text/csv"}
        res = pydantic_validator(body=UserModelStrict)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.json.get("body_params") is None
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        test_request_ctx.request.headers = {"Content-Type": "application/json"}
        res = pydantic_validator(body=UserModelStrict)(application_api)(test_request_ctx.request)
        assert res.json.get("validation_error")
        assert res.json.get("body_params") is None
        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
