from functools import wraps
from http import HTTPStatus
from typing import Callable, Optional, Type

from flask import jsonify, make_response, request
from pydantic import BaseModel, ValidationError

MEDIA_TYPE_JSON = "application/json"


def validate_params(model: Type[BaseModel], model_args: dict, errors: dict, error_key: str) -> BaseModel:
    try:
        validated_model = model(**model_args)
    except ValidationError as ve:
        errors[error_key] = ve.errors()
    else:
        return validated_model


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

            if query:
                try:
                    query_model = validate_params(query, request.args, errors, "query_params")
                except TypeError as ex:
                    error_msg = f"Exception occurred while parsing the query params. Error {ex}"
                    return make_response(jsonify({"validation_error": error_msg}), validation_error_status_code)

            if path_params:
                try:
                    path_param_model = validate_params(path_params, kwargs, errors, "path_params")
                except TypeError as ex:
                    error_msg = f"Exception occurred while parsing the query path params. Error {ex}"
                    return make_response(jsonify({"validation_error": error_msg}), validation_error_status_code)

            if body:
                try:
                    body_model = validate_params(body, request.json, errors, "body_params")

                except TypeError as ex:
                    content_type = request.headers.get("Content-Type", "").lower()
                    media_type = content_type.split(";")[0]
                    if media_type != MEDIA_TYPE_JSON:
                        error_msg = f"Unsupported media type '{content_type}' in request. {MEDIA_TYPE_JSON}' is required."
                        return make_response(jsonify({"validation_error": error_msg}), validation_error_status_code)

                    error_msg = f"Exception occurred while parsing the request json body. Error {ex}"
                    return make_response(jsonify({"validation_error": error_msg}), validation_error_status_code)

            request.query_model = query_model
            request.body_model = body_model
            request.path_param_model = path_param_model

            if errors:
                return make_response(jsonify({"validation_error": errors}), validation_error_status_code)

            res = func(*args, **kwargs)

            return res

        return wrapper

    return decorate
