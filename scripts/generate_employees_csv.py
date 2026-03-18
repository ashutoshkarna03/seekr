#!/usr/bin/env python3
import csv
import random
from pathlib import Path


def generate_employees(total: int = 1000) -> list[dict[str, str]]:
    random.seed(42)

    departments = {
        "Engineering": ["Software Engineer", "Backend Engineer", "Frontend Engineer", "DevOps Engineer"],
        "Product": ["Product Manager", "Technical Product Manager", "Associate Product Manager"],
        "Design": ["Product Designer", "UX Designer", "Visual Designer"],
        "Data": ["Data Analyst", "Data Scientist", "Analytics Engineer"],
        "HR": ["HR Generalist", "Talent Partner", "People Operations Specialist"],
        "Finance": ["Financial Analyst", "Finance Manager", "Accountant"],
        "Sales": ["Account Executive", "Sales Manager", "Business Development Representative"],
        "Operations": ["Operations Manager", "Program Coordinator", "Business Operations Analyst"],
    }

    skills_by_department = {
        "Engineering": ["Python", "FastAPI", "React", "TypeScript", "SQL", "Docker", "AWS", "CI/CD"],
        "Product": ["Roadmapping", "User Stories", "Stakeholder Management", "A/B Testing", "Analytics", "Jira"],
        "Design": ["Figma", "Wireframing", "Prototyping", "User Research", "Design Systems", "Accessibility"],
        "Data": ["SQL", "Python", "Pandas", "ETL", "Tableau", "Machine Learning", "Statistics"],
        "HR": ["Recruiting", "Onboarding", "Employee Relations", "Performance Management", "HRIS", "Communication"],
        "Finance": ["Financial Modeling", "Forecasting", "Budgeting", "Excel", "Reporting", "Variance Analysis"],
        "Sales": ["Negotiation", "CRM", "Prospecting", "Pipeline Management", "Presentation", "Closing"],
        "Operations": ["Process Improvement", "Project Management", "Documentation", "Vendor Management", "Automation"],
    }

    projects = [
        "Customer Portal Refresh",
        "Knowledge Base Revamp",
        "Hiring Pipeline Upgrade",
        "Data Quality Initiative",
        "Q4 Revenue Plan",
        "Expense Automation",
        "Onboarding Redesign",
        "Support Workflow Optimization",
        "Product Analytics Rollout",
        "Internal Tool Migration",
        "Retention Campaign",
        "Team Skills Matrix",
    ]

    first_names = [
        "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Jamie", "Riley", "Avery", "Cameron", "Parker",
        "Logan", "Drew", "Quinn", "Reese", "Skyler", "Dakota", "Sam", "Harper", "Robin", "Kendall",
    ]
    last_names = [
        "Patel", "Chen", "Garcia", "Johnson", "Kim", "Nguyen", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Anderson", "Thomas", "Jackson", "White", "Martin", "Lee", "Clark", "Lopez", "Hall",
    ]

    rows: list[dict[str, str]] = []
    dept_names = list(departments.keys())

    for i in range(1, total + 1):
        department = random.choice(dept_names)
        role = random.choice(departments[department])
        name = f"{random.choice(first_names)} {random.choice(last_names)}"

        employee_skills = random.sample(skills_by_department[department], k=4)
        employee_projects = random.sample(projects, k=2)

        bio = (
            f"{name} is a {role} in {department} focused on "
            f"{employee_skills[0]} and {employee_skills[1]} to support cross-team goals."
        )

        rows.append(
            {
                "employee_id": str(i),
                "name": name,
                "department": department,
                "role": role,
                "skills": ", ".join(employee_skills),
                "projects": "; ".join(employee_projects),
                "bio": bio,
            }
        )

    return rows


def main() -> None:
    output_path = Path("data/employees.csv")
    fieldnames = ["employee_id", "name", "department", "role", "skills", "projects", "bio"]

    rows = generate_employees(total=1000)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} records at {output_path.resolve()}")


if __name__ == "__main__":
    main()
