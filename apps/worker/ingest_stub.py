"""Worker stub for Phase 2 ingestion pipeline."""

def ingest_folder(path: str) -> dict:
    return {
        "status": "queued",
        "path": path,
        "note": "Implement parser chain: md/json/yaml/txt/csv/xlsx"
    }
