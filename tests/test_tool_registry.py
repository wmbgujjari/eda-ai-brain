from app.GenAI.tools.tool_registry import TOOLS

for tools in TOOLS:
    print("-",tools.name)