const PensionTab = ({ results, onGenerate, onRegenerate, loading }) => {
  return (
    <section>
      <div className="flex gap-2 mb-4">
        <button
          className={`btn-generate flex-1 py-3.5 px-6 rounded-[10px] text-[15px] font-bold text-bg border-none cursor-pointer tracking-wide disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]${loading ? ' loading' : ''}`}
          onClick={() => onGenerate()}
          disabled={loading}
        >
          번호 생성
        </button>
        {results.length > 0 && (
          <button
            className="py-3.5 px-5 bg-surface2 text-dim border border-night text-[14px] font-medium rounded-[10px] cursor-pointer transition-all hover:bg-surface3 hover:text-body whitespace-nowrap disabled:opacity-40"
            onClick={() => onRegenerate()}
            disabled={loading}
          >
            다시 생성
          </button>
        )}
      </div>

      {results.length > 0 && (
        <p className="text-[11px] text-muted mb-3 leading-5 text-center">
          생성된 번호는 <span className="text-dim">참고용</span>입니다. 실제 구매 번호는 동행복권 서버가 별도로 배정합니다.
        </p>
      )}

      <div>
        {results.map((r, i) => {
          return (
            <div
              key={i}
              className="bg-surface border border-t-[rgba(255,255,255,0.07)] border-night rounded-xl p-4 px-4.5 mb-2"
            >
              <div className="flex justify-between items-center mb-3.5">
                <span className="text-[11px] font-semibold text-muted bg-surface3 px-2 py-0.5 rounded-full uppercase tracking-wide">
                  {r.strategy}
                </span>
                <div className="flex items-baseline gap-1">
                  <span className="text-[20px] font-extrabold text-gold leading-none tabular-nums">{r.group}</span>
                  <span className="text-[11px] text-muted">조</span>
                </div>
              </div>
              <div className="flex justify-center gap-1.5">
                {r.numbers.map((d, j) => (
                  <div
                    key={j}
                    className="w-9 h-12 bg-surface3 border border-night border-t-[rgba(255,255,255,0.07)] rounded-lg flex items-center justify-center text-[22px] font-extrabold text-sky tabular-nums"
                    style={{ boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)' }}
                  >
                    {d}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default PensionTab;
