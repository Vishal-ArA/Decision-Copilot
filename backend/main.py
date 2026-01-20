from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
import logging
import httpx
from dotenv import load_dotenv

# ======================================================
# LOAD ENV
# ======================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(level=logging.INFO)
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

from pydantic import BaseModel

class Answer(BaseModel):
    conversation_id: str
    answer: str
    question_index: int



class QuestionResponse(BaseModel):
    question: str
    is_final: bool = False
    hint: Optional[str] = None


# ======================================================
# STORAGE (IN-MEMORY)
# ======================================================

conversations: Dict[str, Dict] = {}

# ======================================================
# HELPERS
# ======================================================

def generate_question_hints(question: str) -> str:
    q = question.lower()
    if "why" in q:
        return "What’s driving this decision?"
    if "risk" in q:
        return "What worries you most?"
    if "time" in q:
        return "Is this urgent or flexible?"
    return "Be honest and specific."


async def ask_llm(prompt: str) -> str:
    """
    Calls OpenRouter / OpenAI-compatible API safely.
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://decision-copilot",
        "X-Title": "Decision Copilot",
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an expert decision-making coach."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{OPENAI_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
        )

        if r.status_code != 200:
            logger.error(r.text)
            raise HTTPException(status_code=500, detail="LLM request failed")

        return r.json()["choices"][0]["message"]["content"].strip()

# ======================================================
# ROUTES
# ======================================================

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "openai_key_loaded": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/decision/start", response_model=QuestionResponse)
async def start_decision(payload: DecisionInput):
    conversations[payload.conversation_id] = {
        "decision": payload.decision,
        "questions": [],
        "answers": [],
        "status": "active",
    }

    prompt = f"""
The user is deciding:

"{payload.decision}"

Ask ONE concise, insightful clarifying question.
Return ONLY the question text.
"""

    try:
        question = await ask_llm(prompt)
    except Exception as e:
        logger.exception(e)
        question = "Why is this decision important to you?"

    conversations[payload.conversation_id]["questions"].append(question)

    return QuestionResponse(
        question=question,
        hint=generate_question_hints(question),
    )

# ======================================================
# ENTRYPOINT (LOCAL ONLY)
# ======================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
@app.post("/api/decision/answer", response_model=QuestionResponse)
async def answer_question(payload: Answer):
    convo = conversations.get(payload.conversation_id)

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    convo["answers"].append(payload.answer)

    # STOP after 3 answers
    if len(convo["answers"]) >= 3:
        convo["status"] = "completed"
        return QuestionResponse(
            question="Thanks. I have enough information to give you a recommendation.",
            is_final=True
        )

    prompt = f"""
Decision: {convo['decision']}

Previous Q&A:
{list(zip(convo['questions'], convo['answers']))}

Ask the NEXT most important clarifying question.
Return ONLY the question.
"""

    try:
        result = await question_agent.run(prompt)
        question = result.data.strip()
    except Exception as e:
        logger.error(e)
        question = "What else should I consider before deciding?"

    convo["questions"].append(question)

    return QuestionResponse(
        question=question,
        hint=generate_question_hints(question)
    )
@app.post("/api/decision/answer", response_model=QuestionResponse)
async def answer_question(payload: Answer):
    convo = conversations.get(payload.conversation_id)

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    convo["answers"].append(payload.answer)

    # STOP after 3 answers
    if len(convo["answers"]) >= 3:
        convo["status"] = "completed"
        return QuestionResponse(
            question="Thanks. I have enough information to give you a recommendation.",
            is_final=True
        )

    prompt = f"""
Decision: {convo['decision']}

Previous Q&A:
{list(zip(convo['questions'], convo['answers']))}

Ask the NEXT most important clarifying question.
Return ONLY the question.
"""

    try:
        result = await question_agent.run(prompt)
        question = result.data.strip()
    except Exception as e:
        logger.error(e)
        question = "What else should I consider before deciding?"

    convo["questions"].append(question)

    return QuestionResponse(
        question=question,
        hint=generate_question_hints(question)
    )
