import asyncio
from collections import defaultdict

_progress: dict[str, list[dict]] = {}
_events: dict[str, list[asyncio.Event]] = defaultdict(list)


def emit(scan_id: str, step: str, detail: str = "", status: str = "running", phase: str = "") -> None:
    entry = {"step": step, "detail": detail, "status": status, "phase": phase}
    _progress.setdefault(scan_id, []).append(entry)
    for event in _events.get(scan_id, []):
        event.set()


def get_steps(scan_id: str) -> list[dict]:
    return list(_progress.get(scan_id, []))


def subscribe(scan_id: str) -> asyncio.Event:
    event = asyncio.Event()
    _events[scan_id].append(event)
    return event


def unsubscribe(scan_id: str, event: asyncio.Event) -> None:
    listeners = _events.get(scan_id, [])
    if event in listeners:
        listeners.remove(event)
    if not listeners:
        _events.pop(scan_id, None)


def cleanup(scan_id: str) -> None:
    _progress.pop(scan_id, None)
    _events.pop(scan_id, None)
