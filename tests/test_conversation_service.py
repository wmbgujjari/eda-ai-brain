from app.services.conversation_service import ConversationService

conversation_service = ConversationService()

#conversation_service.add_message(
#    "chat-004","user-001","user","What is the Consumption Level of Consumer C001"
#)

#conversation_service.add_message(
#    "chat-004","user-001","assistant","Consumption Level of Consumer C001 is Medium"
#)

conversation = conversation_service.repository.get_conversation("chat-005")

print("User Messages:")
print("/n",conversation)