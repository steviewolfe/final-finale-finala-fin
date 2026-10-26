// Predict before you see: the reader guesses first, then the posting answers.
const OPTIONS = [
  { id: 'few', label: '0 to 2 of 9', test: (n) => n <= 2 },
  { id: 'some', label: '3 to 5 of 9', test: (n) => n >= 3 && n <= 5 },
  { id: 'many', label: '6 or more of 9', test: (n) => n >= 6 },
]

export default function PredictCard({ result, prediction, onPredict }) {
  // A category counts as "vague or unmentioned" when it has no clear evidence.
  const unclear = result.gaps.length
  const actual = OPTIONS.find((o) => o.test(unclear))
  const guess = OPTIONS.find((o) => o.id === prediction)

  return (
    <section className="predict card-paper" aria-labelledby="predict-title">
      <p className="eyebrow">Before you look</p>
      <h3 id="predict-title">How many of the 9 areas do you think this posting leaves vague or unmentioned?</h3>

      {!guess ? (
        <div className="predict-options" role="group" aria-label="Your guess">
          {OPTIONS.map((o) => (
            <button key={o.id} className="predict-btn" onClick={() => onPredict(o.id)}>
              {o.label}
            </button>
          ))}
        </div>
      ) : (
        <p className="reveal-line">
          You guessed <strong>{guess.label}</strong>. This posting leaves <strong>{unclear} of 9</strong> areas
          vague or unmentioned.{' '}
          {guess.id === actual.id ? 'Your instinct was right.' : 'It may be clearer, or vaguer, than it first looks.'}
        </p>
      )}
    </section>
  )
}
