import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .ai_service import extract_required_skills_with_claude, fallback_skills, rank_with_claude
from .data_loader import load_employees
from .models import (
    AIResult,
    AISearchRequest,
    AISearchResponse,
    AISkillsRequest,
    AISkillsResponse,
    ManualSearchRequest,
    ManualSearchResponse,
)
from .search import build_shortlist, manual_search

load_dotenv()
logger = logging.getLogger("workplace_knowledge_map")

CSV_PATH = os.getenv("EMPLOYEE_CSV_PATH", "../data/employees.csv")

_MAX_MANUAL_RESULTS = 30
_AI_SHORTLIST_SIZE = 20

employees = []


@asynccontextmanager
async def lifespan(_: FastAPI):
    global employees
    employees = load_employees(CSV_PATH)
    logger.info("Loaded %s employees from %s", len(employees), CSV_PATH)
    yield


app = FastAPI(title="Workplace Knowledge Map API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search/manual", response_model=ManualSearchResponse)
def search_manual(payload: ManualSearchRequest):
    results = manual_search(
        employees,
        keyword=payload.keyword,
        department=payload.department,
        max_results=_MAX_MANUAL_RESULTS,
    )
    return ManualSearchResponse(results=results)


@app.post("/search/ai", response_model=AISearchResponse)
async def ai_search(payload: AISearchRequest):
    approved_skills = [skill.strip() for skill in payload.required_skills if skill.strip()]
    effective_query = payload.query
    if approved_skills:
        effective_query = f"{payload.query}. Required skills: {', '.join(approved_skills)}."

    shortlist = build_shortlist(employees, effective_query, max_candidates=_AI_SHORTLIST_SIZE)

    try:
        ranked = await rank_with_claude(effective_query, shortlist, top_n=payload.top_n)
        return AISearchResponse(results=ranked)
    except Exception as exc:
        logger.exception("AI ranking failed, returning fallback. query=%r error=%s", effective_query, exc)
        fallback = [
            AIResult(
                employee=employee,
                reason="Fallback match from keyword retrieval while AI ranking is unavailable.",
            )
            for employee in shortlist[: payload.top_n]
        ]
        return AISearchResponse(results=fallback)


@app.post("/search/ai/skills", response_model=AISkillsResponse)
async def ai_extract_skills(payload: AISkillsRequest):
    try:
        skills = await extract_required_skills_with_claude(payload.query)
    except Exception as exc:
        logger.exception("AI skill extraction failed, using fallback tokens. query=%r error=%s", payload.query, exc)
        skills = fallback_skills(payload.query)

    return AISkillsResponse(required_skills=skills)
