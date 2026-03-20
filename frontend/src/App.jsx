import { useState, useEffect } from 'react';
import LottoTab from './components/LottoTab';
import PensionTab from './components/PensionTab';
import StatsTab from './components/StatsTab';
import BuyTab from './components/BuyTab';

const TABS = [
  { id: 'lotto',   label: '로또 6/45' },
  { id: 'pension', label: '연금복권 720+' },
  { id: 'stats',   label: '통계' },
  { id: 'buy',     label: '구매' },
];

const fetchGenerate = async (lottoCount = 5) => {
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lotto_count: lottoCount, pension_count: 5 }),
  });
  return res.json();
};

const App = () => {
  const [activeTab, setActiveTab] = useState('lotto');
  const [lotto, setLotto] = useState([]);
  const [pension, setPension] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/stats').then((r) => r.json()).then(setStats);
  }, []);

  const handleGenerate = async (lottoCount) => {
    setLoading(true);
    const data = await fetchGenerate(typeof lottoCount === 'number' ? lottoCount : 5);
    setLotto(data.lotto);
    setPension(data.pension);
    setStats(data.stats);
    setSelected(data.lotto.slice(0, 5));
    setLoading(false);
  };

  const handleRegenerateLotto = async (lottoCount) => {
    setLoading(true);
    const data = await fetchGenerate(lottoCount);
    setLotto(data.lotto);
    setSelected(data.lotto.slice(0, 5));
    setLoading(false);
  };

  const handleRegeneratePension = async () => {
    setLoading(true);
    const data = await fetchGenerate();
    setPension(data.pension);
    setLoading(false);
  };

  const handleSelect = (r) => {
    const key = JSON.stringify(r.numbers);
    const exists = selected.findIndex((s) => JSON.stringify(s.numbers) === key);
    if (exists >= 0) {
      setSelected((prev) => prev.filter((_, i) => i !== exists));
    } else if (selected.length < 5) {
      setSelected((prev) => [...prev, r]);
    }
  };

  const handleRemove = (idx) => {
    setSelected((prev) => prev.filter((_, i) => i !== idx));
  };

  return (
    <div className="max-w-[680px] mx-auto px-4 py-8">
      <header className="text-center mb-9">
        <span
          className="text-4xl block mb-2.5"
          style={{ filter: 'drop-shadow(0 0 12px rgba(232,168,32,0.5))' }}
        >🎱</span>
        <h1 className="text-2xl font-bold tracking-tight text-body">
          <em className="not-italic text-gold">번호</em> 생성기
        </h1>
        <p className="text-dim text-[13px] mt-1 tracking-wide">로또 6/45 & 연금복권 720+</p>
      </header>

      <nav
        className="flex border-b border-night mb-6"
        style={{ background: 'radial-gradient(ellipse 80% 40% at 50% -10%, rgba(232,168,32,0.04) 0%, transparent 70%)' }}
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab-item${activeTab === t.id ? ' active' : ''}`}
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
          onSyncLotto={() => setSelected([])}
        />
      )}

      <footer className="text-center pt-8 pb-4 text-muted text-[11px] leading-relaxed">
        <p>⚠️ 복권은 완전한 확률 게임입니다. 재미로만 참고하세요!</p>
      </footer>
    </div>
  );
};

export default App;
