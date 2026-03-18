import json
import os
import re

import httpx

from .models import AIResult, Employee

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

_MAX_TOKENS_SKILLS = 220
_MAX_TOKENS_RANK = 450
_SKILLS_CAP = 8


def _candidate_payload(employee: Employee) -> dict:
    return {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "department": employee.department,
        "role": employee.role,
        "skills": employee.skills,
        "projects": employee.projects,
        "bio": employee.bio,
    }


def _extract_json_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Claude response did not contain valid JSON")
    return text[start : end + 1]


def _clean_reason(reason: str) -> str:
    cleaned = reason.strip()
    cleaned = cleaned.replace("which matches the user's query", "")
    cleaned = cleaned.replace('which matches the user query', "")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip(" ,.-")


async def _send_to_claude(user_content: str, max_tokens: int = 450) -> str:
    api_key = os.getenv("ANTHROPIC_KEY", "").strip()
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_KEY is not configured")

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0,
        "system": (
            "You are an assistant for a workplace knowledge map. "
            "Return strict JSON only, no markdown."
        ),
        "messages": [
            {
                "role": "user",
                "content": user_content,
            }
        ],
    }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(ANTHROPIC_URL, headers=headers, json=payload)
        if response.is_error:
            body_text = response.text[:1000]
            raise RuntimeError(
                f"Anthropic API error status={response.status_code} model={model} body={body_text}"
            )
        data = response.json()

    content_blocks = data.get("content", [])
    return "".join(block.get("text", "") for block in content_blocks if block.get("type") == "text")


def _dedupe_skills(items: list[str], max_count: int = _SKILLS_CAP) -> list[str]:
    """Return a deduplicated, lowercased list of skills capped at max_count."""
    seen: list[str] = []
    for item in items:
        skill = str(item).strip().lower()
        if skill and skill not in seen:
            seen.append(skill)
        if len(seen) == max_count:
            break
    return seen


_FALLBACK_STOP_WORDS = {"with", "from", "that", "this", "have", "need", "find", "engineer", "developer"}


def fallback_skills(query: str) -> list[str]:
    """Extract skill keywords from a query without calling the AI API."""
    tokens = [token.lower() for token in re.split(r"\W+", query) if len(token) > 2]
    return _dedupe_skills([t for t in tokens if t not in _FALLBACK_STOP_WORDS])


async def extract_required_skills_with_claude(query: str) -> list[str]:
    user_content = (
        "Extract required skill keywords from the user query.\n"
        f"User query:\n{query}\n\n"
        "Return strict JSON only with this schema:\n"
        '{"required_skills":["skill1","skill2"]}\n'
        "Rules: return 3 to 8 concise skill keywords, no sentences, no duplicates."
    )
    text = await _send_to_claude(user_content=user_content, max_tokens=_MAX_TOKENS_SKILLS)
    parsed = json.loads(_extract_json_block(text))

    cleaned = _dedupe_skills(parsed.get("required_skills", []))
    return cleaned if cleaned else fallback_skills(query)


async def rank_with_claude(query: str, candidates: list[Employee], top_n: int) -> list[AIResult]:
    user_content = (
        "User query:\n"
        f"{query}\n\n"
        "Candidates:\n"
        f"{json.dumps([_candidate_payload(c) for c in candidates])}\n\n"
        f"Return JSON with key 'results'. 'results' must be an array of exactly {top_n} objects. "
        "Each object must contain: employee_id (int), reason (max 140 chars). "
        "Use only candidate ids provided."
    )
    text = await _send_to_claude(user_content=user_content, max_tokens=_MAX_TOKENS_RANK)
    parsed = json.loads(_extract_json_block(text))

    by_id = {employee.employee_id: employee for employee in candidates}
    results: list[AIResult] = []
    used_ids: set[int] = set()
    for item in parsed.get("results", []):
        employee_id = item.get("employee_id")
        reason = _clean_reason(str(item.get("reason", "")))
        employee = by_id.get(employee_id)
        if employee and reason and employee_id not in used_ids:
            results.append(AIResult(employee=employee, reason=reason[:300]))
            used_ids.add(employee_id)
        if len(results) == top_n:
            break

    for employee in candidates:
        if len(results) >= top_n:
            break
        if employee.employee_id in used_ids:
            continue
        results.append(
            AIResult(
                employee=employee,
                reason="Strong profile match based on overlapping skills and projects.",
            )
        )
        used_ids.add(employee.employee_id)

    return results[:top_n]
