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

async function saveCard(id, title, subtitle, description) {
  const r = await fetch(`${API}/cards/${id}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, subtitle, description })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function getRevisions(id) {
  const r = await fetch(`${API}/cards/${id}/revisions`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function revertRevision(id, revision) {
  const r = await fetch(`${API}/cards/${id}/revert/${revision}`, { method: 'POST' });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function renderSourceBox(el, card) {
  const s = card.source || {};
  const editable = (card.editableFields || []).join(', ') || 'none';
  el.innerHTML = `
    <div><strong>Path:</strong> <code>${s.path || 'n/a'}</code></div>
    <div><strong>Parser:</strong> ${s.parser || 'n/a'}</div>
    <div><strong>Confidence:</strong> ${typeof s.confidence === 'number' ? s.confidence.toFixed(2) : 'n/a'}</div>
    <div><strong>Editable:</strong> ${editable}</div>
  `;
}

function renderCards(cards) {
  deckEl.innerHTML = '';
  cards.forEach((card) => {
    const frag = template.content.cloneNode(true);
    frag.querySelector('.type').textContent = card.type;
    frag.querySelector('.rev').textContent = `r${card.revision}`;

    const titleEl = frag.querySelector('.edit-title');
    const subtitleEl = frag.querySelector('.edit-subtitle');
    const descEl = frag.querySelector('.edit-description');
    titleEl.value = card.title || '';
    subtitleEl.value = card.subtitle || '';
    descEl.value = card.description || '';

    const stats = frag.querySelector('.stats');
    (card.stats || []).slice(0, 6).forEach((s) => stats.appendChild(statNode(s)));
    const traits = frag.querySelector('.traits');
    (card.traits || []).slice(0, 8).forEach((t) => traits.appendChild(traitNode(t)));

    const revBox = frag.querySelector('.revisions');
    const srcBox = frag.querySelector('.source-box');
    renderSourceBox(srcBox, card);

    frag.querySelector('.save-btn').addEventListener('click', async () => {
      try {
        const out = await saveCard(card.id, titleEl.value, subtitleEl.value, descEl.value);
        showReport(`Saved ${out.id} at revision r${out.revision}`);
        await refreshCards();
      } catch (e) { showReport(`Save failed: ${e.message}`); }
    });

    frag.querySelector('.revs-btn').addEventListener('click', async () => {
      try {
        const revs = await getRevisions(card.id);
        revBox.innerHTML = '';
        revs.slice().reverse().forEach((rv) => {
          const row = document.createElement('div');
          row.className = 'rev-row';
          const when = new Date(rv.updatedAt).toLocaleString();
          row.innerHTML = `<span>r${rv.revision} · ${when}</span>`;
          const btn = document.createElement('button');
          btn.className = 'small';
          btn.textContent = 'Revert';
          btn.addEventListener('click', async () => {
            try {
              const out = await revertRevision(card.id, rv.revision);
              showReport(`Reverted ${card.id} to r${rv.revision}; new head r${out.revision}`);
              await refreshCards();
            } catch (e) { showReport(`Revert failed: ${e.message}`); }
          });
          row.appendChild(btn);
          revBox.appendChild(row);
        });
        revBox.classList.toggle('hidden');
      } catch (e) { showReport(`Revision load failed: ${e.message}`); }
    });

    frag.querySelector('.src-btn').addEventListener('click', () => {
      srcBox.classList.toggle('hidden');
    });

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
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path })
  });
  const data = await r.json();
  if (!r.ok) { showReport(`Ingest failed: ${JSON.stringify(data)}`); return; }
  showReport(`Ingested ${data.imported} cards (parsed=${data.report.parsed}, errors=${data.report.errors})`);
  await refreshCards();
}

document.getElementById('refreshBtn').addEventListener('click', refreshCards);
document.getElementById('ingestBtn').addEventListener('click', ingestFolder);
refreshCards().catch((e) => showReport(`API not reachable yet: ${e.message}`));
