from functools import wraps
from http import HTTPStatus
from typing import Callable, Optional, Type

from flask import jsonify, make_response, request
from pydantic import BaseModel, ValidationError

from .exceptions import RequestValidationError

MEDIA_TYPE_JSON = "application/json"

error_key_map = {
    "query_params": "the query params",
    "path_params": "the path params",
    "body_params": "the request json body",
}


def validate_params(model: Type[BaseModel], model_args: dict) -> BaseModel:
    validated_model = model(**model_args)
    return validated_model


def get_error_key(type_: str):
    """
    Args:
         type_ (str): type_ would be either args, path or json
    """
    return (("body_params", "path_params")[type_ == "path"], "query_params")[type_ == "args"]


def validate_(model, type_: str, errors):
    error_key = get_error_key(type_)
    error_message = None
    content_type = request.headers.get("Content-Type", "").lower()
    media_type = content_type.split(";")[0]
    payload = getattr(request, type_ if type_ != "path" else "view_args")
    query_model = None

    try:
        query_model = validate_params(
            model, payload
        )
    except ValidationError as ex:
        error_message = f"Exception occurred while parsing {error_key_map[error_key]}. Error {ex}"
        errors[error_key] = ex.errors()

    except TypeError as ex:
        error_message = str(ex)
        if error_key == "body_params" and media_type != MEDIA_TYPE_JSON:
            error_message = f"Unsupported media type '{content_type}' in request. {MEDIA_TYPE_JSON}' is required."

    if error_message:
        raise RequestValidationError(error_message=error_message)

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
                return make_response(
                    jsonify({"validation_error": e.error_message, "errors": errors}), validation_error_status_code
                )

            request.query_model = query_model
            request.body_model = body_model
            request.path_param_model = path_param_model

            res = func(*args, **kwargs)

            return res

        return wrapper

    return decorate
