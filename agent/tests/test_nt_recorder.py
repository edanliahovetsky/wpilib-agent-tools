from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from wpilib_agent_tools.lib.nt_recorder import NTRecorder

ntcore = pytest.importorskip("ntcore")


def _publish_loop(stop_event: threading.Event, persist_file: Path) -> None:
    server = ntcore.NetworkTableInstance.create()
    # Avoid writing default networktables.json into the repo cwd.
    server.startServer(str(persist_file))
    value_pub = server.getDoubleTopic("/RecorderTest/Value").publish()
    enabled_pub = server.getBooleanTopic("/RecorderTest/Enabled").publish()

    counter = 0
    try:
        while not stop_event.is_set():
            value_pub.set(float(counter))
            enabled_pub.set(counter % 2 == 0)
            counter += 1
            time.sleep(0.02)
    finally:
        server.stopServer()


def test_record_collects_values_from_reachable_server(tmp_path: Path) -> None:
    stop_event = threading.Event()
    publisher = threading.Thread(
        target=_publish_loop,
        args=(stop_event, tmp_path / "networktables_persist.json"),
        daemon=True,
    )
    publisher.start()
    time.sleep(0.3)

    try:
        recorder = NTRecorder(
            address="localhost",
            duration_sec=1.2,
            key_prefixes=["/RecorderTest"],
            output_dir=tmp_path,
            poll_interval_sec=0.02,
        )
        result = recorder.record(output_file="reachable.wpilog")
    finally:
        stop_event.set()
        publisher.join(timeout=2.0)

    assert result.topic_count >= 1
    assert result.sample_count > 0
    assert Path(result.output_file).exists()


def test_record_fails_when_server_unreachable(tmp_path: Path) -> None:
    recorder = NTRecorder(
        address="192.0.2.1",
        duration_sec=1.0,
        output_dir=tmp_path,
    )
    with pytest.raises(RuntimeError, match="Unable to connect to NT4 server"):
        recorder.record(output_file="unreachable.wpilog")
