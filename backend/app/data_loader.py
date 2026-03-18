import csv
import re
from pathlib import Path

from .models import Employee


def _split_multi_value(value: str) -> list[str]:
    if not value:
        return []
    # Accept both comma-separated and semicolon-separated values.
    return [item.strip() for item in re.split(r"[;,]", value) if item.strip()]


def _clean_name(value: str) -> str:
    # Remove accidental numeric suffixes like "John Smith 42".
    return re.sub(r"\s+\d+$", "", value).strip()


def load_employees(csv_path: str) -> list[Employee]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    employees: list[Employee] = []
    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader, start=1):
            raw_employee_id = (row.get("employee_id") or "").strip()
            employee_id = int(raw_employee_id) if raw_employee_id.isdigit() else idx
            employees.append(
                Employee(
                    employee_id=employee_id,
                    name=_clean_name(row.get("name", "")),
                    department=row.get("department", "").strip(),
                    role=row.get("role", "").strip(),
                    skills=_split_multi_value(row.get("skills", "")),
                    projects=_split_multi_value(row.get("projects", "")),
                    bio=row.get("bio", "").strip(),
                )
            )
    return employees
