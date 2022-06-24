from distutils.log import error
from functools import wraps
from http import HTTPStatus
from typing import Callable, Optional, Type

from flask import jsonify, make_response, request
from pydantic import BaseModel, ValidationError
from .exceptions import RequestValidationError

MEDIA_TYPE_JSON = "application/json"


def validate_params(model: Type[BaseModel], model_args: dict, errors: dict, error_key: str) -> BaseModel:
    try:
        validated_model = model(**model_args)
    except ValidationError as ve:
        errors[error_key] = ve.errors()
    else:
        return validated_model


def get_error_key(type_: str):
    return (("body_params", "path_params")[
        type_ == "path"], "query_params")[type_ == "args"]


def validate_(model, type_: str, errors):
    error_key = get_error_key(type_)
    err_ = ""
    content_type = request.headers.get(
        "Content-Type", "").lower()
    media_type = content_type.split(";")[0]
    payload = getattr(request, type_ if type_ != "path" else "view_args")
    try:
        query_model = validate_params(
            model, payload, errors, error_key)
    except TypeError as ex:
        if error_key == "query_params":
            err_ = "the query params"
        elif error_key == "path_params":
            err_ == "the path params"
        elif error_key == "body_params":
            err_ = "the request json body"
        error_msg = f"Exception occurred while parsing {err_}. Error {ex}"
        if error_key == "body_params" and media_type != MEDIA_TYPE_JSON:
            error_msg = f"Unsupported media type '{content_type}' in request. {MEDIA_TYPE_JSON}' is required."
        raise RequestValidationError(error_message=error_msg)
    return query_model


def pydantic_validator(
        body: Optional[Type[BaseModel]] = None,
        query: Optional[Type[BaseModel]] = None,
        path_params: Optional[Type[BaseModel]] = None,
        validation_error_status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY
):
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors = {}
            query_model = body_model = path_param_model = None

            try:
                if query:
                    query_model = validate_(query, "args", errors)

                if path_params:
                    path_param_model = validate_(path_params, "path", errors)

                if body:
                    body_model = validate_(body, "json", errors)
            except RequestValidationError as e:
                return make_response(jsonify({"validation_error": e.error_message}), validation_error_status_code)

            request.query_model = query_model
            request.body_model = body_model
            request.path_param_model = path_param_model

            if errors:
                return make_response(jsonify({"validation_error": errors}), validation_error_status_code)

            res = func(*args, **kwargs)

            return res

        return wrapper

    return decorate
