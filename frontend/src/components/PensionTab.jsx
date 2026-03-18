export default function PensionTab({ results, onGenerate, onRegenerate, loading }) {
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
        {results.map((r, i) => (
          <div key={i} className="number-card" style={{ cursor: 'default' }}>
            <div className="card-header">
              <span className="strategy-name">{r.strategy}</span>
            </div>
            <div className="pension-display">
              <div className="pension-group">
                {r.group}<span>조</span>
              </div>
              {r.numbers.map((d, j) => (
                <div key={j} className="pension-digit">{d}</div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
