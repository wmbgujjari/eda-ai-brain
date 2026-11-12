from app.repositories.conversation_repository import ConversationRepository
from app.repositories.execution_repository import ExecutionRepository

class ConversationService:

    def __init__(self):
        self.repository = ConversationRepository()
        self.execution_repository = ExecutionRepository()

    def add_message(self,thread_id,user_id,role,content,chart_data=None,task_results=None,):

        conversation = self.repository.get_conversation(thread_id)
        print("the conversation of the Thread ",conversation)

        if conversation is None:
            self.repository.create_conversation(thread_id,user_id)
        
        self.repository.add_message(thread_id,role,content,chart_data,task_results)

        return self.repository.get_conversation(thread_id)

    def add_execution(
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
        return self.execution_repository.create_execution(
            thread_id=thread_id,
            user_id=user_id,
            user_request=user_request,
            workflow=workflow,
            plan=plan,
            task_results=task_results,
            chart_data=chart_data,
            final_answer=final_answer,
            status=status,
        )
    def get_executions(self, thread_id):
        return self.execution_repository.get_executions_by_thread(thread_id)
    
    def get_conversations_userId(self,user_id):

        return self.repository.get_conversations_userId(user_id)

    def get_conversation(self,thread_id):

        return self.repository.get_conversation(thread_id)
        

    def rename_conversation(self, user_id, thread_id, new_title):

        if not new_title or not new_title.strip():
            raise ValueError("Conversation title cannot be empty")

        new_title = new_title.strip()

        return self.repository.rename_conversation(
            user_id=user_id,
            thread_id=thread_id,
            new_title=new_title
        )

    def delete_conversation(self, user_id, thread_id):

        return self.repository.delete_conversation(
            user_id=user_id,
            thread_id=thread_id
        )
        
