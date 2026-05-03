# CardForge Implementation Plan

## Goal
Create a system that ingests heterogeneous folders and renders editable, mobile-first trading-card style views.

## Phases
1. Foundation: schema, storage, API skeleton
2. Ingestion: parser + mapper + confidence score
3. UI: mobile card renderer + theme system
4. Editing: inline edits + revision history
5. Connectors: Hermes/OpenClaw + service cards + spreadsheet charts
6. Deploy: server/port mapping + health endpoints

## 7-Day Sprint
- Day 1: schema + DB tables + sample cards
- Day 2: md/json/yaml/txt parser
- Day 3: card UI + responsive interactions
- Day 4: editor + save + revisions
- Day 5: service metadata mapping
- Day 6: csv/xlsx chart cards
- Day 7: deploy + demo + polish

## Non-Negotiables
- Mobile-first (thumb-friendly)
- Source provenance per field
- Revisions/diff for every edit
- Fallback cards when parser confidence is low
