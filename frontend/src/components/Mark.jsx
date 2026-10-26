import { useEffect, useRef, useState } from 'react'
import { autoUpdate, flip, offset, shift, useFloating } from '@floating-ui/react-dom'
import Popover from './Popover.jsx'
import { SIGNAL_NAME, niceCategory, scoreLine } from '../labels.js'

// One underlined span of the posting. Hover or focus opens its explanation.
export default function Mark({
  segment,
  items,
  lens,
  isActive,
  pulse,
  uid,
  lit = true,
  onSelect,
  registerMark,
  onLocateCard,
}) {
  const [open, setOpen] = useState(false)
  const markRef = useRef(null)
  const popRef = useRef(null)
  const { refs, floatingStyles } = useFloating({
    placement: 'top',
    middleware: [offset(10), flip({ padding: 8 }), shift({ padding: 8 })],
    whileElementsMounted: autoUpdate,
  })
  const closeTimer = useRef(null)
  const openTimer = useRef(null)
  const tipId = `tip-${uid}`
  const isFlagged = segment.kind === 'flagged'

  useEffect(() => () => {
    clearTimeout(closeTimer.current)
    clearTimeout(openTimer.current)
  }, [])

  const keepOpen = () => clearTimeout(closeTimer.current)
  const scheduleClose = () => {
    clearTimeout(closeTimer.current)
    closeTimer.current = setTimeout(() => setOpen(false), 140)
  }
  const close = () => {
    clearTimeout(closeTimer.current)
    setOpen(false)
  }

  const onBlur = (e) => {
    if (popRef.current && popRef.current.contains(e.relatedTarget)) return
    setOpen(false)
  }

  const onKeyDown = (e) => {
    if (e.key === 'Escape') {
      close()
      markRef.current?.focus()
    }
  }

  const classes = [
    'seg',
    `seg-${segment.kind}`,
    isActive ? 'is-active' : '',
    pulse ? 'is-pulse' : '',
    lit ? '' : 'is-unlit',
  ].filter(Boolean).join(' ')

  return (
    <>
      <mark
        ref={(node) => {
          markRef.current = node
          refs.setReference(node)
          if (node) registerMark(segment.ids, node)
        }}
        className={classes}
        data-ids={segment.ids.join(',')}
        tabIndex={0}
        aria-describedby={open ? tipId : undefined}
        onMouseEnter={() => {
          keepOpen()
          // Flow: wait a beat so tooltips do not pop up while the pointer is only passing over.
          openTimer.current = setTimeout(() => setOpen(true), 250)
        }}
        onMouseLeave={() => {
          clearTimeout(openTimer.current)
          scheduleClose()
        }}
        onFocus={() => setOpen(true)}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
        onClick={() => {
          if (segment.ids.length) onSelect(segment.ids[0])
        }}
      >
        {segment.text}
      </mark>

      {open && (
        <Popover
          id={tipId}
          setFloating={refs.setFloating}
          style={floatingStyles}
          popRef={popRef}
          onEnter={keepOpen}
          onLeave={scheduleClose}
          onKeyDown={onKeyDown}
        >
          {isFlagged ? (
            <FlaggedTip text={segment.why} onClose={close} />
          ) : (
            items.map((item, i) => (
              <ItemTip
                key={item.id}
                item={item}
                lens={lens}
                divider={i > 0}
                onLocate={() => {
                  close()
                  onLocateCard(item.id)
                }}
                onClose={close}
              />
            ))
          )}
        </Popover>
      )}
    </>
  )
}

function FlaggedTip({ text, onClose }) {
  return (
    <>
      <h4>
        <span className="signal signal-flagged">{SIGNAL_NAME.flagged}</span>
      </h4>
      <p>{text}</p>
      <div className="actions">
        <button onClick={onClose}>Close</button>
      </div>
    </>
  )
}

function ItemTip({ item, lens, divider, onLocate, onClose }) {
  const impact = item.impact.find((x) => x.profile_id === lens) || item.impact[0]
  return (
    <div style={divider ? { marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--rule)' } : undefined}>
      <h4>
        <span className={`signal signal-${item.signal}`}>{SIGNAL_NAME[item.signal]}</span>
        <span className="muted small">{niceCategory(item.category)}</span>
      </h4>
      <div className="section-label">What it says</div>
      <p>{item.note}</p>
      <div className="section-label">Why it matters</div>
      <p>{item.why}</p>
      {impact && (
        <>
          <div className="section-label">For this profile</div>
          <p>{impact.profile_why}</p>
          <p className="muted small" style={{ marginTop: 6 }}>{scoreLine(impact, item.category)}</p>
        </>
      )}
      <div className="actions">
        <button className="go" onClick={onLocate}>Show card</button>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  )
}
