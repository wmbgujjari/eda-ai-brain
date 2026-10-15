from app.repositories.conversation_repository import ConversationRepository


repository = ConversationRepository()


repository.create_conversation(
    "chat-003",
    "user-001"
)


repository.add_message(
    "chat-003",
    "user",
    "What is the consumption level of C003?"
)


repository.add_message(
    "chat-003",
    "assistant",
    "The consumption level of C003 is MEDIUM."
)


conversation = repository.get_conversation(
    "chat-003"
)


print("Conversation Created")

print("\nConversation:")
print(conversation)