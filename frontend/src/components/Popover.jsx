import { createPortal } from 'react-dom'

// Renders a tooltip in a portal, so the posting's text styling never leaks into it.
// Positioning comes from the parent's useFloating, passed in as setFloating and style.
export default function Popover({ id, setFloating, style, popRef, onEnter, onLeave, onKeyDown, children }) {
  return createPortal(
    <div
      ref={(node) => {
        setFloating(node)
        popRef.current = node
      }}
      style={style}
      role="tooltip"
      id={id}
      className="popover"
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      onKeyDown={onKeyDown}
    >
      {children}
    </div>,
    document.body,
  )
}
