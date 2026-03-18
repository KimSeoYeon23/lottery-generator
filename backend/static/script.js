const state = {
  lotto: [],
  pension: [],
  stats: null,
  selected: [], // 구매할 번호 [{numbers: [...], strategy: '...'}]
};

// 탭 전환
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
  });
});

// 로또 공 색상
function ballClass(n) {
  if (n <= 10) return 'r1';
  if (n <= 20) return 'r2';
  if (n <= 30) return 'r3';
  if (n <= 40) return 'r4';
  return 'r5';
}

// 번호 생성 API
async function generate() {
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lotto_count: 5, pension_count: 5 }),
  });
  return res.json();
}

// 로또 결과 렌더링
function renderLotto(results) {
  const el = document.getElementById('lotto-results');
  el.innerHTML = results.map((r, i) => {
    const balls = r.numbers.map(n =>
      `<div class="ball ${ballClass(n)}">${n}</div>`
    ).join('');
    const isSelected = state.selected.some(s =>
      JSON.stringify(s.numbers) === JSON.stringify(r.numbers)
    );
    return `
      <div class="number-card ${isSelected ? 'selected' : ''}"
           data-index="${i}" data-type="lotto">
        <div class="card-header">
          <span class="strategy-name">${r.strategy}</span>
          <span class="card-meta">합:${r.sum} | 홀짝 ${r.odd_even}</span>
        </div>
        <div class="ball-row">${balls}</div>
      </div>
    `;
  }).join('');

  // 카드 클릭 → 구매 목록에 추가/제거
  el.querySelectorAll('.number-card').forEach(card => {
    card.addEventListener('click', () => {
      const idx = parseInt(card.dataset.index);
      const nums = results[idx].numbers;
      const existing = state.selected.findIndex(s =>
        JSON.stringify(s.numbers) === JSON.stringify(nums)
      );
      if (existing >= 0) {
        state.selected.splice(existing, 1);
        card.classList.remove('selected');
      } else if (state.selected.length < 5) {
        state.selected.push({
          numbers: nums,
          strategy: results[idx].strategy,
        });
        card.classList.add('selected');
      }
      renderSelectedTickets();
    });
  });
}

// 연금복권 결과 렌더링
function renderPension(results) {
  const el = document.getElementById('pension-results');
  el.innerHTML = results.map(r => {
    const digits = r.numbers.map(d =>
      `<div class="pension-digit">${d}</div>`
    ).join('');
    return `
      <div class="number-card">
        <div class="card-header">
          <span class="strategy-name">${r.strategy}</span>
        </div>
        <div class="pension-display">
          <div class="pension-group">${r.group}<span>조</span></div>
          ${digits}
        </div>
      </div>
    `;
  }).join('');
}

// 통계 렌더링
function renderStats(stats) {
  const el = document.getElementById('stats-content');
  const maxLotto = Math.max(...stats.lotto.top10.map(x => x.count));

  let html = `
    <div class="stat-section">
      <h3>🔥 로또 역대 TOP 10</h3>
      ${stats.lotto.top10.map(x => `
        <div class="stat-bar-row">
          <span class="stat-label">${x.number}번</span>
          <div class="stat-bar">
            <div class="stat-bar-fill hot" style="width:${(x.count / maxLotto * 100).toFixed(1)}%"></div>
          </div>
          <span class="stat-count">${x.count}회</span>
        </div>
      `).join('')}
    </div>

    <div class="stat-section">
      <h3>❄️ 가장 적게 나온 번호</h3>
      <div class="stat-grid">
        ${stats.lotto.bottom5.map(x => `
          <div class="stat-chip">
            <span class="num">${x.number}번</span>
            <span class="cnt">${x.count}회</span>
          </div>
        `).join('')}
      </div>
    </div>

    <div class="stat-section">
      <h3>🔴 최근 핫넘버 / 🔵 콜드넘버</h3>
      <div class="stat-grid">
        ${stats.lotto.hot5.map(x => `
          <div class="stat-chip">
            <span class="num">🔴 ${x.number}번</span>
            <span class="cnt">${x.count}회</span>
          </div>
        `).join('')}
        ${stats.lotto.cold5.map(x => `
          <div class="stat-chip">
            <span class="num">🔵 ${x.number}번</span>
            <span class="cnt">${x.count}회</span>
          </div>
        `).join('')}
      </div>
    </div>

    <div class="stat-section">
      <h3>📌 연금복권 조별 출현</h3>
      ${stats.pension.group_freq.map(x => `
        <div class="stat-bar-row">
          <span class="stat-label">${x.group}조</span>
          <div class="stat-bar">
            <div class="stat-bar-fill pension" style="width:${(x.count / 70 * 100).toFixed(1)}%"></div>
          </div>
          <span class="stat-count">${x.count}회</span>
        </div>
      `).join('')}
    </div>

    <div class="stat-section">
      <h3>📊 연금복권 자리별 TOP 3</h3>
      ${stats.pension.digit_stats.map(pos => `
        <div class="stat-bar-row">
          <span class="stat-label">${pos.position}</span>
          <span style="font-size:13px;color:var(--text-dim)">
            ${pos.top3.map(t => `<span style="color:var(--pension-ball);font-weight:600">${t.digit}</span>(${t.count})`).join(' ')}
          </span>
        </div>
      `).join('')}
    </div>

    <div class="stat-section">
      <h3>📐 로또 당첨 합계 범위 (80%)</h3>
      <p style="text-align:center;font-size:20px;font-weight:700;color:var(--accent);padding:8px 0">
        ${stats.lotto.sum_range[0]} ~ ${stats.lotto.sum_range[1]}
      </p>
    </div>
  `;

  el.innerHTML = html;
}

