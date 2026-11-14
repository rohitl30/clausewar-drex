import asyncio
import os
import time
from pathlib import Path
from nace_sdk import AsyncNaceClient, WorkspaceFileSource

async def parse_contract_with_ndi(file_path: str, api_key: str | None = None) -> dict:
    """Uploads and parses a PDF via Nace Document Intelligence (Perception layer)."""
    t0 = time.perf_counter()
    path = Path(file_path)
    key = (api_key or os.environ.get("NACE_API_KEY", "")).strip()
    async with AsyncNaceClient(api_key=key) as client:
        uploaded = await client.documents.upload(str(path))
        ws_id = getattr(uploaded, "workspace_id", None)
        if not ws_id:
            workspaces = await client.workspaces.list()
            ws_list = getattr(workspaces, "items", workspaces)
            ws_id = ws_list[0].workspace_id if hasattr(ws_list[0], "workspace_id") else ws_list[0].id

        job = await client.documents.parse(
            WorkspaceFileSource(file_id=uploaded.file_id, workspace_id=ws_id)
        )
        completed = await client.jobs.wait(job.job_id)
        markdown_text = getattr(completed, "markdown", None) or str(completed)

    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    return {
        "file": path.name,
        "markdown": markdown_text,
        "ndi_latency_ms": latency_ms,
    }

async def parse_all_contracts(doc_paths: list[str], api_key: str | None = None) -> list[dict]:
    return await asyncio.gather(*(parse_contract_with_ndi(p, api_key=api_key) for p in doc_paths))
