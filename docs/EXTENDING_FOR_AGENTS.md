# Extending CardForge for Agent Ecosystems

## Goal
Teach multiple AI agents a shared contract for card generation.

## Recommended contract versioning
- Add `fields._contract_version` (e.g., `cardforge.v1`).
- Add `source.agent` (agent identity) for provenance chain.
- Add `source.ingested_at` UTC timestamp.

## Suggested metadata conventions
For agent profiles:
- `fields.model`
- `fields.personality`
- `fields.heartbeat`
- `fields.soul`
- `fields.capabilities` (array)

For services:
- `fields.host`
- `fields.port`
- `fields.server`
- `fields.app_name`
- `fields.health_endpoint`

For datasets:
- `fields.table_preview`
- `fields.chart_suggestions`
- `fields.units`
- `fields.primary_metric`

## Integration pattern
1. Agent emits raw source files to a known folder.
2. CardForge ingests folder (or watches continuously).
3. Web deck becomes shared operational surface.
4. Agents can patch cards through API and leave revision trail.
