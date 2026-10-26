// Shared display helpers. Keep copy here so components stay consistent.

export const niceCategory = (c) => c.replace(/_/g, ' ').replace(/^./, (s) => s.toUpperCase())

export const SIGNAL_NAME = {
  negative: 'Restriction',
  unclear: 'Unclear',
  positive: 'Benefit',
  flagged: 'Ignored',
  gap: 'Not mentioned',
}

export const BAND_COLOUR = {
  'Good fit': 'var(--mustard)',
  Mixed: 'var(--teal)',
  Concern: 'var(--pink)',
  'Limited evidence': '#98a2b3',
  'Not enough evidence': '#98a2b3',
}

export function scoreLine(impact, category) {
  const pct = Math.round(impact.weight * 100)
  return `Counts as ${impact.value}/100 in ${niceCategory(category)}, which is ${pct}% of this profile's score.`
}
