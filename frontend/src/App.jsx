import { useEffect, useRef, useState } from 'react'
import TopBar from './components/TopBar.jsx'
import Compose from './components/Compose.jsx'
import Document from './components/Document.jsx'
import Rail from './components/Rail.jsx'
import PredictCard from './components/PredictCard.jsx'
import ExploreGrid from './components/ExploreGrid.jsx'
import OptionsDrawer from './components/OptionsDrawer.jsx'
import DetailsDrawer from './components/DetailsDrawer.jsx'
import * as api from './api.js'

const FALLBACK_LIMITS = { max_posting_chars: 12000, max_notes_chars: 500 }
const MAX_COMPARE = 4 // keeps the side-by-side view readable; the server enforces the same cap

const titleFromSample = (name) =>
  name.replace(/^\d+_/, '').replace(/\.txt$/, '').replace(/_/g, ' ')

export default function App() {
  const [view, setView] = useState('compose')
  const [profiles, setProfiles] = useState([])
  const [selected, setSelected] = useState([])
  const [primary, setPrimary] = useState('')
  const [notes, setNotes] = useState('')
  const [posting, setPosting] = useState('')
  const [docTitle, setDocTitle] = useState('Untitled posting')
  const [samples, setSamples] = useState([])
  const [budget, setBudget] = useState({ used: 0, limit: 0 })
  const [limits, setLimits] = useState(FALLBACK_LIMITS)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [drawer, setDrawer] = useState(null)
  const [copied, setCopied] = useState([])

  const [lens, setLens] = useState('')
  const [filter, setFilter] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [pulseId, setPulseId] = useState(null)

  // Choose your path, predict first, and scroll reveal
  const [mode, setMode] = useState('guided') // 'guided' | 'explore'
  const [prediction, setPrediction] = useState(null)
  const [seen, setSeen] = useState([]) // evidence ids the reader has reached
  const [exploreOpen, setExploreOpen] = useState(false)
  const reduceMotion = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

  const marksRef = useRef({})
  const cardRefs = useRef({})

  useEffect(() => {
    api.getProfiles().then((ps) => {
      setProfiles(ps)
      setSelected(ps.slice(0, MAX_COMPARE).map((p) => p.id))
      setPrimary(ps[0]?.id || '')
      setLens(ps[0]?.id || '')
    }).catch((e) => setError(e.message))
    api.getSamples().then(setSamples).catch(() => {})
    api.getBudget().then(setBudget).catch(() => {})
    api.getLimits().then(setLimits).catch(() => {})
  }, [])

  // Scroll reveal (guided mode): an underline lights up once it is half on screen.
  useEffect(() => {
    if (view !== 'review' || !result || mode !== 'guided' || reduceMotion) return undefined
    const io = new IntersectionObserver(
      (entries) => {
        const ids = []
        for (const e of entries) {
          if (!e.isIntersecting) continue
          io.unobserve(e.target)
          for (const raw of (e.target.dataset.ids || '').split(',')) {
            if (raw !== '') ids.push(Number(raw))
          }
        }
        if (ids.length) setSeen((cur) => [...new Set([...cur, ...ids])])
      },
      { threshold: 0.5 },
    )
    document.querySelectorAll('mark.seg[data-ids]').forEach((n) => io.observe(n))
    return () => io.disconnect()
  }, [view, result, mode, reduceMotion])

  // Lit ids: null means every underline is lit (explore mode, or reduced motion).
  const litIds = mode === 'explore' || reduceMotion ? null : new Set(seen)

  // The lens falls back to the first profile in the result if the chosen one is not in it.
  const activeLens = result?.profile_ids?.includes(lens) ? lens : result?.profile_ids?.[0] || ''

  const toggleProfile = (id) => {
    setSelected((cur) => {
      if (cur.includes(id)) {
        const next = cur.filter((x) => x !== id)
        if (!next.includes(primary) && next.length) setPrimary(next[0])
        return next
      }
      // Ignore a fifth profile: the cap is shown on the chips, so this is only a safety net.
      return cur.length >= MAX_COMPARE ? cur : [...cur, id]
    })
  }

  const pickSample = async (name) => {
    try {
      const { text } = await api.getSample(name)
      setPosting(text)
      setDocTitle(titleFromSample(name))
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }

  const check = async () => {
    setBusy(true)
    setError('')
    // Postel's Law: accept messy paste (Windows line endings, stray spaces) and tidy it quietly.
    const cleaned = posting.replace(/\r\n?/g, '\n').replace(/[ \t]+\n/g, '\n').trim()
    try {
      const data = await api.analyze({ posting: cleaned, profiles: selected, primary, notes })
      setResult(data)
      setBudget(data.budget)
      setSelectedId(null)
      setFilter(null)
      setCopied([])
      setPrediction(null)
      setSeen([])
      setExploreOpen(false)
      setView('review')
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  const resetBudget = async () => {
    setBudget(await api.resetBudget())
    setResult(null)
    setView('compose')
  }

  const flashPulse = (id) => {
    setPulseId(id)
    setTimeout(() => setPulseId((cur) => (cur === id ? null : cur)), 900)
  }

  const scrollCardTo = (id) => {
    cardRefs.current[`e${id}`]?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }

  // Selecting from the rail or the explore grid: highlight the matching underline.
  const selectCard = (id) => {
    setSelectedId(id)
    flashPulse(id)
    marksRef.current[id]?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }

  // Selecting an underline: highlight and scroll to the matching card.
  const selectMark = (id) => {
    setSelectedId(id)
    flashPulse(id)
    scrollCardTo(id)
  }

  const registerMark = (ids, node) => {
    for (const id of ids) {
      if (!marksRef.current[id]) marksRef.current[id] = node
    }
  }

  const markCopied = (category) => setCopied((cur) => (cur.includes(category) ? cur : [...cur, category]))

  const openCount = result ? result.gaps.filter((g) => g.question && !copied.includes(g.category)).length : 0

  const canCheck =
    posting.trim().length > 0 && posting.length <= limits.max_posting_chars && selected.length > 0

  // Ids in the order they appear in the posting, so cards read top to bottom.
  const orderedIds = (() => {
    if (!result) return []
    const seenIds = []
    for (const seg of result.segments) {
      for (const id of seg.ids) if (!seenIds.includes(id)) seenIds.push(id)
    }
    for (const e of result.evidence) if (!seenIds.includes(e.id)) seenIds.push(e.id)
    return seenIds
  })()

  const visibleIds = new Set(
    (result?.evidence || [])
      .filter((e) => filter === null || e.category === filter)
      .map((e) => e.id),
  )

  const readProgress =
    result && mode === 'guided' && !reduceMotion
      ? { seen: seen.filter((id) => result.evidence.some((e) => e.id === id)).length, total: result.evidence.length }
      : null

  return (
    <div className="app">
      <TopBar
        title={view === 'review' ? docTitle : 'Between the Lines'}
        openCount={openCount}
        view={view}
        onEdit={() => setView('compose')}
        onOptions={() => setDrawer('options')}
        onDetails={() => setDrawer('details')}
      />

      {view === 'compose' && (
        <Compose
          posting={posting}
          onPosting={setPosting}
          maxChars={limits.max_posting_chars}
          profiles={profiles}
          selected={selected}
          onToggleProfile={toggleProfile}
          notes={notes}
          onNotes={setNotes}
          maxNotes={limits.max_notes_chars}
          samples={samples}
          onPickSample={pickSample}
          canCheck={canCheck}
          busy={busy}
          onCheck={check}
          error={error}
        />
      )}

      {view === 'review' && result && (
        <div className="review">
          <main className="doc-pane">
            {result.error && <div className="banner error">{result.error}</div>}

            {mode === 'guided' && (
              <PredictCard result={result} prediction={prediction} onPredict={setPrediction} />
            )}

            {/* Choose your path: guided reveal, or everything at once */}
            <div className="mode-switch" role="group" aria-label="How to read">
              <button aria-pressed={mode === 'guided'} onClick={() => setMode('guided')}>Guided</button>
              <button
                aria-pressed={mode === 'explore'}
                onClick={() => {
                  setMode('explore')
                  setExploreOpen(true)
                }}
              >
                Explore
              </button>
            </div>

            <Document
              segments={result.segments}
              items={result.evidence}
              lens={activeLens}
              visibleIds={visibleIds}
              litIds={litIds}
              selectedId={selectedId}
              pulseId={pulseId}
              onSelect={selectMark}
              registerMark={registerMark}
              onLocateCard={selectCard}
            />
            <p className="meta-line">
              {result.cache_hit
                ? 'Same posting as before, so the scores match exactly.'
                : 'Scores are calculated from the quotes above.'}
            </p>

            {mode === 'guided' && !exploreOpen && (
              <button className="explore-toggle" onClick={() => setExploreOpen(true)}>
                Explore all evidence
              </button>
            )}
            {exploreOpen && (
              <ExploreGrid result={result} lens={activeLens} selectedId={selectedId} onSelect={selectCard} />
            )}
          </main>
          <Rail
            result={result}
            lens={activeLens}
            onLens={setLens}
            filter={filter}
            onFilter={setFilter}
            selectedId={selectedId}
            pulseId={pulseId}
            onSelectCard={selectMark}
            onLocate={selectCard}
            cardRefs={cardRefs}
            orderedIds={orderedIds}
            copied={copied}
            onCopied={markCopied}
            readProgress={readProgress}
          />
          <a className="jump-rail" href="#rail">See suggestions ({result.evidence.length + result.gaps.length})</a>
        </div>
      )}

      {drawer === 'options' && (
        <OptionsDrawer
          profiles={profiles}
          selected={selected}
          primary={primary}
          onPrimary={setPrimary}
          budget={budget}
          onResetBudget={resetBudget}
          onClose={() => setDrawer(null)}
        />
      )}
      {drawer === 'details' && result && (
        <DetailsDrawer result={result} onClose={() => setDrawer(null)} />
      )}
    </div>
  )
}
