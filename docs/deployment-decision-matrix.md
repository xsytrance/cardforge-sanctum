# Deployment Decision Matrix

## Candidate Runtime Targets

### PRIME
- Use when: personal command sanctum, low-latency local workflows
- Suggested ports: web `13000`, api `18000`, worker internal

### VPS
- Use when: externally accessible demo / shared access
- Suggested ports: web `23000`, api `28000`

### PLUTO / VENUS
- Use when: dedicated workload segmentation is required

## Required Runtime Metadata on Service Cards
- app_name
- server_name
- internal_port
- public_url
- health_endpoint
- owner
- purpose
