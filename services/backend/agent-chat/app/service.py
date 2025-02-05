from flask import Flask
from flask_cors import CORS

from apis.v1.chats import bp as bp_chats_v1


class FlaskConfig:
    pass


def healthcheck():
    return "ok", 200


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)

    CORS(app)

    app.route("/api/v1/healthcheck")(healthcheck)

    app.register_blueprint(bp_chats_v1)

    return app
