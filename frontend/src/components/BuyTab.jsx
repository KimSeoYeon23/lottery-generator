import { useState, useEffect } from 'react';

const Card = ({ children }) => (
  <div className="bg-surface border border-night border-t-[rgba(255,255,255,0.07)] rounded-xl p-[18px]">
    {children}
  </div>
);

const SectionTitle = ({ children }) => (
  <p className="text-[13px] font-semibold text-dim flex items-center gap-1.5 mb-3.5">{children}</p>
);

const MAX_TOTAL = 5;

const BuyTab = ({ selected, onRemove, onSyncLotto }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [balanceResult, setBalanceResult] = useState(null);
  const [buyResult, setBuyResult] = useState(null);
  const [loading, setLoading] = useState('');
  const [quantities, setQuantities] = useState({});
  const [mockMode, setMockMode] = useState(false);

  useEffect(() => {
    setQuantities((prev) => {
      const next = {};
      selected.forEach((_, i) => { next[i] = prev[i] ?? 1; });
      return next;
    });
  }, [selected]);

  const totalQty = Object.values(quantities).reduce((a, b) => a + b, 0);

  const setQty = (idx, delta) => {
    setQuantities((prev) => {
      const current = prev[idx] ?? 1;
      const next = Math.max(1, current + delta);
      const otherTotal = totalQty - current;
      const capped = Math.min(next, MAX_TOTAL - otherTotal);
      return { ...prev, [idx]: capped };
    });
  };

  const handleSaveCreds = async () => {
    if (!username || !password) return;
    const res = await fetch('/api/save-credentials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    setBalanceResult(data.ok
      ? { type: 'success', message: '계정 저장 완료' }
      : { type: 'error', message: data.error }
    );
  };

  const handleBalance = async () => {
    setLoading('balance');
    const res = await fetch('/api/balance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    setLoading('');
    if (data.error) {
      setBalanceResult({ type: 'error', message: data.error });
    } else {
      setBalanceResult({ type: 'balance', data });
    }
  };

  const handleBuy = async () => {
    if (totalQty === 0) return;
    if (!confirm(`총 ${totalQty}장 (${(totalQty * 1000).toLocaleString()}원)을 구매하시겠습니까?`)) return;
    setLoading('buy');
    const tickets = selected.flatMap((s, i) =>
      Array(quantities[i] ?? 1).fill(s.numbers)
    );
    const res = await fetch('/api/buy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickets, username, password, mock: mockMode }),
    });
    const data = await res.json();
    setLoading('');
    if (data.error) {
      setBuyResult({ type: 'error', message: data.error });
    } else {
      setBuyResult({ type: 'success', data });
      onSyncLotto();
    }
  };

  const inputCls = "w-full px-3 py-[11px] mb-2 bg-surface2 border border-night rounded-lg text-body text-[14px] outline-none transition-colors focus:border-[rgba(232,168,32,0.5)] placeholder:text-muted";

  return (
    <div className="flex flex-col gap-3">
      <Card>
        <SectionTitle>🔐 동행복권 계정</SectionTitle>
        <input className={inputCls} type="text" placeholder="아이디" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className={inputCls} type="password" placeholder="비밀번호" value={password} onChange={(e) => setPassword(e.target.value)} />
        <div className="flex gap-2 mt-1">
          <button className="flex-1 py-2.5 text-[13px] font-medium bg-surface2 text-dim border border-night rounded-[10px] cursor-pointer hover:bg-surface3 hover:text-body transition-all"
            onClick={handleSaveCreds}>계정 저장</button>
          <button className={`flex-1 py-2.5 text-[13px] font-medium bg-surface2 text-dim border border-night rounded-[10px] cursor-pointer hover:bg-surface3 hover:text-body transition-all disabled:opacity-40${loading === 'balance' ? ' loading' : ''}`}
            onClick={handleBalance} disabled={loading === 'balance'}>잔액 조회</button>
        </div>

        {balanceResult && (
          <div className="mt-3">
            {balanceResult.type === 'error' && (
              <div className="bg-[rgba(239,68,68,0.06)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3 text-[#fca5a5] text-[13px]">{balanceResult.message}</div>
            )}
            {balanceResult.type === 'success' && (
              <div className="bg-[rgba(34,197,94,0.06)] border border-[rgba(34,197,94,0.2)] rounded-lg p-3 text-[#86efac] text-[13px]">{balanceResult.message}</div>
            )}
            {balanceResult.type === 'balance' && (
              <div className="bg-surface2 rounded-lg p-3 border border-night">
                {[
                  ['총 예치금', `${balanceResult.data.total.toLocaleString()}원`, false],
                  ['구매 가능', `${balanceResult.data.available.toLocaleString()}원`, true],
                  ['예약 구매', `${balanceResult.data.reserved.toLocaleString()}원`, false],
                  ['구매 가능', `${balanceResult.data.tickets}장`, true],
                ].map(([label, value, highlight], i, arr) => (
                  <div key={i} className={`flex justify-between py-[5px]${i < arr.length - 1 ? ' border-b border-night' : ''}`}>
                    <span className="text-muted text-[12px]">{label}</span>
                    <span className={`font-semibold text-[13px] tabular-nums${highlight ? ' text-gold' : ' text-body'}`}>{value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>

      <Card>
        <SectionTitle>🎯 선택된 번호</SectionTitle>
        {selected.length === 0 ? (
          <p className="text-center text-body opacity-60 py-9 text-[13px] leading-7">
            로또 탭에서 번호 카드를 클릭해<br/>구매할 번호를 선택하세요.
          </p>
        ) : (
          <>
            {selected.map((s, i) => (
              <div key={i} className="flex items-center gap-2 bg-surface2 px-3 py-2.5 rounded-lg mb-1.5 border border-night">
                <div className="w-[22px] h-[22px] rounded-full bg-[rgba(232,168,32,0.15)] border border-[#C48B10] flex items-center justify-center text-[11px] font-bold text-gold flex-shrink-0">
                  {'ABCDE'[i]}
                </div>
                <span className="flex-1 font-semibold tabular-nums text-body text-[13px]">{s.numbers.join('  ')}</span>

                {/* 수량 스테퍼 */}
                <div className="flex items-center bg-surface border border-night rounded-md overflow-hidden">
                  <button
                    className="w-6 h-6 flex items-center justify-center text-dim text-[14px] cursor-pointer hover:bg-surface3 hover:text-body transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    onClick={() => setQty(i, -1)}
                    disabled={(quantities[i] ?? 1) <= 1}
                  >−</button>
                  <span className="w-5 text-center text-[13px] font-semibold text-body tabular-nums">{quantities[i] ?? 1}</span>
                  <button
                    className="w-6 h-6 flex items-center justify-center text-dim text-[14px] cursor-pointer hover:bg-surface3 hover:text-body transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    onClick={() => setQty(i, +1)}
                    disabled={totalQty >= MAX_TOTAL}
                  >+</button>
                </div>

                <span className="text-muted cursor-pointer text-[16px] ml-0.5 hover:text-[#ef4444] transition-colors" onClick={() => onRemove(i)}>✕</span>
              </div>
            ))}
            <p className="text-center text-[12px] text-muted py-1 pb-2">
              총 {totalQty}장 · <span className="text-gold font-semibold">{(totalQty * 1000).toLocaleString()}원</span>
              <span className="text-muted"> (최대 5장)</span>
            </p>
          </>
        )}

        {/* 테스트 모드 토글 */}
        <label className="flex items-center gap-2 cursor-pointer mt-3 mb-1 select-none w-fit">
          <div
            className={`w-9 h-5 rounded-full transition-colors relative ${mockMode ? 'bg-gold' : 'bg-surface3'}`}
            onClick={() => setMockMode(m => !m)}
          >
            <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${mockMode ? 'translate-x-4' : 'translate-x-0.5'}`} />
          </div>
          <span className={`text-[12px] font-medium ${mockMode ? 'text-gold' : 'text-muted'}`}>
            테스트 모드 {mockMode ? '(실제 구매 안 됨)' : ''}
          </span>
        </label>

        <button
          className={`w-full py-3.5 mt-2 rounded-[10px] text-[15px] font-semibold border cursor-pointer transition-all disabled:opacity-30 disabled:cursor-not-allowed ${mockMode ? 'bg-[rgba(232,168,32,0.12)] text-gold border-[rgba(232,168,32,0.3)] hover:bg-[rgba(232,168,32,0.2)]' : 'bg-[rgba(239,68,68,0.12)] text-[#fca5a5] border-[rgba(239,68,68,0.25)] hover:bg-[rgba(239,68,68,0.2)]'}${loading === 'buy' ? ' loading' : ''}`}
          onClick={handleBuy}
          disabled={selected.length === 0 || loading === 'buy'}
        >
          {mockMode ? '테스트 구매' : '구매하기'}
        </button>

        {buyResult && (
          buyResult.type === 'error' ? (
            <div className="bg-[rgba(239,68,68,0.06)] border border-[rgba(239,68,68,0.2)] rounded-lg p-3 text-[#fca5a5] text-[13px] mt-2.5">{buyResult.message}</div>
          ) : (
            <div className="bg-[rgba(34,197,94,0.06)] border border-[rgba(34,197,94,0.2)] rounded-lg p-3 text-[#86efac] text-[13px] mt-2.5 leading-6">
              <strong className="block text-[14px] text-[#4ade80] font-bold mb-1">구매 완료!</strong>
              <div>회차: {buyResult.data.round}회</div>
              <div>추첨일: {buyResult.data.draw_date}</div>
              {buyResult.data.tickets.map((t) => (
                <div key={t.slot}>[{t.slot}] {t.mode}: {t.numbers.join(', ')}</div>
              ))}
            </div>
          )
        )}
      </Card>
    </div>
  );
};

export default BuyTab;
