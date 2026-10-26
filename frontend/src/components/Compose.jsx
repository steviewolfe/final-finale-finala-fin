import { useEffect, useState } from 'react'

// Doherty Threshold: feedback is immediate. The steps are estimates, labelled as such.
const STEPS = [
  'Reading the posting',
  'Finding quoted evidence',
  'Scoring each profile',
  'Drafting and checking questions',
]

export default function Compose({
  posting,
  onPosting,
  maxChars,
  profiles,
  selected,
  onToggleProfile,
  notes,
  onNotes,
  maxNotes,
  samples,
  onPickSample,
  canCheck,
  busy,
  onCheck,
  error,
}) {
  const [tab, setTab] = useState('check')
  const [step, setStep] = useState(0)
  const [showNotes, setShowNotes] = useState(false)
  const over = posting.length > maxChars

  useEffect(() => {
    if (!busy) return undefined
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 3000)
    return () => clearInterval(id)
  }, [busy])

  return (
    <main className="compose">
      <div className="tabs" role="tablist" aria-label="Start">
        <button role="tab" aria-selected={tab === 'check'} className={tab === 'check' ? 'tab active' : 'tab'} onClick={() => setTab('check')}>
          Check a posting
        </button>
        <button role="tab" aria-selected={tab === 'problem'} className={tab === 'problem' ? 'tab active' : 'tab'} onClick={() => setTab('problem')}>
          The problem
        </button>
      </div>

      {tab === 'problem' ? (
        <Problem />
      ) : (
        <>
          <h1>Find out what this job really asks of you.</h1>
          <p className="lede">
            Postings often leave out what decides whether a job fits your life. This reads the posting with
            you, shows the exact words behind every claim, and drafts questions you can ask.
          </p>

          {error && <div className="banner error">{error}</div>}

          <div className="card-paper paste">
            <label htmlFor="posting" className="visually-hidden">Job posting</label>
            <textarea
              id="posting"
              value={posting}
              disabled={busy}
              onChange={(e) => onPosting(e.target.value)}
              // Paradox of the Active User: the next step is written inside the box itself.
              placeholder="Paste a job posting here. Then hover the underlined phrases to see why they matter."
            />
            <div className="paste-footer row between wrap">
              <span className="hint" style={over ? { color: 'var(--pink)' } : undefined}>
                {posting.length.toLocaleString()} / {maxChars.toLocaleString()} characters
              </span>
              <div className="row wrap">
                <select
                  aria-label="Load a sample posting"
                  defaultValue=""
                  disabled={busy}
                  onChange={(e) => {
                    if (e.target.value) onPickSample(e.target.value)
                    e.target.value = ''
                  }}
                >
                  <option value="">Load a sample</option>
                  {samples.map((s) => (
                    <option key={s} value={s}>{s.replace(/^\d+_/, '').replace(/\.txt$/, '').replace(/_/g, ' ')}</option>
                  ))}
                </select>
                <button className="primary" onClick={() => { setStep(0); onCheck() }} disabled={!canCheck || busy}>
                  {busy ? 'Checking…' : 'Check this posting'}
                </button>
              </div>
            </div>
          </div>

          {busy && (
            <ol className="steps" aria-live="polite">
              <li className="steps-title">Working through these steps (estimated)</li>
              {STEPS.map((label, i) => (
                <li key={label} className={i < step ? 'done' : i === step ? 'current' : ''}>{label}</li>
              ))}
            </ol>
          )}

          <section className="setup" aria-label="Setup">
            <div className="field">
              <span className="field-title">Compare up to 4 profiles</span>
              <div className="chips">
                {profiles.map((p) => (
                  <button
                    key={p.id}
                    className="chip-toggle"
                    aria-pressed={selected.includes(p.id)}
                    disabled={!selected.includes(p.id) && selected.length >= 4}
                    onClick={() => onToggleProfile(p.id)}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <button className="link-btn" aria-expanded={showNotes} onClick={() => setShowNotes((v) => !v)}>
              {showNotes ? 'Hide private notes' : 'Add private notes (optional)'}
            </button>
            {showNotes && (
              <div className="field">
                <label htmlFor="notes-compose">Private notes</label>
                <input
                  id="notes-compose"
                  type="password"
                  value={notes}
                  maxLength={maxNotes}
                  placeholder="e.g. I have ADHD and two kids"
                  autoComplete="off"
                  onChange={(e) => onNotes(e.target.value)}
                />
                <span className="hint">Used only to check drafted questions. Not saved or logged.</span>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  )
}

function Problem() {
  return (
    <section className="problem" aria-labelledby="problem-title">
      <p className="eyebrow">Before you apply</p>
      <h2 id="problem-title">Find out what this job really asks of you.</h2>
      <p className="lede">
        Job posts often leave out the things that decide whether a job fits your life: whether the hours are
        steady, how fast the pace is, what happens when you are sick or a child is ill, and whether you will be
        able to focus. So you end up guessing. Asking can feel risky, especially when your answer might be used
        against you.
      </p>
      <p className="lede">
        This tool reads the posting with you. It shows every claim next to the exact words it came from, explains
        what that means for someone like you, and drafts questions you can ask without sharing anything private.
        Your private notes are used only to check those questions. They are not saved or logged.
      </p>
      <p className="intro-close">Nothing here decides for you. You know your life best.</p>
    </section>
  )
}
