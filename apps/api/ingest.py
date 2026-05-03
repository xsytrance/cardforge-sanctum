from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import csv, json, re
import yaml
from openpyxl import load_workbook

TEXT_EXT = {'.md', '.txt'}
STRUCT_EXT = {'.json', '.yaml', '.yml'}
TABLE_EXT = {'.csv', '.xlsx'}

KEY_PATTERNS = {
    'model': re.compile(r'\bmodel\b\s*[:=]\s*(.+)', re.I),
    'personality': re.compile(r'\bpersonality\b\s*[:=]\s*(.+)', re.I),
    'heartbeat': re.compile(r'\bheartbeat\b\s*[:=]\s*(.+)', re.I),
    'soul': re.compile(r'\bsoul\b\s*[:=]\s*(.+)', re.I),
    'port': re.compile(r'\bport\b\s*[:=]\s*(.+)', re.I),
    'host': re.compile(r'\bhost\b\s*[:=]\s*(.+)', re.I),
    'server': re.compile(r'\bserver\b\s*[:=]\s*(.+)', re.I),
    'app_name': re.compile(r'\bapp[_\- ]?name\b\s*[:=]\s*(.+)', re.I),
}


def infer_type(name: str, fields: Dict[str, Any]) -> Tuple[str, float]:
    n = name.lower()
    if any(k in fields for k in ['model','personality','heartbeat','soul']) or 'agent' in n:
        return 'agent', 0.9
    if any(k in fields for k in ['port','host','server','app_name']) or 'service' in n:
        return 'service', 0.88
    if 'table_preview' in fields or 'chart_suggestions' in fields or 'dataset' in n:
        return 'dataset', 0.86
    return 'note', 0.6


def extract_kv_from_text(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, pat in KEY_PATTERNS.items():
        m = pat.search(text)
        if m:
            out[key] = m.group(1).strip()
    return out


def parse_text(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = lines[0][:120] if lines else path.stem
    description = '\n'.join(lines[1:8])[:600]
    fields = extract_kv_from_text(text)
    return {'title': title, 'description': description, 'fields': fields}


def parse_json_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding='utf-8', errors='ignore')
    data = json.loads(raw) if path.suffix.lower()=='.json' else yaml.safe_load(raw)
    if not isinstance(data, dict):
        data = {'value': data}
    title = str(data.get('name') or data.get('title') or path.stem)
    description = str(data.get('description') or '')
    fields = {k:v for k,v in data.items() if k not in {'name','title','description'}}
    return {'title': title, 'description': description, 'fields': fields}


def parse_csv(path: Path) -> Dict[str, Any]:
    rows = []
    with path.open('r', encoding='utf-8', errors='ignore', newline='') as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            rows.append(r)
            if i >= 19:
                break
    fields = {
        'table_preview': rows,
        'row_count_preview': len(rows),
        'chart_suggestions': ['bar','line','pie']
    }
    return {'title': path.stem, 'description': 'Dataset imported from CSV', 'fields': fields}


def parse_xlsx(path: Path) -> Dict[str, Any]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True, max_row=21))
    headers = [str(h) for h in rows[0]] if rows else []
    preview = []
    for row in rows[1:]:
        preview.append({headers[i] if i < len(headers) else f'col_{i}': row[i] for i in range(len(row))})
    fields = {
        'sheet': ws.title,
        'columns': headers,
        'table_preview': preview,
        'row_count_preview': len(preview),
        'chart_suggestions': ['bar','line','scatter']
    }
    return {'title': path.stem, 'description': 'Dataset imported from XLSX', 'fields': fields}


def ingest_folder(folder: str) -> Dict[str, Any]:
    p = Path(folder).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f'Folder not found: {p}')

    cards: List[Dict[str, Any]] = []
    report = {'parsed': 0, 'skipped': 0, 'errors': []}

    for fp in p.rglob('*'):
        if not fp.is_file():
            continue
        ext = fp.suffix.lower()
        try:
            if ext in TEXT_EXT:
                parsed = parse_text(fp); parser='text'
            elif ext in STRUCT_EXT:
                parsed = parse_json_yaml(fp); parser='structured'
            elif ext == '.csv':
                parsed = parse_csv(fp); parser='csv'
            elif ext == '.xlsx':
                parsed = parse_xlsx(fp); parser='xlsx'
            else:
                report['skipped'] += 1
                continue

            ctype, conf = infer_type(fp.name, parsed.get('fields', {}))
            cards.append({
                'type': ctype,
                'title': parsed.get('title', fp.stem),
                'subtitle': fp.name,
                'description': parsed.get('description', ''),
                'fields': parsed.get('fields', {}),
                'source': {
                    'path': str(fp),
                    'parser': parser,
                    'confidence': conf,
                    'editable_fields': ['title','subtitle','description','fields']
                }
            })
            report['parsed'] += 1
        except Exception as e:
            report['errors'].append({'file': str(fp), 'error': str(e)})

    return {'cards': cards, 'report': report}
