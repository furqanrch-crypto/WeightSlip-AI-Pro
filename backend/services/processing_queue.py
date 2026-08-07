from __future__ import annotations

from multiprocessing import Process, Queue
from queue import Empty
from threading import Lock


_job_queue: Queue = Queue()
_worker_process: Process | None = None
_worker_lock = Lock()


def _worker_loop(job_queue: Queue) -> None:
    # Import heavy OCR stack only inside the worker process so PaddleOCR CPU work
    # cannot block FastAPI's request-serving process.
    from services.processing import process_weight_slip

    while True:
        try:
            record_id = job_queue.get()
        except (EOFError, KeyboardInterrupt):
            break

        if record_id is None:
            break

        try:
            process_weight_slip(int(record_id))
        except Exception:
            # process_weight_slip already records per-record failures in SQLite.
            # Keep the worker alive for the next queued slip.
            continue


def ensure_worker_started() -> None:
    global _worker_process

    if _worker_process is not None and _worker_process.is_alive():
        return

    with _worker_lock:
        if _worker_process is not None and _worker_process.is_alive():
            return

        worker = Process(
            target=_worker_loop,
            args=(_job_queue,),
            name="weightslip-ocr-worker",
            daemon=True,
        )
        worker.start()
        _worker_process = worker


def enqueue_record(record_id: int) -> None:
    """Queue one record for sequential OCR in a dedicated process."""
    ensure_worker_started()
    _job_queue.put(int(record_id))


def queued_jobs() -> int:
    try:
        return max(0, _job_queue.qsize())
    except (NotImplementedError, OSError):
        return 0


def worker_status() -> dict:
    return {
        "alive": bool(_worker_process and _worker_process.is_alive()),
        "pid": _worker_process.pid if _worker_process else None,
        "queued_jobs": queued_jobs(),
    }
