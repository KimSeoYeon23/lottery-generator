import NumberBall from './NumberBall';

export default function LottoTab({ results, selected, onSelect, onGenerate, onRegenerate, loading }) {
  return (
    <section>
      <div className="flex gap-2 mb-4">
        <button
          className={`flex-1 py-3.5 px-6 rounded-[10px] text-[15px] font-bold text-bg border-none cursor-pointer tracking-wide transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]${loading ? ' loading' : ''}`}
          style={{
            background: 'linear-gradient(135deg, #E8A820, #C48B10)',
            boxShadow: '0 2px 12px rgba(232,168,32,0.25)',
          }}
          onClick={onGenerate}
          disabled={loading}
          onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 20px rgba(232,168,32,0.35)'}
          onMouseLeave={e => e.currentTarget.style.boxShadow = '0 2px 12px rgba(232,168,32,0.25)'}
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
        {results.map((r, i) => {
          const isSelected = selected.some(
            (s) => JSON.stringify(s.numbers) === JSON.stringify(r.numbers)
          );
          return (
            <div
              key={i}
              className={`number-card bg-surface border border-t-[rgba(255,255,255,0.07)] rounded-xl p-4 px-[18px] mb-2 cursor-pointer relative transition-all duration-200 hover:-translate-y-px${isSelected ? ' card-selected border-gold bg-[rgba(232,168,32,0.06)]' : ' border-night hover:border-[rgba(232,168,32,0.3)]'}`}
              onClick={() => onSelect(r)}
            >
              <div className="flex justify-between items-center mb-3.5">
                <span className="text-[11px] font-semibold text-muted bg-surface3 px-[9px] py-[3px] rounded-full uppercase tracking-[0.3px]">
                  {r.strategy}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-muted tabular-nums">합 {r.sum} · {r.odd_even}</span>
                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-gold flex items-center justify-center text-[11px] text-bg font-bold flex-shrink-0">
                      ✓
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-2 justify-center">
                {r.numbers.map((n) => <NumberBall key={n} n={n} />)}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
