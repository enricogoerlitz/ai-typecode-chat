from flask import request, Blueprint

from services.rest.v1 import chat_service
from exc import http_errors


VERSION = "v1"
ROUTE = "chats"

bp = Blueprint(ROUTE, __name__)


def url(route: str) -> str:
    return f"/api/{VERSION}/{route}"


@bp.route(url(f"{ROUTE}"), methods=["GET", "POST"])
def handle_chats():
    match request.method:
        case "GET":
            return http_errors.not_implemented()
        case "POST":
            return http_errors.not_implemented()

    return http_errors.not_implemented()


@bp.route(url(f"{ROUTE}/<string:id>"), methods=["GET", "PATCH", "DELETE"])
def handle_chat_by_id(id: str):
    match request.method:
        case "GET":
            return http_errors.not_implemented()
        case "PATCH":
            return http_errors.not_implemented()
        case "DELETE":
            return http_errors.not_implemented()

    return http_errors.not_implemented()


@bp.route(url(f"{ROUTE}/<string:id>/messages"), methods=["GET", "POST"])
def handle_chat_messages(id: str):
    match request.method:
        case "GET":
            return http_errors.not_implemented()
        case "POST":
            return chat_service.handle_post_chat_message(
                chat_id=id,
                payload=request.get_json()
            )
    return http_errors.not_implemented()


@bp.route(url(f"{ROUTE}/<string:id>/messages/<string:message_id>"), methods=["GET", "PATCH", "DELETE"])  # noqa
def handle_chat_message_by_id(id: str, message_id: str):
    match request.method:
        case "GET":
            return http_errors.not_implemented()
        case "PATCH":
            return http_errors.not_implemented()
        case "DELETE":
            return http_errors.not_implemented()

    return http_errors.not_implemented()
