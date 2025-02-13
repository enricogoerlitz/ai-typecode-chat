from flask import request, Blueprint

from services.rest.v1 import chats_service
from exc import http_errors


VERSION = "v1"
ROUTE = "chats"

bp = Blueprint(ROUTE, __name__)


def url(route: str) -> str:
    return f"/api/{VERSION}/{route}"


@bp.route(url(f"{ROUTE}"), methods=["GET", "PUT"])
def handle_chats():
    match request.method:
        case "GET":
            is_detail = request.args.get("detail", "false") == "true"
            return chats_service.handle_get_list_chats(is_detail=is_detail)
        case "PUT":
            return chats_service.handle_put_chats(request.get_json())

    return http_errors.not_implemented()


@bp.route(url(f"{ROUTE}/<string:id>"), methods=["GET", "DELETE"])
def handle_chat_by_id(id: str):
    match request.method:
        case "GET":
            is_detail = request.view_args.get("detail", "false") == "true"
            return chats_service.handle_get_chat(id, is_detail=is_detail)
        case "DELETE":
            return chats_service.handle_delete_chat(id)

    return http_errors.not_implemented()


@bp.route(url(f"{ROUTE}/<string:id>/messages"), methods=["PUT"])
def handle_chat_messages(id: str):
    match request.method:
        case "GET":
            return http_errors.not_implemented()
        case "PUT":
            return chats_service.handle_put_chat_message(
                chat_id=id,
                payload=request.get_json()
            )
    return http_errors.not_implemented()
