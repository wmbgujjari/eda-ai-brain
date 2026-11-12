
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database.mongodb import MongoDBConnection


class ExecutionRepository:

    def __init__(self):

        self.db = MongoDBConnection().get_database()

        self.executions = self.db["executions"]

        # Unique execution ID
        self.executions.create_index(
            "execution_id",
            unique=True
        )

        # Retrieve executions belonging to a conversation
        self.executions.create_index(
            [
                ("thread_id", 1),
                ("started_at", 1)
            ]
        )

    def create_execution(
        self,
        thread_id,
        user_id,
        user_request,
        workflow,
        plan=None,
        task_results=None,
        chart_data=None,
        final_answer=None,
        status="completed",
    ):

        now = datetime.now(timezone.utc)

        execution = {
            "execution_id": str(uuid4()),
            "thread_id": thread_id,
            "user_id": user_id,
            "user_request": user_request,
            "workflow": workflow,
            "plan": plan or [],
            "task_results": task_results or {},
            "chart_data": chart_data,
            "final_answer": final_answer,
            "status": status,
            "started_at": now,
            "completed_at": now,
        }

        self.executions.insert_one(execution)

        return execution

    def get_execution(self, execution_id):

        return self.executions.find_one(
            {
                "execution_id": execution_id
            },
            {
                "_id": 0
            }
        )

    def get_executions_by_thread(self, thread_id):

        return list(
            self.executions.find(
                {
                    "thread_id": thread_id
                },
                {
                    "_id": 0
                }
            ).sort("started_at", 1)
        )
