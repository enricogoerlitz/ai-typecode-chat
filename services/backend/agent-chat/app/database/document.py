import pymongo
import pymongo.collection
import pymongo.database

from datetime import datetime
from abc import ABC, abstractmethod
from typing import Literal

from bson import ObjectId
from exc import errors
from dto.document.chats import ChatMessageDTO, ChatDTO


class IDocumentChatDB(ABC):
    @abstractmethod
    def is_chat_exising(self, _id: str): pass

    @abstractmethod
    def is_chat_message_existing(self, chat_id: str, message_id: str) -> bool: pass  # noqa

    @abstractmethod
    def find(self, query: dict = None, fields: dict = None) -> list[dict]: pass

    @abstractmethod
    def find_by_id(self, _id: str, fields: dict = None) -> dict: pass

    @abstractmethod
    def find_message_by_id(self, chat_id: str, message_id: str) -> dict: pass

    @abstractmethod
    def find_messages_until_id_match(self, chat_id: str, message_id: str, n: int) -> list[dict]: pass  # noqa

    @abstractmethod
    def put(self, data: ChatDTO) -> str: pass

    @abstractmethod
    def put_message(self, chat_id: str, message: ChatMessageDTO) -> int: pass

    @abstractmethod
    def delete(self, _id: str) -> int: pass

    @abstractmethod
    def delete_message(self, chat_id: str, message_id: str): pass

    @staticmethod
    def create_chatdb(
        type: Literal["MONGO_DB", "COSMOS_DB"]
    ) -> 'IDocumentChatDB':
        match type:
            case "MONGO_DB":
                return MongoChatDB(
                    mongo_uri="mongodb://localhost:27017/",
                    database="emtec_ai_device_type",
                    collection="chats"
                )

        err = "For IDocumentDB type is only 'MONGO_DB' allowed"
        raise errors.ValueErrorGeneral(err)


class MongoChatDB(IDocumentChatDB):
    def __init__(
            self,
            mongo_uri: str,
            database: str,
            collection: str
    ):
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client[database]
        self._collection = self._db[collection]

    @property
    def client(self) -> pymongo.MongoClient:
        return self._client

    @property
    def db(self) -> pymongo.database.Database:
        return self._db

    @property
    def collection(self) -> pymongo.collection.Collection:
        return self._collection

    def is_chat_exising(self, _id: str) -> bool:
        _id = ObjectId(_id)
        chat = self.collection.find_one({"_id": _id}, {"_id": 1})

        return chat is not None

    def is_chat_message_existing(self, chat_id: str, message_id: str) -> bool:
        chat_id = ObjectId(chat_id)
        message_id = ObjectId(message_id)

        message = self.collection.find_one({
            "_id": chat_id,
            "messages._id": message_id
        })

        return message is not None

    def find(self, query: dict = None, fields: dict = None):
        if query is None:
            query = {}
        if fields is None:
            fields = {}

        chats = [chat for chat in self.collection.find(query, fields)]
        return chats

    def find_by_id(self, _id: str, fields: dict = None) -> dict:
        _id = ObjectId(_id)
        if fields is None:
            fields = {}

        chat = self.collection.find_one({"_id": _id}, fields)
        return chat

    def find_message_by_id(self, chat_id: str, message_id: str) -> dict:
        chat_id = ObjectId(chat_id)
        message_id = ObjectId(message_id)

        message_doc = self.collection.find_one(
            {"_id": chat_id, "messages._id": message_id},
            {"messages.$": 1}
        )

        if (
            message_doc and "messages" in message_doc and
            len(message_doc["messages"]) > 0
        ):
            return message_doc["messages"][0]

        return None

    def find_messages_until_id_match(
            self,
            chat_id: str,
            message_id: str,
            n: int
    ) -> list[dict]:
        chat_id = ObjectId(chat_id)
        message_id = ObjectId(message_id)

        query = {"_id": chat_id}
        fields = {
            "messages._id": 1,
            "messages.conversation.user.message": 1,
            "messages.conversation.assistant.message": 1
        }
        doc: dict = self.collection.find_one(query, fields)

        filtered_messages = []
        for message in doc.get("messages", []):
            if message["_id"] == message_id:
                break
            filtered_messages += [
                message["conversation"]["user"]["message"],
                message["conversation"]["assistant"]["message"]
            ]

        n = n * 2
        filtered_messages = filtered_messages[-n:]

        return filtered_messages

    def put(self, chat: ChatDTO) -> str:
        chat_data = chat.to_dict()

        if chat._id is not None:
            chat_data["updateDatetime"] = datetime.now()
            result = self.collection.find_one_and_replace(
                filter={"_id": chat._id},
                replacement=chat_data
            )

            return str(result["_id"])

        chat_data["_id"] = ObjectId()
        result = self.collection.insert_one(chat_data)
        return str(result.inserted_id)

    def put_message(
            self,
            chat_id: str,
            message: ChatMessageDTO
    ) -> int:
        chat_id = ObjectId(chat_id)
        message_data = message.to_dict()

        if self.is_chat_message_existing(chat_id, message._id):  # noqa
            result = self.collection.update_one(
                {"_id": chat_id, "messages._id": message._id},
                {"$set": {"messages.$": message_data}},
            )

            return result.modified_count

        result = self.collection.update_one(
            {"_id": chat_id},
            {"$push": {"messages": message_data}}
        )

        return result.modified_count

    def delete(self, _id: str) -> None:
        _id = ObjectId(_id)
        self.collection.delete_one({"_id": _id})

    def delete_message(self, chat_id: str, message_id: str):
        chat_id = ObjectId(chat_id)
        message_id = ObjectId(message_id)

        result = self.collection.update_one(
            {"_id": chat_id},
            {"$pull": {"messages": {"_id": message_id}}}
        )

        return result.modified_count


chatdb = IDocumentChatDB.create_chatdb("MONGO_DB")
