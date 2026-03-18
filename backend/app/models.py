from pydantic import BaseModel, Field


class Employee(BaseModel):
    employee_id: int
    name: str
    department: str
    role: str
    skills: list[str]
    projects: list[str]
    bio: str


class ManualSearchRequest(BaseModel):
    keyword: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=80)


class AISearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=300)
    top_n: int = Field(default=3, ge=3, le=5)
    required_skills: list[str] = Field(default_factory=list)


class AISkillsRequest(BaseModel):
    query: str = Field(min_length=2, max_length=300)


class AISkillsResponse(BaseModel):
    required_skills: list[str]


class ManualSearchResponse(BaseModel):
    results: list[Employee]


class AIResult(BaseModel):
    employee: Employee
    reason: str


class AISearchResponse(BaseModel):
    results: list[AIResult]
