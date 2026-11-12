from datetime import datetime, timezone
from uuid import uuid4
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

    def add_message(self,thread_id,role,content,chart_data=None,task_results=None,):
        now = datetime.now(timezone.utc)

        message = {
            "role": role,
            "content": content,
            "chart_data": chart_data,
            "timestamp": now,
        }

        # Preserve specialist results when provided.
        if task_results is not None:
            message["task_results"] = task_results

        self.conversations.update_one(
            {"thread_id": thread_id},
            {
                "$push": {
                    "messages": message
                },
                "$set": {
                    "updated_at": now
                },
            },
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
                {
                    "user_id": user_id,
                    "is_active": {"$ne": False}
                },
                {
                    "_id": 0,
                    "thread_id": 1,
                    "title": 1,
                    "messages": 1,
                    "created_at": 1,
                    "update_at": 1,
                    "is_active": 1
                }
            ).sort("update_at", -1)
        )

        result = []

        for conversation in conversations:

            # Prefer manually saved title
            title = conversation.get("title")

            # Generate title from first user message if not renamed
            if not title:
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


    def rename_conversation(self, user_id, thread_id, new_title):

        new_title = new_title.strip()

        if not new_title:
            return False

        result = self.conversations.update_one(
            {
                "user_id": user_id,
                "thread_id": thread_id,
                "is_active": {"$ne": False}
            },
            {
                "$set": {
                    "title": new_title,
                    "update_at": datetime.now()
                }
            }
        )

        return result.matched_count > 0

    def delete_conversation(self, user_id, thread_id):

        result = self.conversations.update_one(
            {
                "user_id": user_id,
                "thread_id": thread_id,
                "is_active": {"$ne": False}
            },
            {
                "$set": {
                    "is_active": False,
                    "update_at": datetime.now()
                }
            }
        )

        return result.modified_count > 0