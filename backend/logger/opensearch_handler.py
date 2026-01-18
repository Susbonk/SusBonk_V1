import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx


def utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class OpenSearchIngestHandler(logging.Handler):
    """
    Async log shipping handler.

    Sends events to an HTTP ingest endpoint (e.g. your ingestd at /ingest),
    batching by size or by interval.

    IMPORTANT:
    - Call `await handler.start()` once after event loop is available.
    - Call `await handler.aclose()` on shutdown to flush & close http client.
    """

    def __init__(
        self,
        *,
        ingest_url: str,
        service_name: str,
        level: int = logging.INFO,
        timeout_s: float = 5.0,
        max_connections: int = 20,
        max_keepalive_connections: int = 10,
        keepalive_expiry_s: float = 30.0,
        batch_size: int = 200,
        flush_interval_s: float = 1.0,
        max_queue: int = 10_000,
        extra_fields: Optional[Dict[str, Any]] = None,
        verify_tls: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(level=level)

        self.ingest_url = ingest_url.rstrip("/")
        self.service_name = service_name
        self.batch_size = batch_size
        self.flush_interval_s = flush_interval_s
        self.extra_fields = extra_fields or {}

        self._queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue(maxsize=max_queue)  # noqa: E501
        self._stop = asyncio.Event()
        self._task: Optional[asyncio.Task[None]] = None

        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry_s,
        )
        self._client = httpx.AsyncClient(
            timeout=timeout_s,
            limits=limits,
            verify=verify_tls,
            headers=headers,
        )

        # Prevent recursive logging if this handler triggers logs internally
        self._shipping = False

    async def start(self) -> None:
        """Start background flusher task."""
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._run(), name="os-log-shipper")

    def emit(self, record: logging.LogRecord) -> None:
        """
        NOTE: logging calls this from sync context.

        We enqueue and return immediately. If queue is full, we drop.
        """
        if self._shipping:
            return

        try:
            event = self._record_to_event(record)
        except Exception:
            # Never raise from emit: logging must not crash the app
            return

        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            # Drop on overload (or you can implement "drop oldest" strategy)
            return

    def _record_to_event(self, record: logging.LogRecord) -> Dict[str, Any]:
        ts = (
            datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

        event: Dict[str, Any] = {
            "@timestamp": ts,
            "service": {"name": self.service_name},
            "log": {"level": record.levelname},
            "message": record.getMessage(),
        }

        fields: Dict[str, Any] = dict(self.extra_fields)

        fields.update(
            {
                "logger": record.name,
                "process": {"pid": record.process},
                "thread": {"id": record.thread, "name": record.threadName},
                "source": {
                    "file": record.pathname,
                    "line": record.lineno,
                    "func": record.funcName,
                },
            }
        )

        if record.exc_info:
            exc_type, exc, _tb = record.exc_info
            fields["exception"] = {
                "type": getattr(exc_type, "__name__", str(exc_type)),
                "message": str(exc),
            }

        # user extra fields pattern: extra={"fields": {...}}
        extra_fields = getattr(record, "fields", None)
        if isinstance(extra_fields, dict):
            fields.update(extra_fields)

        # optional: trace id if you attach it like extra={"trace_id": "..."}
        trace_id = getattr(record, "trace_id", None)
        if trace_id is not None:
            event["trace"] = {"id": str(trace_id)}

        # optional: labels if you attach dict like extra={"labels": {...}}
        labels = getattr(record, "labels", None)
        if isinstance(labels, dict):
            event["labels"] = labels

        if fields:
            event["fields"] = fields

        return event

    async def _run(self) -> None:
        """
        Background loop: flush by batch size or interval.
        """
        buf: list[Dict[str, Any]] = []
        try:
            while not self._stop.is_set():
                try:
                    item = await asyncio.wait_for(
                        self._queue.get(), timeout=self.flush_interval_s
                    )
                    buf.append(item)
                    # drain quickly up to batch_size
                    while len(buf) < self.batch_size:
                        try:
                            buf.append(self._queue.get_nowait())
                        except asyncio.QueueEmpty:
                            break
                except asyncio.TimeoutError:
                    pass  # time-based flush

                if buf:
                    await self._flush(buf)
                    buf.clear()

            # final drain on stop
            while True:
                try:
                    buf.append(self._queue.get_nowait())
                    if len(buf) >= self.batch_size:
                        await self._flush(buf)
                        buf.clear()
                except asyncio.QueueEmpty:
                    break
            if buf:
                await self._flush(buf)
        finally:
            await self._client.aclose()

    async def _flush(self, batch: list[Dict[str, Any]]) -> None:
        """
        Send logs batch to ingest endpoint.
        Never throws.
        """
        self._shipping = True
        try:
            # Your ingest service expects JSON list of events:
            # POST /ingest  [ {...}, {...} ]
            resp = await self._client.post(self.ingest_url, json=batch)
            # if it fails, we drop (or you can implement retry/backoff)
            if resp.status_code >= 400:
                print(
                    f"opensearch ingest failed: {resp.status_code} "
                    f"- {resp.text}"
                )
                return
        except Exception:
            return
        finally:
            self._shipping = False

    async def aclose(self) -> None:
        """Signal stop, flush, close."""
        self._stop.set()
        if self._task:
            try:
                await self._task
            finally:
                self._task = None
