import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl

from app.services.scan_progress import get_steps, subscribe, unsubscribe
from app.services.security_scan_service import get_results, run_security_scan

router = APIRouter(tags=["Security Scan"])


class SecurityScanRequest(BaseModel):
    url: str


class SecurityScanStarted(BaseModel):
    scan_id: str
    status: str


@router.post("/security-scan", response_model=SecurityScanStarted, status_code=status.HTTP_201_CREATED)
async def trigger_security_scan(
    body: SecurityScanRequest,
    background_tasks: BackgroundTasks,
):
    scan_id = str(uuid4())
    background_tasks.add_task(run_security_scan, scan_id, body.url)
    return SecurityScanStarted(scan_id=scan_id, status="pending")


@router.get("/security-scan/{scan_id}/progress")
async def security_scan_progress(scan_id: str, request: Request):
    event = subscribe(scan_id)
    sent = 0

    async def stream():
        nonlocal sent
        try:
            while True:
                if await request.is_disconnected():
                    break

                steps = get_steps(scan_id)
                while sent < len(steps):
                    data = json.dumps(steps[sent])
                    yield f"data: {data}\n\n"
                    if steps[sent].get("status") in ("completed", "failed"):
                        return
                    sent += 1

                event.clear()
                try:
                    await asyncio.wait_for(event.wait(), timeout=30.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            unsubscribe(scan_id, event)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/security-scan/{scan_id}/results")
async def security_scan_results(scan_id: str):
    results = get_results(scan_id)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found or still in progress")
    return results


@router.get("/security-scan/{scan_id}/report/json")
async def security_scan_report_json(scan_id: str):
    results = get_results(scan_id)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found or still in progress")

    content = json.dumps(results, indent=2)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=security-report-{scan_id}.json"},
    )


@router.get("/security-scan/{scan_id}/report/pdf")
async def security_scan_report_pdf(scan_id: str):
    results = get_results(scan_id)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found or still in progress")

    from app.services.security_report_service import generate_security_pdf_report
    pdf_buffer = generate_security_pdf_report(results["url"], results)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=security-report-{scan_id}.pdf"},
    )
