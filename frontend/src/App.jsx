import { useMemo, useState } from 'react'
import { fetchAiSearch, fetchAiSkills } from './api'

const PAGE_SIZE = 5

function AIResultsTable({ rows }) {
  return (
    <table className="results-table">
      <thead>
        <tr>
          <th>Employee ID</th>
          <th>Name</th>
          <th>Department</th>
          <th>Role</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((item) => (
          <tr key={`a-${item.employee.employee_id}`}>
            <td>{item.employee.employee_id}</td>
            <td>{item.employee.name}</td>
            <td>{item.employee.department}</td>
            <td>{item.employee.role}</td>
            <td>{item.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function App() {
  const [logoFailed, setLogoFailed] = useState(false)

  const [query, setQuery] = useState('')
  const [topN, setTopN] = useState(3)

  const [requiredSkills, setRequiredSkills] = useState([])
  const [newSkill, setNewSkill] = useState('')
  const [editingIndex, setEditingIndex] = useState(-1)
  const [editingValue, setEditingValue] = useState('')

  const [results, setResults] = useState([])
  const [page, setPage] = useState(1)

  const [loadingSkills, setLoadingSkills] = useState(false)
  const [loadingResults, setLoadingResults] = useState(false)
  const [error, setError] = useState('')

  const [stage, setStage] = useState('query')

  const resultsTitle = useMemo(() => {
    if (!results.length) return 'No matching employees yet.'
    return `Matching employees (${results.length})`
  }, [results])

  const totalPages = Math.max(1, Math.ceil(results.length / PAGE_SIZE))
  const pagedRows = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const onQuerySubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      setError('Please enter a query.')
      return
    }

    setLoadingSkills(true)
    setError('')
    setResults([])
    setPage(1)

    try {
      const data = await fetchAiSkills(query.trim())
      const skills = data.required_skills || []
      setRequiredSkills(skills)
      setNewSkill('')
      setEditingIndex(-1)
      setEditingValue('')
      setStage('skills')
    } catch (err) {
      setError(err.message)
      setStage('query')
    } finally {
      setLoadingSkills(false)
    }
  }

  const onApproveSkills = async (e) => {
    e.preventDefault()

    const approvedSkills = requiredSkills
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean)

    setLoadingResults(true)
    setError('')

    try {
      const data = await fetchAiSearch(query.trim(), Number(topN), approvedSkills)
      setResults(data.results || [])
      setPage(1)
      setStage('results')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingResults(false)
    }
  }

  const removeSkill = (indexToRemove) => {
    setRequiredSkills((prev) => prev.filter((_, index) => index !== indexToRemove))
    if (editingIndex === indexToRemove) {
      setEditingIndex(-1)
      setEditingValue('')
    }
  }

  const startEditSkill = (index) => {
    setEditingIndex(index)
    setEditingValue(requiredSkills[index] || '')
  }

  const saveEditedSkill = () => {
    const value = editingValue.trim().toLowerCase()
    if (editingIndex < 0) return

    if (!value) {
      removeSkill(editingIndex)
      return
    }

    setRequiredSkills((prev) =>
      prev.map((skill, index) => (index === editingIndex ? value : skill))
    )
    setEditingIndex(-1)
    setEditingValue('')
  }

  const addSkill = () => {
    const value = newSkill.trim().toLowerCase()
    if (!value) return
    setRequiredSkills((prev) => (prev.includes(value) ? prev : [...prev, value]))
    setNewSkill('')
  }

  return (
    <main className="app-layout single-page">
      <aside className="sidebar">
        <div className="brand-wrap">
          {!logoFailed ? (
            <img
              src="/skillsync-logo.png"
              alt="SkillSync logo"
              className="brand-logo"
              onError={() => setLogoFailed(true)}
            />
          ) : (
            <div className="brand-fallback">SS</div>
          )}
          <div>
            <h1 className="brand-title">Seekr</h1>
            <p className="brand-subtitle">Workplace Knowledge Radar</p>
          </div>
        </div>

        <div className="sidebar-footer">
          <button type="button" className="menu-item logout">Logout</button>
        </div>
      </aside>

      <section className="content">
        <div className="panel">
          <p className="section-subtitle">Find co-workers with the skills you need.</p>

          <form onSubmit={onQuerySubmit} className="form">
            <input
              type="text"
              placeholder="Type a technology, tool, or problem and we'll recommend the best people."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <input
              type="number"
              min="3"
              max="5"
              value={topN}
              onChange={(e) => setTopN(Math.min(5, Math.max(3, Number(e.target.value) || 3)))}
              className="topn"
              aria-label="Top N results"
            />
            <button type="submit" disabled={loadingSkills || loadingResults}>
              {loadingSkills ? 'Extracting...' : 'Search'}
            </button>
          </form>

          {stage !== 'query' && (
            <form onSubmit={onApproveSkills} className="skills-form">
              <label className="subtitle">
                Required skill keywords (editable)
              </label>
              <div className="skill-chip-list">
                {requiredSkills.map((skill, index) => (
                  <div
                    key={`${skill}-${index}`}
                    className="skill-chip"
                    onDoubleClick={() => startEditSkill(index)}
                    title="Double-click to edit"
                  >
                    {editingIndex === index ? (
                      <input
                        autoFocus
                        className="chip-edit-input"
                        value={editingValue}
                        onChange={(e) => setEditingValue(e.target.value)}
                        onBlur={saveEditedSkill}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault()
                            saveEditedSkill()
                          }
                          if (e.key === 'Escape') {
                            setEditingIndex(-1)
                            setEditingValue('')
                          }
                        }}
                      />
                    ) : (
                      <span>{skill}</span>
                    )}
                    {editingIndex !== index && (
                      <button
                        type="button"
                        className="chip-remove"
                        onClick={() => removeSkill(index)}
                        aria-label={`Remove ${skill}`}
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <div className="add-skill-row">
                <input
                  type="text"
                  value={newSkill}
                  placeholder="Add another skill"
                  onChange={(e) => setNewSkill(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addSkill()
                    }
                  }}
                />
                <button type="button" className="ok-btn" onClick={addSkill}>Add</button>
              </div>
              <p className="hint">Tip: double-click a skill bubble to edit.</p>
              <div className="skills-actions">
                <button type="submit" disabled={loadingResults} className="ok-btn">
                  {loadingResults ? '...' : 'OK'}
                </button>
              </div>
            </form>
          )}

          {error && <p className="error">{error}</p>}

          {stage === 'results' && (
            <>
              <p className="subtitle">{resultsTitle}</p>
              {pagedRows.length > 0 && <AIResultsTable rows={pagedRows} />}
              {results.length > PAGE_SIZE && (
                <div className="pagination">
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </button>
                  <span>Page {page} of {totalPages}</span>
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </main>
  )
}
