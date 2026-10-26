// Top bar. Jakob's Law: brand left, actions right. Cognitive Load: only what the
// reader needs here. Zeigarnik Effect: the open-question count is always visible.
export default function TopBar({ title, openCount, view, onEdit, onOptions, onDetails }) {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">B</span>
        <span>Between the Lines</span>
      </div>
      <div className="doc-title" title={title}>{title}</div>
      <div className="topbar-actions">
        {view === 'review' && openCount > 0 && (
          <span className="pill open" title="Drafted questions you have not copied yet">
            {openCount} open {openCount === 1 ? 'question' : 'questions'}
          </span>
        )}
        {view === 'review' && (
          <>
            <button className="icon-btn" onClick={onEdit}>Edit posting</button>
            <button className="icon-btn" onClick={onDetails}>Run details</button>
          </>
        )}
        <button className="icon-btn" onClick={onOptions}>Options</button>
      </div>
    </header>
  )
}
