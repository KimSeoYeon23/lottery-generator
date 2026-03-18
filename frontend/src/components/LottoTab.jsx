import NumberBall from './NumberBall';

export default function LottoTab({ results, selected, onSelect, onGenerate, onRegenerate, loading }) {
  return (
    <section>
      <div className="generate-controls">
        <button
          className={`btn-primary${loading ? ' loading' : ''}`}
          onClick={onGenerate}
          disabled={loading}
        >
          번호 생성
        </button>
        {results.length > 0 && (
          <button className="btn-secondary" onClick={onRegenerate} disabled={loading}>
            다시 생성
          </button>
        )}
      </div>

      <div>
        {results.map((r, i) => {
          const isSelected = selected.some(
            (s) => JSON.stringify(s.numbers) === JSON.stringify(r.numbers)
          );
          return (
            <div
              key={i}
              className={`number-card${isSelected ? ' selected' : ''}`}
              onClick={() => onSelect(r)}
            >
              <div className="card-header">
                <span className="strategy-name">{r.strategy}</span>
                <span className="card-meta">합 {r.sum} · {r.odd_even}</span>
              </div>
              <div className="ball-row">
                {r.numbers.map((n) => (
                  <NumberBall key={n} n={n} />
                ))}
              </div>
              {isSelected && (
                <div className="card-select-indicator">✓</div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
