// Thin wrappers around the FastAPI backend. Requests go to the same origin,
// and Vite's dev server proxies /api to the backend during development.

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return body
}

export const getProfiles = () => request('/api/profiles')
export const getSamples = () => request('/api/samples')
export const getSample = (name) => request(`/api/samples/${encodeURIComponent(name)}`)
export const getBudget = () => request('/api/budget')
export const resetBudget = () => request('/api/budget/reset', { method: 'POST' })
export const analyze = (payload) =>
  request('/api/analyze', { method: 'POST', body: JSON.stringify(payload) })
export const getLimits = () => request('/api/limits')