// 선택된 번호 렌더링 (구매탭)
function renderSelectedTickets() {
  const el = document.getElementById('selected-tickets');
  const btn = document.getElementById('btn-buy');

  if (state.selected.length === 0) {
    el.innerHTML = '<p class="placeholder">로또 탭에서 번호를 클릭해 선택하세요. (최대 5장)</p>';
    btn.disabled = true;
    return;
  }

  el.innerHTML = state.selected.map((s, i) => `
    <div class="selected-ticket-item">
      <span class="nums">${s.numbers.join(', ')}</span>
      <span class="strategy-name">${s.strategy}</span>
      <span class="remove" data-idx="${i}">✕</span>
    </div>
  `).join('') + `
    <p style="font-size:12px;color:var(--text-dim);margin-top:8px;text-align:center">
      ${state.selected.length}장 = ${(state.selected.length * 1000).toLocaleString()}원
    </p>
  `;

  btn.disabled = false;

  el.querySelectorAll('.remove').forEach(rm => {
    rm.addEventListener('click', (e) => {
      e.stopPropagation();
      const idx = parseInt(rm.dataset.idx);
      state.selected.splice(idx, 1);
      renderSelectedTickets();
      renderLotto(state.lotto); // 선택 상태 동기화
    });
  });
}

// 이벤트: 로또 생성
document.getElementById('btn-generate-lotto').addEventListener('click', async function () {
  this.classList.add('loading');
  this.disabled = true;
  const data = await generate();
  state.lotto = data.lotto;
  state.pension = data.pension;
  state.stats = data.stats;
  renderLotto(data.lotto);
  renderPension(data.pension);
  renderStats(data.stats);
  this.classList.remove('loading');
  this.disabled = false;
  document.getElementById('btn-regenerate-lotto').style.display = '';
});

document.getElementById('btn-regenerate-lotto').addEventListener('click', async function () {
  const data = await generate();
  state.lotto = data.lotto;
  renderLotto(data.lotto);
});

// 이벤트: 연금복권 생성
document.getElementById('btn-generate-pension').addEventListener('click', async function () {
  this.classList.add('loading');
  this.disabled = true;
  const data = await generate();
  state.pension = data.pension;
  state.lotto = data.lotto;
  state.stats = data.stats;
  renderPension(data.pension);
  renderLotto(data.lotto);
  renderStats(data.stats);
  this.classList.remove('loading');
  this.disabled = false;
  document.getElementById('btn-regenerate-pension').style.display = '';
});

document.getElementById('btn-regenerate-pension').addEventListener('click', async function () {
  const data = await generate();
  state.pension = data.pension;
  renderPension(data.pension);
});

// 이벤트: 계정 저장
document.getElementById('btn-save-creds').addEventListener('click', async function () {
  const username = document.getElementById('dh-username').value;
  const password = document.getElementById('dh-password').value;
  if (!username || !password) return;

  const res = await fetch('/api/save-credentials', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  const el = document.getElementById('balance-result');
  if (data.ok) {
    el.innerHTML = '<div class="result-success">계정 저장 완료</div>';
  } else {
    el.innerHTML = `<div class="result-error">${data.error}</div>`;
  }
});

// 이벤트: 잔액 조회
document.getElementById('btn-balance').addEventListener('click', async function () {
  this.classList.add('loading');
  const username = document.getElementById('dh-username').value;
  const password = document.getElementById('dh-password').value;

  const res = await fetch('/api/balance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  const el = document.getElementById('balance-result');

  if (data.error) {
    el.innerHTML = `<div class="result-error">${data.error}</div>`;
  } else {
    el.innerHTML = `
      <div class="balance-info">
        <div class="balance-row"><span class="label">총 예치금</span><span class="value">${data.total.toLocaleString()}원</span></div>
        <div class="balance-row"><span class="label">구매 가능</span><span class="value highlight">${data.available.toLocaleString()}원</span></div>
        <div class="balance-row"><span class="label">예약 구매</span><span class="value">${data.reserved.toLocaleString()}원</span></div>
        <div class="balance-row"><span class="label">구매 가능</span><span class="value highlight">${data.tickets}장</span></div>
      </div>
    `;
  }
  this.classList.remove('loading');
});

// 이벤트: 구매
document.getElementById('btn-buy').addEventListener('click', async function () {
  if (state.selected.length === 0) return;
  if (!confirm(`${state.selected.length}장 (${(state.selected.length * 1000).toLocaleString()}원)을 구매하시겠습니까?`)) return;

  this.classList.add('loading');
  this.disabled = true;

  const username = document.getElementById('dh-username').value;
  const password = document.getElementById('dh-password').value;

  const res = await fetch('/api/buy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tickets: state.selected.map(s => s.numbers),
      username, password,
    }),
  });
  const data = await res.json();
  const el = document.getElementById('buy-result');

  if (data.error) {
    el.innerHTML = `<div class="result-error">${data.error}</div>`;
  } else {
    const ticketList = data.tickets.map(t =>
      `<div style="margin:4px 0">[${t.slot}] ${t.mode}: ${t.numbers.join(', ')}</div>`
    ).join('');
    el.innerHTML = `
      <div class="result-success">
        <div style="font-weight:700;margin-bottom:8px">구매 완료!</div>
        <div>회차: ${data.round}회</div>
        <div>추첨일: ${data.draw_date}</div>
        ${ticketList}
      </div>
    `;
    state.selected = [];
    renderSelectedTickets();
    renderLotto(state.lotto);
  }

  this.classList.remove('loading');
  this.disabled = false;
});
