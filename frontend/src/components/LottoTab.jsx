import { useState } from 'react';
import NumberBall from './NumberBall';

const LottoTab = ({ results, selected, onSelect, onGenerate, onRegenerate, loading }) => {
  const [count, setCount] = useState(5);

  return (
    <section>
      {/* 수량 + 금액 */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center bg-surface2 border border-night rounded-lg overflow-hidden">
          <button
            className="w-9 h-9 flex items-center justify-center text-dim text-[18px] cursor-pointer hover:bg-surface3 hover:text-body transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            onClick={() => setCount(c => Math.max(1, c - 1))}
            disabled={count <= 1}
          >−</button>
          <span className="w-11 text-center text-[14px] font-bold text-body tabular-nums">{count}장</span>
          <button
            className="w-9 h-9 flex items-center justify-center text-dim text-[18px] cursor-pointer hover:bg-surface3 hover:text-body transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            onClick={() => setCount(c => Math.min(10, c + 1))}
            disabled={count >= 10}
          >+</button>
        </div>
        <span className="text-[13px] text-muted tabular-nums">
          <span className="text-gold font-bold text-[15px]">{(count * 1000).toLocaleString()}</span>원
        </span>
      </div>

      <div className="flex gap-2 mb-4">
        <button
          className={`btn-generate flex-1 py-3.5 px-6 rounded-[10px] text-[15px] font-bold text-bg border-none cursor-pointer tracking-wide disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]${loading ? ' loading' : ''}`}
          onClick={() => onGenerate(count)}
          disabled={loading}
        >
          번호 생성
        </button>
        {results.length > 0 && (
          <button
            className="py-3.5 px-5 bg-surface2 text-dim border border-night text-[14px] font-medium rounded-[10px] cursor-pointer transition-all hover:bg-surface3 hover:text-body whitespace-nowrap disabled:opacity-40"
            onClick={() => onRegenerate(count)}
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
              className={`number-card bg-surface rounded-xl p-4 px-4.5 mb-2 cursor-pointer relative transition-all duration-200 hover:-translate-y-px border border-t-[rgba(255,255,255,0.07)]${isSelected ? ' card-selected border-gold bg-[rgba(232,168,32,0.06)]' : ' border-night hover:border-[rgba(232,168,32,0.3)]'}`}
              onClick={() => onSelect(r)}
            >
              <div className="flex justify-between items-center mb-3.5">
                <span className="text-[11px] font-semibold text-muted bg-surface3 px-2 py-0.5 rounded-full uppercase tracking-wide">
                  {r.strategy}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-muted tabular-nums">합 {r.sum} · {r.odd_even}</span>
                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-gold flex items-center justify-center text-bg flex-shrink-0">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3 h-3">
                        <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clipRule="evenodd" />
                      </svg>
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
};

export default LottoTab;
