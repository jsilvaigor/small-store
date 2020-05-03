from flask import Flask, request, jsonify, Response
import sqlite3
import json

from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import HTTPException

from login_actions import login_action, logout_action
from user_actions import create_user_action
from constants import database_name
from utils import get_file
from validators import validate_authorization

app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {"code": e.code, "name": e.name, "description": e.description,}
    )
    response.content_type = "application/json"
    return response


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    body = request.get_json()
    return create_user_action(body)


@app.route("/api/v1/login", methods=["POST"])
def login():
    body = request.get_json()
    return login_action(body)


@app.route("/api/v1/logout", methods=["POST"])
@validate_authorization
def logout(decoded: dict, token: str):
    return logout_action(decoded)


@app.route("/api/v1/store/categories", methods=["GET"])
@validate_authorization
def categories(decoded: dict, token: str):
    return jsonify({"productCategories": ["Vestido", "Blusa", "Calça", "Short"]})


@app.route("/api/docs/openapi.yaml", methods=["GET"])
def get_swagger():
    content = get_file("openapi.yaml")
    return Response(content, content_type="text/vnd.yaml")


SWAGGER_URL = "/api/docs"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    "/api/docs/openapi.yaml",
)

# Register blueprint at URL
# (URL must match the one given to factory function above)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    app.run()
