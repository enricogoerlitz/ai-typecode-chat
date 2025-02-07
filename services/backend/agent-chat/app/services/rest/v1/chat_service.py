# flake8: noqa

from flask import Response
from typing import Iterator

from logger import logger
from utils.chat import ChatPOSTMessagePayloadV1
from services.ai.promptflow.v1 import promptflow
from exc import http_errors
from services.ai.client import aiclient


def handle_post_chat_message(chat_id: str, payload: dict) -> Iterator[Response]:
    try:
        cnf = ChatPOSTMessagePayloadV1(payload=payload)
        flow = promptflow.AIPromptFlow(chat_id=chat_id, cnf=cnf)
        return Response(
            flow.execute(),
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(e, exc_info=True)
        return http_errors.UNEXPECTED_ERROR_RESULT
