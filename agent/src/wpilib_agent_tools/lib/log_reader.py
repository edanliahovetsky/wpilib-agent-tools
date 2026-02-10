"""Unified log reading for WPILOG and recorder JSON outputs."""

from __future__ import annotations

import glob
import json
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from wpilib_agent_tools.lib.wpilog_struct_decoder import decode_struct_value

try:
    from wpiutil.log import DataLogReader
except ImportError:  # pragma: no cover - depends on optional runtime dependency
    DataLogReader = None  # type: ignore[assignment]


Numeric = int | float


@dataclass(frozen=True)
class LogSummary:
    """Metadata summary for a parsed log file."""

    path: str
    format: str
    size_bytes: int
    modified_epoch: float
    start_time: float | None
    end_time: float | None
    duration_sec: float | None
    key_count: int
    sample_count: int


def decode_value(raw: bytes, type_str: str) -> Any:
    """Decode WPILOG raw bytes into Python values."""
    try:
        if type_str.startswith("struct:"):
            decoded_struct = decode_struct_value(raw, type_str)
            if decoded_struct is not None:
                return decoded_struct
            return {
                "type": "UnknownStruct",
                "wpilog_type": type_str,
                "raw_size_bytes": len(raw),
                "raw_hex": f"0x{raw.hex()}",
            }
        if type_str == "double":
            return struct.unpack("<d", raw)[0]
        if type_str == "float":
            return struct.unpack("<f", raw)[0]
        if type_str in {"int64", "integer"}:
            return struct.unpack("<q", raw)[0]
        if type_str == "boolean":
            return bool(raw[0])
        if type_str == "string":
            return raw.decode("utf-8")
        if type_str == "double[]":
            count = len(raw) // 8
            return list(struct.unpack(f"<{count}d", raw))
        if type_str == "float[]":
            count = len(raw) // 4
            return list(struct.unpack(f"<{count}f", raw))
        if type_str in {"int64[]", "integer[]"}:
            count = len(raw) // 8
            return list(struct.unpack(f"<{count}q", raw))
        if type_str == "boolean[]":
            return [bool(byte) for byte in raw]
        if type_str == "string[]":
            return raw.decode("utf-8", errors="replace").split("\x00")
        return raw
    except Exception as exc:  # pragma: no cover - corrupted bytes/runtime-specific payloads
        return f"<decode error: {exc}>"


def _record_timestamp_sec(record: Any) -> float:
    if hasattr(record, "getTimestamp"):
        return float(record.getTimestamp()) / 1_000_000.0
    return float(record.timestamp) / 1_000_000.0


def _record_entry_id(record: Any) -> int:
    if hasattr(record, "getEntry"):
        return int(record.getEntry())
    return int(record.entry)


def _record_raw(record: Any) -> bytes:
    if hasattr(record, "getRaw"):
        return bytes(record.getRaw())
    return bytes(record.data)


