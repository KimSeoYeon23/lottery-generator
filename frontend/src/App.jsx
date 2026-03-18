import { useState } from 'react';
import LottoTab from './components/LottoTab';
import PensionTab from './components/PensionTab';
import StatsTab from './components/StatsTab';
import BuyTab from './components/BuyTab';

const TABS = [
  { id: 'lotto', label: '로또 6/45' },
  { id: 'pension', label: '연금복권 720+' },
  { id: 'stats', label: '통계' },
  { id: 'buy', label: '구매' },
];

async function fetchGenerate() {
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lotto_count: 5, pension_count: 5 }),
  });
  return res.json();
}

export default function App() {
  const [activeTab, setActiveTab] = useState('lotto');
  const [lotto, setLotto] = useState([]);
  const [pension, setPension] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleGenerate() {
    setLoading(true);
    const data = await fetchGenerate();
    setLotto(data.lotto);
    setPension(data.pension);
    setStats(data.stats);
    setLoading(false);
  }

  async function handleRegenerateLotto() {
    setLoading(true);
    const data = await fetchGenerate();
    setLotto(data.lotto);
    setLoading(false);
  }

  async function handleRegeneratePension() {
    setLoading(true);
    const data = await fetchGenerate();
    setPension(data.pension);
    setLoading(false);
  }

  function handleSelect(r) {
    const key = JSON.stringify(r.numbers);
    const exists = selected.findIndex((s) => JSON.stringify(s.numbers) === key);
    if (exists >= 0) {
      setSelected((prev) => prev.filter((_, i) => i !== exists));
    } else if (selected.length < 5) {
      setSelected((prev) => [...prev, r]);
    }
  }

  function handleRemove(idx) {
    setSelected((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleSyncLotto() {
    setSelected([]);
  }

  return (
    <div className="container">
      <header>
        <span className="header-icon">🎱</span>
        <h1><em>번호</em> 생성기</h1>
        <p className="subtitle">로또 6/45 & 연금복권 720+</p>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab${activeTab === t.id ? ' active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {activeTab === 'lotto' && (
        <LottoTab
          results={lotto}
          selected={selected}
          onSelect={handleSelect}
          onGenerate={handleGenerate}
          onRegenerate={handleRegenerateLotto}
          loading={loading}
        />
      )}
      {activeTab === 'pension' && (
        <PensionTab
          results={pension}
          onGenerate={handleGenerate}
          onRegenerate={handleRegeneratePension}
          loading={loading}
        />
      )}
      {activeTab === 'stats' && <StatsTab stats={stats} />}
      {activeTab === 'buy' && (
        <BuyTab
          selected={selected}
          onRemove={handleRemove}
          onSyncLotto={handleSyncLotto}
        />
      )}

      <footer>
        <p>⚠️ 복권은 완전한 확률 게임입니다. 재미로만 참고하세요!</p>
      </footer>
    </div>
  );
}
