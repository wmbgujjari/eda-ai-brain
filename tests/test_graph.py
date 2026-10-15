from app.GenAI.graph.simple_graph import graph


result = graph.invoke({
    "message": "Hello"
})

print("Graph Result:")
print(result)