class LogReader:
    """Read data from `.wpilog` or recorder `.json` files."""

    def __init__(self, file_path: str | Path):
        self.path = Path(file_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Log file not found: {self.path}")
        self._json_data: dict[str, Any] | None = None

    @property
    def format(self) -> str:
        suffix = self.path.suffix.lower()
        if suffix == ".wpilog":
            return "wpilog"
        if suffix == ".json":
            return "json"
        return "unknown"

    @staticmethod
    def list_log_files(log_dir: str | Path = "agent/logs") -> list[Path]:
        """List supported log files newest-first."""
        directory = Path(log_dir)
        if not directory.exists():
            return []
        patterns = ["*.wpilog", "*.json"]
        files: list[Path] = []
        for pattern in patterns:
            files.extend(directory.glob(pattern))
        return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)

    @staticmethod
    def get_latest_log(log_dir: str | Path = "agent/logs") -> Path | None:
        files = LogReader.list_log_files(log_dir)
        return files[0] if files else None

    def _load_json(self) -> dict[str, Any]:
        if self._json_data is None:
            with self.path.open("r", encoding="utf-8") as handle:
                self._json_data = json.load(handle)
        return self._json_data

    def list_keys(self, key_filter: str | None = None) -> list[str]:
        """Return keys available in the file."""
        keys = sorted(self._iter_entry_types().keys())
        if key_filter:
            lowered = key_filter.lower()
            keys = [key for key in keys if lowered in key.lower()]
        return keys

    def _iter_entry_types(self) -> dict[str, str]:
        if self.format == "json":
            payload = self._load_json()
            entries = payload.get("entries", {})
            if not isinstance(entries, dict):
                return {}
            return {
                str(name): str(value.get("type", "unknown"))
                for name, value in entries.items()
                if isinstance(value, dict)
            }

        if self.format != "wpilog":
            raise ValueError(f"Unsupported log format for key scan: {self.path}")
        if DataLogReader is None:
            raise RuntimeError("robotpy-wpiutil is required to read .wpilog files")

        entry_types: dict[str, str] = {}
        reader = DataLogReader(str(self.path))
        for record in reader:
            if not record.isStart():
                continue
            start_data = record.getStartData()
            entry_types[str(start_data.name)] = str(start_data.type)
        return entry_types

    def get_summary(self) -> LogSummary:
        """Return file-level metadata including duration and counts."""
        stat = self.path.stat()
        start_time: float | None = None
        end_time: float | None = None
        key_count = 0
        sample_count = 0

        if self.format == "json":
            payload = self._load_json()
            entries = payload.get("entries", {})
            if isinstance(entries, dict):
                key_count = len(entries)
                for entry_data in entries.values():
                    if not isinstance(entry_data, dict):
                        continue
                    points = entry_data.get("data", [])
                    if isinstance(points, list):
                        sample_count += len(points)
                        if points:
                            first = points[0][0]
                            last = points[-1][0]
                            if isinstance(first, (int, float)):
                                start_time = first if start_time is None else min(start_time, float(first))
                            if isinstance(last, (int, float)):
                                end_time = last if end_time is None else max(end_time, float(last))
        elif self.format == "wpilog":
            if DataLogReader is None:
                raise RuntimeError("robotpy-wpiutil is required to read .wpilog files")
            reader = DataLogReader(str(self.path))
            key_names: set[str] = set()
            for record in reader:
                timestamp = _record_timestamp_sec(record)
                start_time = timestamp if start_time is None else min(start_time, timestamp)
                end_time = timestamp if end_time is None else max(end_time, timestamp)
                sample_count += 1
                if record.isStart():
                    start_data = record.getStartData()
                    key_names.add(str(start_data.name))
            key_count = len(key_names)
        else:
            raise ValueError(f"Unsupported log format: {self.path}")

        duration = None
        if start_time is not None and end_time is not None:
            duration = end_time - start_time

        return LogSummary(
            path=str(self.path),
            format=self.format,
            size_bytes=stat.st_size,
            modified_epoch=stat.st_mtime,
            start_time=start_time,
            end_time=end_time,
            duration_sec=duration,
            key_count=key_count,
            sample_count=sample_count,
        )

    def read_key_points(
        self,
        key: str,
        *,
        start: float | None = None,
        end: float | None = None,
    ) -> list[tuple[float, Any]]:
        """Return timestamp-value points for a key."""
        if self.format == "json":
            return self._read_json_key_points(key=key, start=start, end=end)
        if self.format == "wpilog":
            return self._read_wpilog_key_points(key=key, start=start, end=end)
        raise ValueError(f"Unsupported log format: {self.path}")

    def read_multiple_keys(
        self,
        keys: Iterable[str],
        *,
        start: float | None = None,
        end: float | None = None,
    ) -> dict[str, list[tuple[float, Any]]]:
        """Read points for multiple keys."""
        return {key: self.read_key_points(key, start=start, end=end) for key in keys}

    def _read_json_key_points(
        self,
        *,
        key: str,
        start: float | None,
        end: float | None,
    ) -> list[tuple[float, Any]]:
        payload = self._load_json()
        entries = payload.get("entries", {})
        if not isinstance(entries, dict):
            return []
        entry = entries.get(key)
        if not isinstance(entry, dict):
            return []
        data = entry.get("data", [])
        if not isinstance(data, list):
            return []
        points: list[tuple[float, Any]] = []
        for item in data:
            if not isinstance(item, list) or len(item) != 2:
                continue
            timestamp, value = item
            if not isinstance(timestamp, (int, float)):
                continue
            timestamp = float(timestamp)
            if start is not None and timestamp < start:
                continue
            if end is not None and timestamp > end:
                continue
            points.append((timestamp, value))
        return points

    def _read_wpilog_key_points(
        self,
        *,
        key: str,
        start: float | None,
        end: float | None,
    ) -> list[tuple[float, Any]]:
        if DataLogReader is None:
            raise RuntimeError("robotpy-wpiutil is required to read .wpilog files")

        reader = DataLogReader(str(self.path))
        entry_by_id: dict[int, tuple[str, str]] = {}
        target_ids: set[int] = set()
        points: list[tuple[float, Any]] = []

        for record in reader:
            if record.isStart():
                start_data = record.getStartData()
                entry_id = int(start_data.entry)
                entry_name = str(start_data.name)
                entry_type = str(start_data.type)
                entry_by_id[entry_id] = (entry_name, entry_type)
                if entry_name == key:
                    target_ids.add(entry_id)
                continue

            if record.isFinish() or record.isSetMetadata() or record.isControl():
                continue

            entry_id = _record_entry_id(record)
            if entry_id not in target_ids:
                continue

            timestamp = _record_timestamp_sec(record)
            if start is not None and timestamp < start:
                continue
            if end is not None and timestamp > end:
                continue

            _, entry_type = entry_by_id.get(entry_id, ("", "unknown"))
            raw = _record_raw(record)
            points.append((timestamp, decode_value(raw, entry_type)))

        return points


def expand_log_glob(path_or_glob: str) -> list[str]:
    """Expand shell-style globs while preserving direct file paths."""
    if any(token in path_or_glob for token in "*?[]"):
        return sorted(glob.glob(path_or_glob))
    return [path_or_glob]


def ensure_log_file(file_path: str | None, log_dir: str = "agent/logs") -> str:
    """Resolve default log file selection if `file_path` is omitted."""
    if file_path:
        return file_path
    latest = LogReader.get_latest_log(log_dir)
    if latest is None:
        raise FileNotFoundError(f"No log files found in {os.path.abspath(log_dir)}")
    return str(latest)
