import { useState } from 'react'
import { SIGNAL_NAME, niceCategory } from '../labels.js'

// A category with no clear evidence, and the question to ask about it.
// Zeigarnik Effect: an open card stays prominent until the question is copied.
export default function GapCard({ gap, copied, onCopied, cardRef }) {
  const unclear = gap.state === 'unclear'
  const [showWhy, setShowWhy] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(gap.question)
    } catch {
      // Clipboard can be blocked; still mark it so the reader keeps moving.
    }
    onCopied(gap.category)
  }

  return (
    <article ref={cardRef} className={`card gap ${copied ? 'is-done' : ''}`} style={{ '--accent': 'var(--ink-data)' }}>
      <div className="row between">
        <span className="signal signal-gap">{SIGNAL_NAME.gap}</span>
        <span className="muted small">{niceCategory(gap.category)}</span>
      </div>
      <p className="why">
        {unclear
          ? 'The posting only gives vague wording here, so ask directly.'
          : 'The posting does not mention this. Ask directly.'}
      </p>

      {gap.question && (
        <>
          <p className="gap-q">{gap.question}</p>
          <div className="row between">
            {gap.question_rewritten ? (
              <button className="badge-btn" aria-expanded={showWhy} onClick={() => setShowWhy((v) => !v)}>
                Changed to protect your notes
              </button>
            ) : (
              <span />
            )}
            <button className="copy-btn" onClick={copy} disabled={copied}>
              {copied ? 'Copied' : 'Copy question'}
            </button>
          </div>
        </>
      )}
      {showWhy && gap.question_original && (
        <div className="why-changed">
          <p className="small muted">First draft, with private details removed:</p>
          <p className="gap-q-old">{gap.question_original}</p>
          <p className="small muted">The question above was rewritten so it asks for the same information without revealing anything private.</p>
        </div>
      )}
      {!gap.question && gap.question_dropped && (
        <p className="muted small" style={{ marginTop: 8 }}>
          One question was dropped for privacy.
        </p>
      )}
    </article>
  )
}
