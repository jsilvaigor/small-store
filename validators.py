import json
import sqlite3

import jwt
from cerberus import Validator
import functools

from flask import request
from jwt import ExpiredSignatureError
from werkzeug.exceptions import InternalServerError, Forbidden, Unauthorized, BadRequest

from constants import jwt_secret, database_name
from database_queries import select_token


def validate_authorization(func):
    @functools.wraps(func)
    def wrapper(**kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise Forbidden()

        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, jwt_secret)
            with sqlite3.connect(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute(select_token, (decoded.get("sub", 0),))
                token = cursor.fetchone()
                if token is not None:
                    return func(decoded, token, **kwargs)
                else:
                    raise Unauthorized(
                        description="Invalid or Expired token. Login again."
                    )
        except ExpiredSignatureError:
            raise Unauthorized(description="Invalid or Expired token. Login again.")

    return wrapper


def validate_body(schema: dict):
    validator = Validator(schema)

    def inner(func):
        @functools.wraps(func)
        def wrapper(body: dict, **kwargs):
            if validator.validate(body):
                return func(body, **kwargs)
            else:
                raise BadRequest(description=json.dumps(validator.errors))

        return wrapper

    return inner


email_schema = {
    "required": True,
    "type": "string",
    "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
}

user_schema = {
    "firstName": {"required": True, "type": "string"},
    "lastName": {"required": True, "type": "string"},
    "email": email_schema,
    "password": {"type": "string"},
}

login_schema = {"email": email_schema, "password": {"type": "string"}}
