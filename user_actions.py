import bcrypt
import sqlite3
from sqlite3 import IntegrityError
from http import HTTPStatus

from werkzeug.exceptions import BadRequest

from constants import database_name
from database_queries import insert_user
from utils import get_field_binary
from validators import validate_body, user_schema


@validate_body(user_schema)
def create_user_action(body: dict):
    password = get_field_binary(body, "password")
    hash = bcrypt.hashpw(password, bcrypt.gensalt(14))
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                insert_user,
                (body.get("firstName"), body.get("lastName"), body.get("email"), hash),
            )

            conn.commit()
            return "", HTTPStatus.CREATED
        except IntegrityError as error:
            raise BadRequest(description=str(error))
