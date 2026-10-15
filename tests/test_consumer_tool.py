from app.GenAI.tools.consumer_tools import get_consumption_level


print("Tool Name:")
print(get_consumption_level.name)

print("\nTool Description:")
print(get_consumption_level.description)

print("\nTool Input Schema:")
print(get_consumption_level.args_schema)