import re

from .models import Employee

_SCORE_NAME = 3
_SCORE_DEPT_ROLE = 2
_SCORE_TEXT = 1


def _searchable_text(employee: Employee) -> str:
    return " ".join(
        [
            employee.name,
            employee.bio,
            " ".join(employee.skills),
            " ".join(employee.projects),
        ]
    ).lower()


def _keyword_score(employee: Employee, keyword: str) -> int:
    terms = [term for term in re.split(r"\W+", keyword.lower()) if term]
    if not terms:
        return 0

    haystacks = [
        employee.name.lower(),
        " ".join(employee.skills).lower(),
        " ".join(employee.projects).lower(),
        employee.bio.lower(),
    ]

    score = 0
    for term in terms:
        score += sum(text.count(term) for text in haystacks)
    return score


def manual_search(
    employees: list[Employee],
    keyword: str | None = None,
    department: str | None = None,
    max_results: int = 30,
) -> list[Employee]:
    keyword = (keyword or "").strip().lower()
    department = (department or "").strip().lower()

    filtered = employees
    if department:
        filtered = [e for e in filtered if e.department.lower() == department]

    if not keyword:
        return filtered[:max_results]

    scored: list[tuple[int, Employee]] = []
    for employee in filtered:
        score = _keyword_score(employee, keyword)
        if score > 0:
            scored.append((score, employee))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [employee for _, employee in scored[:max_results]]


def build_shortlist(employees: list[Employee], query: str, max_candidates: int = 25) -> list[Employee]:
    tokens = [t for t in re.split(r"\W+", query.lower()) if len(t) > 1]
    if not tokens:
        return employees[:max_candidates]

    scored: list[tuple[int, Employee]] = []
    for employee in employees:
        text = _searchable_text(employee)
        score = sum(_SCORE_NAME for token in tokens if token in employee.name.lower())
        score += sum(_SCORE_DEPT_ROLE for token in tokens if token in employee.department.lower())
        score += sum(_SCORE_DEPT_ROLE for token in tokens if token in employee.role.lower())
        score += sum(_SCORE_TEXT for token in tokens if token in text)
        if score > 0:
            scored.append((score, employee))

    scored.sort(key=lambda x: x[0], reverse=True)
    shortlist = [employee for _, employee in scored[:max_candidates]]
    return shortlist if shortlist else employees[:max_candidates]
