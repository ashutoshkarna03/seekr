const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchManualSearch({ keyword, department }) {
  const response = await fetch(`${API_BASE}/search/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      keyword: keyword.trim() || null,
      department: department.trim() || null,
    }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'Manual search failed')
  }
  return response.json()
}

export async function fetchAiSkills(query) {
  const response = await fetch(`${API_BASE}/search/ai/skills`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'AI skill extraction failed')
  }

  return response.json()
}

export async function fetchAiSearch(query, topN = 3, requiredSkills = []) {
  const response = await fetch(`${API_BASE}/search/ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_n: topN, required_skills: requiredSkills }),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'AI search failed')
  }

  return response.json()
}
