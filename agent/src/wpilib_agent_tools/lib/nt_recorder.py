"""NetworkTables recording utilities."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # pragma: no cover - runtime dependency
    import ntcore
except ImportError:  # pragma: no cover - runtime dependency
    ntcore = None  # type: ignore[assignment]


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, bytes):
        return list(value)
    if hasattr(value, "tolist"):
        return value.tolist()
    return str(value)


def _extract_entry_value(entry: Any) -> Any:
    """Get an entry value across RobotPy API variations."""
    for method_name in ("getValue", "value"):
        method = getattr(entry, method_name, None)
        if callable(method):
            try:
                maybe = method()
                if hasattr(maybe, "isValid") and callable(maybe.isValid) and not maybe.isValid():
                    return None
                if hasattr(maybe, "value") and callable(maybe.value):
                    return _jsonable(maybe.value())
                if hasattr(maybe, "getValue") and callable(maybe.getValue):
                    return _jsonable(maybe.getValue())
                return _jsonable(maybe)
            except Exception:
                continue
    return None


def _extract_value_payload(value_obj: Any) -> Any:
    """Convert an ntcore Value-like object into JSON-compatible data."""
    if value_obj is None:
        return None

    # RobotPy ntcore Value objects expose isValid()/value().
    valid = getattr(value_obj, "isValid", None)
    if callable(valid):
        try:
            if not bool(valid()):
                return None
        except Exception:
            return None

    candidate = value_obj
    for method_name in ("value", "getValue"):
        method = getattr(candidate, method_name, None)
        if callable(method):
            try:
                candidate = method()
            except Exception:
                continue
            break

    return _jsonable(candidate)


@dataclass(frozen=True)
class RecordingResult:
    """Return value from a completed recording."""

    output_file: str
    address: str
    duration_sec: float
    topic_count: int
    sample_count: int


class NTRecorder:
    """Best-effort polling recorder for NetworkTables values."""

    def __init__(
        self,
        *,
        address: str,
        duration_sec: float,
        key_prefixes: list[str] | None = None,
        output_dir: str | Path = "agent/logs",
        poll_interval_sec: float = 0.02,
    ) -> None:
        self.address = address
        self.duration_sec = duration_sec
        self.key_prefixes = key_prefixes or []
        self.output_dir = Path(output_dir)
        self.poll_interval_sec = poll_interval_sec

    def _match_key(self, key: str) -> bool:
        if not self.key_prefixes:
            return True
        lowered = key.lower()
        for prefix in self.key_prefixes:
            if lowered.startswith(prefix.lower()):
                return True
        return False

    def _wait_for_connection(self, inst: Any) -> None:
        # Give NT4 a short grace period to establish transport before sampling.
        timeout = max(0.5, min(5.0, self.duration_sec * 0.5))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                if inst.isConnected():
                    return
            except Exception:
                pass
            time.sleep(0.05)
        raise RuntimeError(
            f"Unable to connect to NT4 server at '{self.address}' within {timeout:.1f}s."
        )

    def _record_with_listener(
        self,
        *,
        inst: Any,
        start_mono: float,
        topic_types: dict[str, str],
        topic_data: dict[str, list[list[Any]]],
        last_values: dict[str, Any],
    ) -> None:
        prefixes = self.key_prefixes or [""]
        subscriber = ntcore.MultiSubscriber(inst, prefixes)
        poller = ntcore.NetworkTableListenerPoller(inst)
        event_flags = ntcore.EventFlags.kPublish | ntcore.EventFlags.kValueAll
        poller.addListener(subscriber, int(event_flags))
        try:
            while True:
                elapsed = time.monotonic() - start_mono
                if elapsed >= self.duration_sec:
                    break

                for event in poller.readQueue():
                    data = getattr(event, "data", None)
                    if data is None:
                        continue

                    if isinstance(data, ntcore.TopicInfo):
                        name = str(data.name)
                        if not self._match_key(name):
                            continue
                        type_str = str(getattr(data, "type_str", "unknown"))
                        topic_types.setdefault(name, type_str)
                        continue

                    if isinstance(data, ntcore.ValueEventData):
                        try:
                            name = str(data.topic.getName())
                        except Exception:
                            continue
                        if not self._match_key(name):
                            continue

                        value = _extract_value_payload(getattr(data, "value", None))
                        if value is None:
                            continue
                        if name in last_values and last_values[name] == value:
                            continue

                        last_values[name] = value
                        topic_data.setdefault(name, []).append([round(elapsed, 6), value])
                        continue

                time.sleep(self.poll_interval_sec)
        finally:
            try:
                poller.close()
            finally:
                subscriber.close()

    def _record_with_topic_scan(
        self,
        *,
        inst: Any,
        start_mono: float,
        topic_types: dict[str, str],
        topic_data: dict[str, list[list[Any]]],
        last_values: dict[str, Any],
    ) -> None:
        # Fallback path for environments without listener APIs.
        while True:
            elapsed = time.monotonic() - start_mono
            if elapsed >= self.duration_sec:
                break

            try:
                topics = inst.getTopics()
            except Exception:
                topics = []

            for topic in topics:
                try:
                    name = str(topic.getName())
                except Exception:
                    continue
                if not self._match_key(name):
                    continue

                topic_types.setdefault(name, str(getattr(topic, "getTypeString", lambda: "unknown")()))
                entry = inst.getEntry(name)
                value = _extract_entry_value(entry)
                if value is None:
                    continue
                if name in last_values and last_values[name] == value:
                    continue
                last_values[name] = value
                topic_data.setdefault(name, []).append([round(elapsed, 6), value])

            time.sleep(self.poll_interval_sec)

    def record(self, output_file: str | Path | None = None) -> RecordingResult:
        """Record values for the configured duration and write JSON output."""
        if ntcore is None:
            raise RuntimeError(
                "pyntcore is required for `record`. Install dependencies first."
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        if output_file is None:
            stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"nt_record_{stamp}.json"
        else:
            output_path = Path(output_file)
            if not output_path.is_absolute():
                output_path = self.output_dir / output_path

        inst = ntcore.NetworkTableInstance.getDefault()
        inst.stopServer()
        inst.stopClient()
        inst.startClient4("wpilib-agent-tools-recorder")
        inst.setServer(self.address)
        self._wait_for_connection(inst)

        start_wall = datetime.now(tz=timezone.utc).isoformat()
        start_mono = time.monotonic()
        topic_types: dict[str, str] = {}
        topic_data: dict[str, list[list[Any]]] = {}
        last_values: dict[str, Any] = {}

        try:
            if all(hasattr(ntcore, attr) for attr in ("MultiSubscriber", "NetworkTableListenerPoller", "TopicInfo", "ValueEventData")):
                self._record_with_listener(
                    inst=inst,
                    start_mono=start_mono,
                    topic_types=topic_types,
                    topic_data=topic_data,
                    last_values=last_values,
                )
            else:
                self._record_with_topic_scan(
                    inst=inst,
                    start_mono=start_mono,
                    topic_types=topic_types,
                    topic_data=topic_data,
                    last_values=last_values,
                )
        finally:
            inst.stopClient()

        entries: dict[str, Any] = {}
        sample_count = 0
        for key, series in topic_data.items():
            sample_count += len(series)
            entries[key] = {
                "type": topic_types.get(key, "unknown"),
                "data": series,
            }

        payload = {
            "source": "NT4",
            "address": self.address,
            "start_time": start_wall,
            "duration_sec": round(time.monotonic() - start_mono, 6),
            "entries": entries,
        }
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        return RecordingResult(
            output_file=str(output_path),
            address=self.address,
            duration_sec=float(payload["duration_sec"]),
            topic_count=len(entries),
            sample_count=sample_count,
        )
