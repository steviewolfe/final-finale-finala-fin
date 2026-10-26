import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Type system: grotesk display, serif body, mono micro-copy (all open-licence, SIL OFL).
import '@fontsource/schibsted-grotesk/400.css'
import '@fontsource/schibsted-grotesk/700.css'
import '@fontsource/newsreader/400.css'
import '@fontsource/newsreader/700.css'
import '@fontsource/space-mono/400.css'
import '@fontsource/space-mono/700.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
