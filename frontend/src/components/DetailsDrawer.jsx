import { useEffect } from 'react'
import { niceCategory } from '../labels.js'

// Run details: token metrics, pipeline trace, ignored text, rejected quotes, token table.
export default function DetailsDrawer({ result, onClose }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const u = result.usage
  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-modal="true" aria-label="Run details">
        <header>
          <h2>Run details</h2>
          <button className="ghost" onClick={onClose}>Close</button>
        </header>

        <div className="metrics">
          <Metric label="LLM calls" value={u.calls} />
          <Metric label="Est. cost (USD)" value={`$${u.cost_usd.toFixed(4)}`} />
          <Metric label="Tokens in" value={u.input_tokens.toLocaleString()} />
          <Metric label="Tokens out" value={u.output_tokens.toLocaleString()} />
        </div>

        <section>
          <div className="section-title">Pipeline trace</div>
          <ul className="plain">
            {result.trace.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </section>

        {result.flagged.length > 0 && (
          <div className="banner warn">
            <strong>Ignored instruction-like text in the posting:</strong>
            <ul className="plain">
              {result.flagged.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          </div>
        )}

        {result.rejected.length > 0 && (
          <section>
            <div className="section-title">Rejected evidence</div>
            <table>
              <thead><tr><th>Category</th><th>Quote</th><th>Reason</th></tr></thead>
              <tbody>
                {result.rejected.map((r, i) => (
                  <tr key={i}>
                    <td>{niceCategory(r.category)}</td>
                    <td>{r.quote}</td>
                    <td>{r.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {u.rows.length > 0 && (
          <section>
            <div className="section-title">Token usage by agent</div>
            <table>
              <thead><tr><th>Agent</th><th>In</th><th>Cached</th><th>Out</th><th>USD</th></tr></thead>
              <tbody>
                {u.rows.map((r, i) => (
                  <tr key={i}>
                    <td>{r.agent}</td>
                    <td>{r.input_tokens}</td>
                    <td>{r.cached_input_tokens}</td>
                    <td>{r.output_tokens}</td>
                    <td>{r.cost_usd}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </aside>
    </>
  )
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <div className="metric-value">{value}</div>
      <div className="muted small">{label}</div>
    </div>
  )
}
