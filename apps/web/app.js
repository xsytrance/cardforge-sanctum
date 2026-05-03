const API = 'http://127.0.0.1:18000';

const deckEl = document.getElementById('deck');
const reportEl = document.getElementById('report');
const template = document.getElementById('cardTemplate');

function showReport(text) {
  reportEl.textContent = text;
  reportEl.classList.remove('hidden');
}

function statNode(s) {
  const d = document.createElement('div');
  d.className = 'stat';
  d.innerHTML = `<div class="k">${s.label}</div><div class="v">${s.value ?? '-'}</div>`;
  return d;
}

function traitNode(t) {
  const d = document.createElement('span');
  d.className = 'trait';
  d.textContent = t;
  return d;
}

function renderCards(cards) {
  deckEl.innerHTML = '';
  cards.forEach((card) => {
    const frag = template.content.cloneNode(true);
    frag.querySelector('.type').textContent = card.type;
    frag.querySelector('.rev').textContent = `r${card.revision}`;
    frag.querySelector('.title').textContent = card.title;
    frag.querySelector('.sub').textContent = card.subtitle || '';
    frag.querySelector('.desc').textContent = card.description || '';

    const stats = frag.querySelector('.stats');
    (card.stats || []).slice(0, 6).forEach((s) => stats.appendChild(statNode(s)));

    const traits = frag.querySelector('.traits');
    (card.traits || []).slice(0, 8).forEach((t) => traits.appendChild(traitNode(t)));

    deckEl.appendChild(frag);
  });
}

async function refreshCards() {
  const r = await fetch(`${API}/cards`);
  const data = await r.json();
  renderCards(data);
  showReport(`Loaded ${data.length} cards`);
}

async function ingestFolder() {
  const path = document.getElementById('folderPath').value.trim();
  const r = await fetch(`${API}/ingest/folder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path })
  });
  const data = await r.json();
  if (!r.ok) {
    showReport(`Ingest failed: ${JSON.stringify(data)}`);
    return;
  }
  showReport(`Ingested ${data.imported} cards (parsed=${data.report.parsed}, errors=${data.report.errors})`);
  await refreshCards();
}

document.getElementById('refreshBtn').addEventListener('click', refreshCards);
document.getElementById('ingestBtn').addEventListener('click', ingestFolder);

refreshCards().catch((e) => showReport(`API not reachable yet: ${e.message}`));
