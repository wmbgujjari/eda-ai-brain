from datetime import datetime, timezone

from app.core.database.mongodb import MongoDBConnection


class ConversationRepository:

    def __init__(self):

        self.db = MongoDBConnection().get_database()

        self.conversations = self.db["conversations"]

        # thread_id must be unique
        self.conversations.create_index(
            "thread_id",
            unique=True
        )

    def create_conversation(self, thread_id, user_id):

        now = datetime.now(timezone.utc)

        conversation = {
            "thread_id": thread_id,
            "user_id": user_id,
            "created_at": now,
            "update_at": now,
            "messages": []
        }

        return self.conversations.insert_one(conversation)

    def add_message(self, thread_id, role, content,chart_data=None):

        now = datetime.now(timezone.utc)

        self.conversations.update_one(
            {
                "thread_id": thread_id
            },
            {
                "$push": {
                    "messages": {
                        "role": role,
                        "content": content,
                        "chart_data": chart_data,
                        "timestamp": now
                    }
                },
                "$set": {
                    "updated_at": now
                }
            }
        )

    def get_conversation(self, thread_id):

        return self.conversations.find_one(
            {
                "thread_id": thread_id
            },
            {
                "_id": 0
            }
        )

    def get_conversations_userId(self, user_id):

        conversations = list(
            self.conversations.find(
                {"user_id": user_id},
                {
                    "_id": 0,
                    "thread_id": 1,
                    "messages": 1,
                    "created_at": 1,
                    "update_at": 1
                }
            ).sort("update_at", -1)
        )

        result = []

        for conversation in conversations:

            title = "New Chat"

            for message in conversation.get("messages", []):

                if message.get("role") == "user":
                    title = message.get("content", "New Chat")
                    break

            result.append({
                "thread_id": conversation["thread_id"],
                "title": title,
                "created_at": conversation.get("created_at"),
                "update_at": conversation.get("update_at")
            })

        return result