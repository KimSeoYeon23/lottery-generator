import { useState } from 'react';

const Card = ({ children }) => (
  <div className="bg-surface border border-night border-t-[rgba(255,255,255,0.07)] rounded-xl p-[18px]">
    {children}
  </div>
);

const SectionTitle = ({ children }) => (
  <p className="text-[13px] font-semibold text-dim flex items-center gap-1.5 mb-3.5">{children}</p>
);

export default function BuyTab({ selected, onRemove, onSyncLotto }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [balanceResult, setBalanceResult] = useState(null);
  const [buyResult, setBuyResult] = useState(null);
  const [loading, setLoading] = useState('');

  async function handleSaveCreds() {
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
  }

  async function handleBalance() {
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
  }

  async function handleBuy() {
    if (selected.length === 0) return;
    if (!confirm(`${selected.length}장 (${(selected.length * 1000).toLocaleString()}원)을 구매하시겠습니까?`)) return;
    setLoading('buy');
    const res = await fetch('/api/buy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickets: selected.map((s) => s.numbers), username, password }),
    });
    const data = await res.json();
    setLoading('');
    if (data.error) {
      setBuyResult({ type: 'error', message: data.error });
    } else {
      setBuyResult({ type: 'success', data });
      onSyncLotto();
    }
  }

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
            로또 탭에서 번호 카드를 클릭해<br/>구매할 번호를 선택하세요. (최대 5장)
          </p>
        ) : (
          <>
            {selected.map((s, i) => (
              <div key={i} className="flex items-center gap-2.5 bg-surface2 px-3 py-2.5 rounded-lg mb-1.5 border border-night">
                <div className="w-[22px] h-[22px] rounded-full bg-[rgba(232,168,32,0.15)] border border-[#C48B10] flex items-center justify-center text-[11px] font-bold text-gold flex-shrink-0">
                  {'ABCDE'[i]}
                </div>
                <span className="flex-1 font-semibold tabular-nums text-body text-[13px]">{s.numbers.join('  ')}</span>
                <span className="text-muted text-[11px]">{s.strategy}</span>
                <span className="text-muted cursor-pointer text-[16px] ml-1 hover:text-[#ef4444] transition-colors" onClick={() => onRemove(i)}>✕</span>
              </div>
            ))}
            <p className="text-center text-[12px] text-muted py-1 pb-2">
              {selected.length}장 · <span className="text-gold font-semibold">{(selected.length * 1000).toLocaleString()}원</span>
            </p>
          </>
        )}

        <button
          className={`w-full py-3.5 mt-3 rounded-[10px] text-[15px] font-semibold bg-[rgba(239,68,68,0.12)] text-[#fca5a5] border border-[rgba(239,68,68,0.25)] cursor-pointer transition-all disabled:opacity-30 disabled:cursor-not-allowed hover:not-disabled:bg-[rgba(239,68,68,0.2)]${loading === 'buy' ? ' loading' : ''}`}
          onClick={handleBuy}
          disabled={selected.length === 0 || loading === 'buy'}
        >
          구매하기
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
}
