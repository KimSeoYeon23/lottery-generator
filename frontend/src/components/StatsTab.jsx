export default function StatsTab({ stats }) {
  if (!stats) {
    return <p className="placeholder">번호를 생성하면 통계가 표시됩니다.</p>;
  }

  const maxLotto = Math.max(...stats.lotto.top10.map((x) => x.count));

  return (
    <div>
      <div className="stat-section">
        <h3>🔥 로또 역대 TOP 10</h3>
        {stats.lotto.top10.map((x) => (
          <div key={x.number} className="stat-bar-row">
            <span className="stat-label">{x.number}번</span>
            <div className="stat-bar">
              <div
                className="stat-bar-fill hot"
                style={{ width: `${((x.count / maxLotto) * 100).toFixed(1)}%` }}
              />
            </div>
            <span className="stat-count">{x.count}회</span>
          </div>
        ))}
      </div>

      <div className="stat-section">
        <h3>❄️ 가장 적게 나온 번호</h3>
        <div className="stat-grid">
          {stats.lotto.bottom5.map((x) => (
            <div key={x.number} className="stat-chip">
              <span className="num">{x.number}번</span>
              <span className="cnt">{x.count}회</span>
            </div>
          ))}
        </div>
      </div>

      <div className="stat-section">
        <h3>🔴 최근 핫넘버 / 🔵 콜드넘버</h3>
        <div className="stat-grid">
          {stats.lotto.hot5.map((x) => (
            <div key={x.number} className="stat-chip">
              <span className="num">🔴 {x.number}번</span>
              <span className="cnt">{x.count}회</span>
            </div>
          ))}
          {stats.lotto.cold5.map((x) => (
            <div key={x.number} className="stat-chip">
              <span className="num">🔵 {x.number}번</span>
              <span className="cnt">{x.count}회</span>
            </div>
          ))}
        </div>
      </div>

      <div className="stat-section">
        <h3>📌 연금복권 조별 출현</h3>
        {stats.pension.group_freq.map((x) => (
          <div key={x.group} className="stat-bar-row">
            <span className="stat-label">{x.group}조</span>
            <div className="stat-bar">
              <div
                className="stat-bar-fill pension"
                style={{ width: `${((x.count / 70) * 100).toFixed(1)}%` }}
              />
            </div>
            <span className="stat-count">{x.count}회</span>
          </div>
        ))}
      </div>

      <div className="stat-section">
        <h3>📊 연금복권 자리별 TOP 3</h3>
        {stats.pension.digit_stats.map((pos) => (
          <div key={pos.position} className="stat-bar-row">
            <span className="stat-label">{pos.position}</span>
            <span style={{ fontSize: 13, color: 'var(--text-dim)' }}>
              {pos.top3.map((t) => (
                <span key={t.digit}>
                  <span style={{ color: 'var(--pension-ball)', fontWeight: 600 }}>{t.digit}</span>
                  ({t.count}){' '}
                </span>
              ))}
            </span>
          </div>
        ))}
      </div>

      <div className="stat-section">
        <h3>📐 로또 당첨 합계 범위 (80%)</h3>
        <p style={{ textAlign: 'center', fontSize: 20, fontWeight: 700, color: 'var(--accent)', padding: '8px 0' }}>
          {stats.lotto.sum_range[0]} ~ {stats.lotto.sum_range[1]}
        </p>
      </div>
    </div>
  );
}
