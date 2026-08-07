from __future__ import annotations

from queue import Queue
from threading import Lock, Thread

from services.processing import process_weight_slip


_job_queue: Queue[int] = Queue()
_worker_started = False
_worker_lock = Lock()


def _worker_loop() -> None:
    while True:
        record_id = _job_queue.get()
        try:
            process_weight_slip(record_id)
        finally:
            _job_queue.task_done()


def ensure_worker_started() -> None:
    global _worker_started

    if _worker_started:
        return

    with _worker_lock:
        if _worker_started:
            return

        worker = Thread(
            target=_worker_loop,
            name="weightslip-ocr-worker",
            daemon=True,
        )
        worker.start()
        _worker_started = True


def enqueue_record(record_id: int) -> None:
    """Queue one record for sequential OCR processing.

    A single worker keeps heavy PaddleOCR inference away from request handling and
    prevents many simultaneous OCR jobs from exhausting a Codespace CPU/RAM.
    """
    ensure_worker_started()
    _job_queue.put(record_id)


def queued_jobs() -> int:
    return _job_queue.qsize()
