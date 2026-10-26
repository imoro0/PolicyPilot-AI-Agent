
from dotenv import load_dotenv

# Load environment variables before importing the agent.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.API.chat import router as chat_router

app = FastAPI(
    title="PolicyPilot AI Agent",
    description="An AI agent for company privacy and policy documents.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def home():
    return {
        "message": "PolicyPilot AI Agent is running!",
        "status": "success"
    }
