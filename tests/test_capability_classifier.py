
from app.GenAI.agents.capability_classifier import classify_capabilities


requests = [
    "Get the consumption level of consumer C001.",
    "Show a historical consumption of consumer C001.",
    "Get the consumption level of consumer C001 and prepare a chart of its historical consumption.",
]

for request in requests:
    print("\nRequest:", request)
    print("Capabilities:", classify_capabilities(request))