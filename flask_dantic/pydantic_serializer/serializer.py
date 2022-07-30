import json
from typing import Any, Dict, Optional, Type, Union, List

from pydantic import BaseConfig
from pydantic.class_validators import Validator
from pydantic.fields import FieldInfo, ModelField, UndefinedType

from flask_dantic.pydantic_serializer.encoders import jsonable_encoder


def get_response_field(
        name: str,
        type_: Type[Any],
        class_validators: Optional[Dict[str, Validator]] = None,
        default: Optional[Any] = None,
        required: Union[bool, UndefinedType] = False,
        model_config: Type[BaseConfig] = BaseConfig,
        field_info: Optional[FieldInfo] = None,
        alias: Optional[str] = None,
) -> ModelField:
    """
    Create a new response field. Raises if type_ is invalid.
    """
    field_info = field_info or FieldInfo(None)
    model_config.orm_mode = True

    try:
        model_field = ModelField(
            name=name,
            type_=type_,
            class_validators=class_validators,
            default=default,
            required=required,
            model_config=model_config,
            alias=alias,
            field_info=field_info
        )
    except RuntimeError:
        raise RuntimeError(
            f"Invalid args for response field. {type_} is not a valid pydantic field type."
        )

    return model_field


def serialize(
        data: Any,
        pydantic_type: Type[Any],
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        model_name: str = "ResponseModel",
        exclude_none: bool = False,
        many=False,
        json_dump: bool = True,
):
    """Create python dict from an object using a Pydantic Type"""
    if many:
        pydantic_type = List[pydantic_type]

    response_field = get_response_field(name=model_name, type_=pydantic_type)
    response_dict, errors = response_field.validate(data, {}, loc=("response",))

    if not errors:
        encoded_obj = jsonable_encoder(response_dict, include=include, exclude=exclude, exclude_none=exclude_none)
        if json_dump:
            return json.dumps(encoded_obj)
        return encoded_obj

    else:
        for error in errors:
            raise error
