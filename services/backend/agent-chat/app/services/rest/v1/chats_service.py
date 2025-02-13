from bson import ObjectId, json_util
from flask import Response
from typing import Iterator

from logger import logger
from utils.chats import ChatMessagePayload
from services.ai.promptflow.v1 import promptflow
from exc import http_errors, errors
from database.document import chatdb
from datetime import datetime
from dto.document.chats import (
    ChatMessageDTO,
    ConversationUser,
    ConversationAssistant,
    ChatLLMMessageDTO,
    ChatAssistentResponse,
    ChatDTO
)


def handle_get_chat(chat_id: str, is_detail) -> Response:
    try:
        fields = {}
        if not is_detail:
            fields["_id"] = 1
            fields["name"] = 1
            fields["context"] = 1
            fields["messages._id"] = 1
            fields["messages.conversation.user.message"] = 1
            fields["messages.conversation.assistant.message"] = 1
            fields["messages.createTimestamp"] = 1

        result = chatdb.find_by_id(chat_id, fields=fields)
        if result is None:
            return http_errors.not_found(f"Object with _id={chat_id} not found.")  # noqa

        return Response(
            json_util.dumps(result),
            status=200,
            content_type="application/json"
        )

    except Exception as e:
        logger.error(e, exc_info=True)
        return http_errors.UNEXPECTED_ERROR_RESULT


def handle_get_list_chats(is_detail: bool) -> Response:
    try:
        query = {}
        fields = {}

        if not is_detail:
            fields["_id"] = 1
            fields["name"] = 1
            fields["context"] = 1

        result = chatdb.find(query=query, fields=fields)

        return Response(
            json_util.dumps(result),
            status=200,
            content_type="application/json"
        )
    except Exception as e:
        logger.error(e, exc_info=True)
        return http_errors.UNEXPECTED_ERROR_RESULT


def handle_put_chats(payload: dict) -> Response:
    try:
        _id = ObjectId(payload["_id"]) if "_id" in payload else None
        name = payload.get("name", "untitled")
        type_code = payload.get("typeCode", None)

        if type_code is None:
            raise errors.ValueErrorGeneral("Typecode should no be blank")

        now = datetime.now()
        chat = ChatDTO(
            _id=_id,
            name=name,
            context={
                "deviceTypeCode": type_code
            },
            messages=[],
            createTimestamp=now,
            updateTimestamp=now
        )
        chat_id = chatdb.put(chat)

        if chat_id is None:
            raise Exception("Could not create an chat.")

        return {"_id": chat_id}, 200
    except errors.ValueErrorGeneral as e:
        return http_errors.bad_request(e)

    except Exception as e:
        logger.error(e, exc_info=True)
        return http_errors.UNEXPECTED_ERROR_RESULT


def handle_delete_chat(chat_id: str) -> Response:
    try:
        _ = chatdb.delete(chat_id)
        return "", 204
    except Exception as e:
        logger.error(e, exc_info=True)
        return http_errors.UNEXPECTED_ERROR_RESULT


def handle_put_chat_message(chat_id: str, payload: dict) -> Iterator[Response]:
    cnf = ChatMessagePayload(chat_id=chat_id, payload=payload)

    try:
        cnf.validate()

        if not chatdb.is_chat_exising(chat_id):
            return http_errors.not_found(f"Object with _id={chat_id} not found.")  # noqa

        message = _add_user_message(cnf)

        flow = promptflow.AIPromptFlow(
            chat_id=chat_id,
            cnf=cnf,
            message=message
        )

        return Response(
            flow.execute(add_system_message=_add_system_message),
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(e, exc_info=True)
        return http_errors.UNEXPECTED_ERROR_RESULT


def _add_user_message(cnf: ChatMessagePayload) -> ChatMessageDTO:
    now = datetime.now()

    message = ChatMessageDTO(
        _id=ObjectId(),
        conversation=None,
        createTimestamp=now,
        updateTimestamp=now
    )

    if cnf.message_id is not None:
        db_message = chatdb.find_message_by_id(
            chat_id=cnf.chat_id,
            message_id=cnf.message_id
        )
        if db_message is None:
            raise Exception(f"Message with _id={cnf.message_id} not found.")

        message._id = db_message["_id"]
        message.createTimestamp = db_message["createTimestamp"]

    user_message = ConversationUser(
        message=ChatLLMMessageDTO(role="user", content=cnf.message_content),
        request=cnf.payload,
        system={
            "createTimestamp": now
        }
    )

    message.set_user_message(user_message)

    result = chatdb.put_message(cnf.chat_id, message)

    if result != 1:
        raise Exception("Failed to save message.")

    return message


def _add_system_message(
        *,
        chat_id: str,
        message: ChatMessageDTO,
        content: str,
        response: ChatAssistentResponse,
        system_error: str
) -> None:
    now = datetime.now()

    assistant = ConversationAssistant(
        message=ChatLLMMessageDTO(role="assistant", content=content),
        response=response,
        system={
            "createTimestamp": now,
            "error": system_error
        }
    )

    message.set_assistant_message(assistant)

    result = chatdb.put_message(chat_id, message)

    if result != 1:
        raise Exception("Failed to save message.")

    return
