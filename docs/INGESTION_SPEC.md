# Ingestion Specification

## Supported file types
- Text: `.md`, `.txt`
- Structured: `.json`, `.yaml`, `.yml`
- Tabular: `.csv`, `.xlsx`

## Normalized card payload
```json
{
  "type":"dataset",
  "title":"Revenue Q1",
  "subtitle":"revenue.csv",
  "description":"Dataset imported from CSV",
  "fields":{},
  "source":{
    "path":"/abs/path/revenue.csv",
    "parser":"csv",
    "confidence":0.86,
    "editable_fields":["title","subtitle","description","fields"]
  }
}
```

## Inference rules
- `agent` if model/personality/heartbeat/soul indicators found
- `service` if host/port/server/app_name indicators found
- `dataset` if table preview or chart suggestions present
- else `note`

## Dataset chart requirements
Frontend auto-chart works when:
- `fields.table_preview` is non-empty array of objects
- first column can be treated as x-axis labels
- at least one later column has numeric values

## Error handling
Parser exceptions are captured in ingest report:
```json
{"file":"...","error":"..."}
```
Ingest continues with remaining files.
