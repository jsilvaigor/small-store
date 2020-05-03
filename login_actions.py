import datetime
import sqlite3
from http import HTTPStatus
from sqlite3 import Cursor
from typing import Union

import bcrypt
import jwt
from flask import jsonify
from jwt import ExpiredSignatureError
from werkzeug.exceptions import Unauthorized, NotFound, InternalServerError

from constants import database_name, jwt_secret, jwt_expire_hours
from database_queries import (
    select_token,
    delete_token_for_user,
    select_user,
    insert_token,
)
from utils import get_field_binary
from validators import login_schema, validate_body


def get_existing_token(cursor: Cursor, user_id: int) -> Union[str, None]:
    cursor.execute(select_token, (user_id,))
    select_result = cursor.fetchone()
    if select_result is None:
        return None
    try:
        (token,) = select_result
        jwt.decode(token, jwt_secret)
        return token.decode("utf-8")
    except ExpiredSignatureError:
        cursor.execute(delete_token_for_user, (user_id,))
        return None


@validate_body(login_schema)
def login_action(body: dict):
    email = body.get("email", "")
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        cursor.execute(select_user, {"email": email})
        user = cursor.fetchone()
        if user is None:
            raise Unauthorized()

        (user_id, first_name, last_name, _email, password) = user
        if bcrypt.checkpw(get_field_binary(body, "password"), password):

            current_token = get_existing_token(cursor, user_id)
            if current_token is not None:
                conn.commit()
                return jsonify({"token": current_token})

            token = jwt.encode(
                {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": _email,
                    "exp": datetime.datetime.utcnow()
                    + datetime.timedelta(hours=jwt_expire_hours),
                    "sub": user_id,
                },
                jwt_secret,
                algorithm="HS256",
            )
            cursor.execute(insert_token, {"token": token, "user_id": user_id})
            conn.commit()
            return jsonify({"token": token.decode("utf-8")})
        else:
            raise Unauthorized()


def logout_action(decoded: dict):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(delete_token_for_user, (decoded.get("sub", ""),))
            conn.commit()
            return "", HTTPStatus.NO_CONTENT
        except Exception as e:
            return InternalServerError(description=str(e))
