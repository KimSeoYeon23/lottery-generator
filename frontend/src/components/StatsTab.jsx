const Section = ({ title, children }) => (
  <div className="bg-surface border border-night border-t-[rgba(255,255,255,0.07)] rounded-xl p-4 px-[18px] mb-2.5">
    <h3 className="text-[12px] font-semibold text-dim uppercase tracking-[0.4px] mb-3.5">{title}</h3>
    {children}
  </div>
);

const BarRow = ({ label, pct, count, variant }) => {
  const fill = {
    hot:     'linear-gradient(90deg, #E8A820, #ef4444)',
    cold:    'linear-gradient(90deg, #38bdf8, #818cf8)',
    pension: 'linear-gradient(90deg, #E8A820, #818cf8)',
  }[variant];
  return (
    <div className="flex items-center gap-2.5 mb-[7px] text-[13px]">
      <span className="w-12 text-right text-dim text-[12px] flex-shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-surface3 rounded overflow-hidden">
        <div className="h-full rounded transition-[width] duration-500" style={{ width: `${pct}%`, background: fill }} />
      </div>
      <span className="w-9 text-[11px] text-muted flex-shrink-0 tabular-nums">{count}회</span>
    </div>
  );
};

export default function StatsTab({ stats }) {
  if (!stats) {
    return <p className="text-center text-body opacity-60 py-9 text-[13px] leading-7">번호를 생성하면 통계가 표시됩니다.</p>;
  }

  const maxLotto = Math.max(...stats.lotto.top10.map((x) => x.count));

  return (
    <div>
      <Section title="🔥 로또 역대 TOP 10">
        {stats.lotto.top10.map((x) => (
          <BarRow key={x.number} label={`${x.number}번`} pct={(x.count / maxLotto * 100).toFixed(1)} count={x.count} variant="hot" />
        ))}
      </Section>

      <Section title="❄️ 가장 적게 나온 번호">
        <div className="grid grid-cols-2 gap-1.5">
          {stats.lotto.bottom5.map((x) => (
            <div key={x.number} className="flex justify-between items-center bg-surface2 px-3 py-2 rounded-lg border border-night">
              <span className="text-gold font-bold text-[14px]">{x.number}번</span>
              <span className="text-muted text-[11px]">{x.count}회</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="🔴 핫넘버 / 🔵 콜드넘버">
        <div className="grid grid-cols-2 gap-1.5">
          {stats.lotto.hot5.map((x) => (
            <div key={x.number} className="flex justify-between items-center bg-surface2 px-3 py-2 rounded-lg border border-night">
              <span className="text-gold font-bold text-[14px]">🔴 {x.number}번</span>
              <span className="text-muted text-[11px]">{x.count}회</span>
            </div>
          ))}
          {stats.lotto.cold5.map((x) => (
            <div key={x.number} className="flex justify-between items-center bg-surface2 px-3 py-2 rounded-lg border border-night">
              <span className="text-[#38bdf8] font-bold text-[14px]">🔵 {x.number}번</span>
              <span className="text-muted text-[11px]">{x.count}회</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="📌 연금복권 조별 출현">
        {stats.pension.group_freq.map((x) => (
          <BarRow key={x.group} label={`${x.group}조`} pct={(x.count / 70 * 100).toFixed(1)} count={x.count} variant="pension" />
        ))}
      </Section>

      <Section title="📊 연금복권 자리별 TOP 3">
        {stats.pension.digit_stats.map((pos) => (
          <div key={pos.position} className="flex items-center gap-2.5 mb-[7px]">
            <span className="w-12 text-right text-dim text-[12px] flex-shrink-0">{pos.position}</span>
            <span className="text-[13px] text-dim">
              {pos.top3.map((t) => (
                <span key={t.digit} className="mr-2">
                  <span className="text-[#38BDF8] font-bold">{t.digit}</span>
                  <span className="text-muted text-[11px]">({t.count})</span>
                </span>
              ))}
            </span>
          </div>
        ))}
      </Section>

      <Section title="📐 로또 당첨 합계 범위 (80%)">
        <p className="text-center text-[20px] font-bold text-gold py-2">
          {stats.lotto.sum_range[0]} ~ {stats.lotto.sum_range[1]}
        </p>
      </Section>
    </div>
  );
}
