const PensionTab = ({ results, onGenerate, onRegenerate, loading }) => {
  return (
    <section>
      <div className="flex gap-2 mb-4">
        <button
          className={`flex-1 py-3.5 px-6 rounded-[10px] text-[15px] font-bold text-bg border-none cursor-pointer tracking-wide transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]${loading ? ' loading' : ''}`}
          style={{ background: 'linear-gradient(135deg, #E8A820, #C48B10)', boxShadow: '0 2px 12px rgba(232,168,32,0.25)' }}
          onClick={onGenerate}
          disabled={loading}
        >
          번호 생성
        </button>
        {results.length > 0 && (
          <button
            className="py-3 px-4 bg-surface2 text-dim border border-night text-[14px] font-medium rounded-[10px] cursor-pointer transition-all hover:bg-surface3 hover:text-body whitespace-nowrap disabled:opacity-40"
            onClick={onRegenerate}
            disabled={loading}
          >
            다시 생성
          </button>
        )}
      </div>

      <div>
        {results.map((r, i) => (
          <div key={i} className="bg-surface border border-night border-t-[rgba(255,255,255,0.07)] rounded-xl p-4 px-[18px] mb-2">
            <div className="flex justify-between items-center mb-3.5">
              <span className="text-[11px] font-semibold text-muted bg-surface3 px-[9px] py-[3px] rounded-full uppercase tracking-[0.3px]">
                {r.strategy}
              </span>
            </div>
            <div className="flex items-center justify-center gap-1.5">
              <div className="flex flex-col items-center mr-2.5">
                <span className="text-[28px] font-extrabold text-gold leading-none">{r.group}</span>
                <span className="text-[10px] text-muted mt-0.5">조</span>
              </div>
              {r.numbers.map((d, j) => (
                <div
                  key={j}
                  className="w-[38px] h-[52px] bg-surface3 border border-night border-t-[rgba(255,255,255,0.07)] rounded-[7px] flex items-center justify-center text-[22px] font-extrabold text-[#38BDF8] tabular-nums"
                  style={{ boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)' }}
                >
                  {d}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default PensionTab;
