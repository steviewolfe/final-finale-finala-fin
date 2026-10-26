import { useEffect } from 'react'

// Options: only what does not belong on the main screen. Profiles, notes, and
// samples live on the compose screen. This drawer holds the question owner and the budget.
export default function OptionsDrawer({ profiles, selected, primary, onPrimary, budget, onResetBudget, onClose }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-modal="true" aria-label="Options">
        <header>
          <h2>Options</h2>
          <button className="ghost" onClick={onClose}>Close</button>
        </header>

        <div className="field">
          <label htmlFor="primary">Write the questions for</label>
          <select id="primary" value={primary} onChange={(e) => onPrimary(e.target.value)}>
            {profiles
              .filter((p) => selected.includes(p.id))
              .map((p) => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
          </select>
          <span className="hint">Questions are drafted for this profile. Scores are shown for every profile you chose.</span>
        </div>

        <div className="field">
          <span className="field-title">Usage this session</span>
          <span className="hint">
            {budget.used.toLocaleString()} of {budget.limit.toLocaleString()} tokens used. The session stops at this limit.
          </span>
          <div>
            <button className="ghost" onClick={onResetBudget}>Reset usage</button>
          </div>
        </div>
      </aside>
    </>
  )
}
