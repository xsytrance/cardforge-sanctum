const API = 'http://127.0.0.1:18000';
const deck = document.getElementById('deck');
const statusEl = document.getElementById('status');

function setStatus(msg){ statusEl.textContent = msg; }

async function fetchCards(){
  const r = await fetch(`${API}/cards`);
  return await r.json();
}

async function refresh(){
  const cards = await fetchCards();
  render(cards);
  setStatus(`Loaded ${cards.length} cards`);
}

function render(cards){
  deck.innerHTML = '';
  const tpl = document.getElementById('cardTpl');
  cards.forEach(c => {
    const node = tpl.content.cloneNode(true);
    node.querySelector('.type').textContent = c.type;
    node.querySelector('.title').value = c.title || '';
    node.querySelector('.subtitle').value = c.subtitle || '';
    node.querySelector('.description').value = c.description || '';
    node.querySelector('.fields').value = JSON.stringify(c.fields || {}, null, 2);
    node.querySelector('.source').textContent = JSON.stringify(c.source || {}, null, 2);

    node.querySelector('.save').onclick = async () => {
      let fields;
      try { fields = JSON.parse(node.querySelector('.fields').value || '{}'); }
      catch(e){ alert('fields must be valid JSON'); return; }

      const payload = {
        title: node.querySelector('.title').value,
        subtitle: node.querySelector('.subtitle').value,
        description: node.querySelector('.description').value,
        fields
      };
      const res = await fetch(`${API}/cards/${c.id}`, {
        method:'PATCH', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)
      });
      if(!res.ok) return alert('save failed');
      setStatus(`Saved ${c.title}`);
      refresh();
    };

    node.querySelector('.revs').onclick = async () => {
      const panel = node.querySelector('.revpanel');
      const res = await fetch(`${API}/cards/${c.id}/revisions`);
      const revs = await res.json();
      panel.innerHTML = revs.slice().reverse().map(r =>
        `<div><code>${r.at}</code> ${r.reason} <button data-rev="${r.id}">Revert</button></div>`
      ).join('');
      panel.querySelectorAll('button[data-rev]').forEach(btn => {
        btn.onclick = async () => {
          const rev = btn.getAttribute('data-rev');
          const rr = await fetch(`${API}/cards/${c.id}/revert/${rev}`, {method:'POST'});
          if(!rr.ok) return alert('revert failed');
          setStatus('Reverted');
          refresh();
        };
      });
    };

    deck.appendChild(node);
  });
}

document.getElementById('refreshBtn').onclick = refresh;
document.getElementById('ingestBtn').onclick = async () => {
  const path = document.getElementById('folderPath').value.trim();
  if(!path) return alert('enter folder path');
  setStatus('Ingesting...');
  const res = await fetch(`${API}/ingest/folder`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({path})
  });
  const data = await res.json();
  if(!res.ok) return setStatus(`Ingest failed: ${data.detail || 'error'}`);
  setStatus(`Ingested ${data.created}. Parsed ${data.report.parsed}, skipped ${data.report.skipped}, errors ${data.report.errors.length}`);
  refresh();
};

refresh().catch(e => setStatus(`API unreachable: ${e.message}`));
