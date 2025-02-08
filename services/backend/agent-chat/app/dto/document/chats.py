from bson import ObjectId
from dataclasses import dataclass, asdict
import datetime


@dataclass
class ChatDTO:
    _id: ObjectId | None
    name: str
    context: dict
    messages: list
    createTimestamp: datetime.datetime
    updateTimestamp: datetime.datetime

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChatLLMMessageDTO:
    role: str
    content: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversationUser:
    message: ChatLLMMessageDTO
    request: dict
    system: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChatAssistentResponse:
    statusCode: int
    error: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversationAssistant:
    message: ChatLLMMessageDTO
    response: ChatAssistentResponse
    system: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChatMessageDTO:
    _id: ObjectId | None
    conversation: dict[str, ConversationUser | ConversationAssistant] | None
    createTimestamp: datetime.datetime
    updateTimestamp: datetime.datetime

    def set_user_message(self, user: ConversationUser) -> None:
        self.conversation = {}
        self.conversation["user"] = user.to_dict()
        self.conversation["assistant"] = ConversationAssistant(
            message=ChatLLMMessageDTO(role="assistant", content=""),
            response=ChatAssistentResponse(statusCode=200, error=None),
            system={}
        )
        return self

    def set_assistant_message(self, assistant: ConversationAssistant) -> None:
        self.conversation["assistant"] = assistant.to_dict()
        return self

    def to_dict(self) -> dict:
        return asdict(self)
