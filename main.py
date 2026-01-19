from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
import json
import logging

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# ======================================================
# LOAD ENV (CRITICAL)
# ======================================================

load_dotenv()  # <-- THIS FIXES YOUR ERROR

# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ======================================================
# FASTAPI APP
# ======================================================

app = FastAPI(title="Decision Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# DATA MODELS
# ======================================================

class DecisionInput(BaseModel):
    decision: str = Field(..., min_length=10, max_length=1000)
    conversation_id: str


class QuestionResponse(BaseModel):
    question: str
    is_final: bool = False
    hint: Optional[str] = None


class Answer(BaseModel):
    conversation_id: str
    answer: str
    question_index: int


class CriteriaScore(BaseModel):
    name: str
    weight: float
    description: str


class OptionScore(BaseModel):
    option: str
    scores: List[int]
    total_score: float
    strengths: List[str] = []
    weaknesses: List[str] = []


class Analysis(BaseModel):
    decision: str
    options: List[str]
    criteria: List[CriteriaScore]
    scores: List[OptionScore]
    recommendation: str
    confidence: int
    reasoning: List[str]
    what_would_change: List[str]
    considerations: List[str]
    timeline: str = ""

# ======================================================
# STORAGE
# ======================================================

conversations: Dict[str, Dict] = {}

# ======================================================
# AI MODEL (OpenRouter)
# ======================================================

# REQUIRED env vars:
# OPENAI_API_KEY=sk-or-xxxx
# OPENAI_API_BASE=https://openrouter.ai/api/v1

model = OpenAIModel("openai/gpt-4o-mini")

# ======================================================
# AI AGENTS
# ======================================================

question_agent = Agent(
    model=model,
    system_prompt="""
You are an expert decision-making coach.
Ask ONE concise, insightful clarifying question.
Return ONLY the question text.
""".strip()
)

analysis_agent = Agent(
    model=model,
    system_prompt="""
You are a world-class decision analyst.
Use MCDA, risk analysis, and long-term reasoning.
Return structured, actionable recommendations.
""".strip()
)

# ======================================================
# HELPERS
# ======================================================

def generate_question_hints(question: str) -> str:
    if "why" in question.lower():
        return "What’s driving this decision?"
    if "risk" in question.lower():
        return "What worries you most?"
    if "time" in question.lower():
        return "Is this urgent or flexible?"
    return "Be honest and specific."

def confidence_score(scores: List[OptionScore]) -> int:
    if len(scores) < 2:
        return 75
    diff = scores[0].total_score - scores[1].total_score
    return max(60, min(95, int(70 + diff)))

# ======================================================
# ROUTES
# ======================================================

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "openai_api_key_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "openai_api_base": os.getenv("OPENAI_API_BASE"),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/decision/start", response_model=QuestionResponse)
async def start_decision(payload: DecisionInput):
    conversations[payload.conversation_id] = {
        "decision": payload.decision,
        "questions": [],
        "answers": [],
        "status": "active"
    }

    prompt = f"""
The user is deciding:

"{payload.decision}"

Ask the MOST important first question.
Return ONLY the question.
"""

    try:
        result = await question_agent.run(prompt)
        question = result.data.strip()
    except Exception as e:
        logger.error(e)
        question = "Why is this decision important to you?"

    conversations[payload.conversation_id]["questions"].append(question)

    return QuestionResponse(
        question=question,
        hint=generate_question_hints(question)
    )

# ======================================================
# ENTRYPOINT
# ======================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
