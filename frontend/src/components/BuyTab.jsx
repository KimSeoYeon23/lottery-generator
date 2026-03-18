import { useState } from 'react';

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
      body: JSON.stringify({
        tickets: selected.map((s) => s.numbers),
        username,
        password,
      }),
    });
    const data = await res.json();
    setLoading('');

    if (data.error) {
      setBuyResult({ type: 'error', message: data.error });
    } else {
      setBuyResult({ type: 'success', data });
      onSyncLotto(); // 선택 초기화 후 로또 카드 상태 동기화
    }
  }

  return (
    <div className="buy-section">
      <div className="login-form">
        <p className="section-title">🔐 동행복권 계정</p>
        <input
          type="text"
          placeholder="아이디"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <div className="login-actions">
          <button className="btn-secondary" onClick={handleSaveCreds}>계정 저장</button>
          <button
            className={`btn-secondary${loading === 'balance' ? ' loading' : ''}`}
            onClick={handleBalance}
            disabled={loading === 'balance'}
          >
            잔액 조회
          </button>
        </div>

        {balanceResult && (
          <div style={{ marginTop: 12, fontSize: 13 }}>
            {balanceResult.type === 'error' && (
              <div className="result-error">{balanceResult.message}</div>
            )}
            {balanceResult.type === 'success' && (
              <div className="result-success">{balanceResult.message}</div>
            )}
            {balanceResult.type === 'balance' && (
              <div className="balance-info">
                <div className="balance-row">
                  <span className="label">총 예치금</span>
                  <span className="value">{balanceResult.data.total.toLocaleString()}원</span>
                </div>
                <div className="balance-row">
                  <span className="label">구매 가능</span>
                  <span className="value highlight">{balanceResult.data.available.toLocaleString()}원</span>
                </div>
                <div className="balance-row">
                  <span className="label">예약 구매</span>
                  <span className="value">{balanceResult.data.reserved.toLocaleString()}원</span>
                </div>
                <div className="balance-row">
                  <span className="label">구매 가능</span>
                  <span className="value highlight">{balanceResult.data.tickets}장</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="buy-tickets">
        <p className="section-title">🎯 선택된 번호</p>
        {selected.length === 0 ? (
          <p className="placeholder">로또 탭에서 번호 카드를 클릭해<br/>구매할 번호를 선택하세요. (최대 5장)</p>
        ) : (
          <>
            {selected.map((s, i) => (
              <div key={i} className="selected-ticket-item">
                <span className="slot">{'ABCDE'[i]}</span>
                <span className="nums">{s.numbers.join('  ')}</span>
                <span className="strat">{s.strategy}</span>
                <span className="remove" onClick={() => onRemove(i)}>✕</span>
              </div>
            ))}
            <p className="ticket-summary">
              {selected.length}장 · <span>{(selected.length * 1000).toLocaleString()}원</span>
            </p>
          </>
        )}

        <button
          className={`btn-danger${loading === 'buy' ? ' loading' : ''}`}
          onClick={handleBuy}
          disabled={selected.length === 0 || loading === 'buy'}
        >
          구매하기
        </button>

        {buyResult && (
          buyResult.type === 'error' ? (
            <div className="result-error">{buyResult.message}</div>
          ) : (
            <div className="result-success">
              <strong>구매 완료!</strong>
              <div>회차: {buyResult.data.round}회</div>
              <div>추첨일: {buyResult.data.draw_date}</div>
              {buyResult.data.tickets.map((t) => (
                <div key={t.slot} style={{ margin: '4px 0' }}>
                  [{t.slot}] {t.mode}: {t.numbers.join(', ')}
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
