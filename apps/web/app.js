const API = 'http://127.0.0.1:18000';
const deck = document.getElementById('deck');
const statusEl = document.getElementById('status');
const liveCharts = [];

function setStatus(msg){ statusEl.textContent = msg; }
function fmt(obj){ return JSON.stringify(obj, null, 2); }

async function api(path, options={}){
  const res = await fetch(`${API}${path}`, options);
  const data = await res.json().catch(() => ({}));
  if(!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

function destroyCharts(){ while(liveCharts.length){ liveCharts.pop().destroy(); } }

function buildChartData(fields){
  const rows = fields?.table_preview;
  if(!Array.isArray(rows) || rows.length === 0) return null;
  const keys = Object.keys(rows[0]);
  if(keys.length < 2) return null;

  const xKey = keys[0];
  const yCandidates = keys.slice(1);
  const yKey = yCandidates.find(k => rows.some(r => Number.isFinite(Number(r[k]))));
  if(!yKey) return null;

  const labels = rows.map(r => String(r[xKey] ?? ''));
  const values = rows.map(r => Number(r[yKey] ?? 0));
  const typePref = (fields?.chart_suggestions || [])[0] || 'bar';
  const chartType = ['bar','line','pie','scatter'].includes(typePref) ? typePref : 'bar';

  return { chartType, labels, values, xKey, yKey };
}

async function refresh(){
  const cards = await api('/cards');
  render(cards);
  setStatus(`Loaded ${cards.length} cards`);
}

function render(cards){
  destroyCharts();
  deck.innerHTML = '';
  const tpl = document.getElementById('cardTpl');

  cards.forEach(c => {
    const node = tpl.content.cloneNode(true);
    node.querySelector('.type').textContent = c.type;
    node.querySelector('.title').value = c.title || '';
    node.querySelector('.subtitle').value = c.subtitle || '';
    node.querySelector('.description').value = c.description || '';
    node.querySelector('.fields').value = fmt(c.fields || {});
    node.querySelector('.source').textContent = fmt(c.source || {});

    const chartCanvas = node.querySelector('.chart');
    const chartCfg = c.type === 'dataset' ? buildChartData(c.fields) : null;
    if(chartCfg){
      const chart = new Chart(chartCanvas, {
        type: chartCfg.chartType,
        data: {
          labels: chartCfg.labels,
          datasets: [{
            label: `${chartCfg.yKey} by ${chartCfg.xKey}`,
            data: chartCfg.values,
            borderColor: '#6ef3ff',
            backgroundColor: ['#6ef3ff88','#ff4fd888','#58ff9f88','#ffd16688','#9b5de588']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
      liveCharts.push(chart);
    } else {
      chartCanvas.parentElement.innerHTML = '<small>No chartable numeric series found in table_preview.</small>';
    }

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

      await api(`/cards/${c.id}`, {
        method: 'PATCH',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      setStatus(`Saved ${payload.title}`);
      refresh();
    };

    node.querySelector('.revs').onclick = async () => {
      const panel = node.querySelector('.revpanel');
      const revs = await api(`/cards/${c.id}/revisions`);
      panel.innerHTML = revs.map(r =>
        `<div><code>${r.at}</code> ${r.reason} <button data-rev="${r.id}">Revert</button></div>`
      ).join('');
      panel.querySelectorAll('button[data-rev]').forEach(btn => {
        btn.onclick = async () => {
          const rev = btn.getAttribute('data-rev');
          await api(`/cards/${c.id}/revert/${rev}`, {method:'POST'});
          setStatus('Reverted');
          refresh();
        };
      });
    };

    deck.appendChild(node);
  });
}

document.getElementById('refreshBtn').onclick = () => refresh().catch(e => setStatus(`Refresh failed: ${e.message}`));
document.getElementById('ingestBtn').onclick = async () => {
  const path = document.getElementById('folderPath').value.trim();
  if(!path) return alert('enter folder path');
  setStatus('Ingesting...');
  try {
    const data = await api('/ingest/folder', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({path})
    });
    setStatus(`Ingested/updated ${data.created_or_updated}. Parsed ${data.report.parsed}, skipped ${data.report.skipped}, errors ${data.report.errors.length}`);
    refresh();
  } catch(e){ setStatus(`Ingest failed: ${e.message}`); }
};

document.getElementById('watchStartBtn').onclick = async () => {
  const path = document.getElementById('folderPath').value.trim();
  if(!path) return alert('enter folder path');
  const debounce = Number(document.getElementById('debounce').value || '2');
  try {
    const s = await api('/watch/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({path, debounce_seconds: debounce})});
    setStatus(`Watch started:\n${fmt(s)}`);
  } catch(e){ setStatus(`Watch start failed: ${e.message}`); }
};

document.getElementById('watchStopBtn').onclick = async () => {
  try {
    const s = await api('/watch/stop', {method:'POST'});
    setStatus(`Watch stopped:\n${fmt(s)}`);
  } catch(e){ setStatus(`Watch stop failed: ${e.message}`); }
};

document.getElementById('watchStatusBtn').onclick = async () => {
  try {
    const s = await api('/watch/status');
    setStatus(`Watch status:\n${fmt(s)}`);
  } catch(e){ setStatus(`Watch status failed: ${e.message}`); }
};

refresh().catch(e => setStatus(`API unreachable: ${e.message}`));
