from app.repositories.conversation_repository import ConversationRepository

class ConversationService:

    def __init__(self):
        self.repository = ConversationRepository()
    
    def add_message(self,thread_id,user_id,role,content,chart_data=None):

        conversation = self.repository.get_conversation(thread_id)
        print("the conversation of the Thread ",conversation)

        if conversation is None:
            self.repository.create_conversation(thread_id,user_id)
        
        self.repository.add_message(thread_id,role,content,chart_data)

        return self.repository.get_conversation(thread_id)

    def get_conversations_userId(self,user_id):

        return self.repository.get_conversations_userId(user_id)

    def get_conversation(self,thread_id):

        return self.repository.get_conversation(thread_id)
        

        
