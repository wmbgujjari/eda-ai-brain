from fastapi import FastAPI
from app.api.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(
    title="EDA AI Brain",
    description="AI Agent based Energy Data Analytics Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message":"EDA AI is Running"}

app.include_router(chat_router)