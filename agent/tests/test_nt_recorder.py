from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import pytest

from wpilib_agent_tools.lib.nt_recorder import NTRecorder, _parse_address

ntcore = pytest.importorskip("ntcore")


@pytest.fixture(autouse=True)
def _reset_default_networktables_instance() -> None:
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.stopClient()
    inst.stopServer()
    yield
    inst.stopClient()
    inst.stopServer()


def _find_open_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        ("localhost", ("localhost", None)),
        ("127.0.0.1:5810", ("127.0.0.1", 5810)),
        ("[::1]:5810", ("::1", 5810)),
        ("::1", ("::1", None)),
    ],
)
def test_parse_address_valid(address: str, expected: tuple[str, int | None]) -> None:
    assert _parse_address(address) == expected


@pytest.mark.parametrize(
    "address",
    [
        "",
        "127.0.0.1:",
        "[::1",
        "host:abc",
        "host:70000",
    ],
)
def test_parse_address_invalid(address: str) -> None:
    with pytest.raises(RuntimeError, match="Invalid NT4 server address|cannot be empty"):
        _parse_address(address)


def _publish_loop(
    stop_event: threading.Event,
    ready_event: threading.Event,
    persist_file: Path,
    nt4_port: int,
) -> None:
    server = ntcore.NetworkTableInstance.create()
    # Avoid writing default networktables.json into the repo cwd.
    server.startServer(str(persist_file), "127.0.0.1", 0, nt4_port)
    value_pub = server.getDoubleTopic("/RecorderTest/Value").publish()
    enabled_pub = server.getBooleanTopic("/RecorderTest/Enabled").publish()
    ready_event.set()

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
    port = _find_open_port()
    stop_event = threading.Event()
    ready_event = threading.Event()
    publisher = threading.Thread(
        target=_publish_loop,
        args=(stop_event, ready_event, tmp_path / "networktables_persist.json", port),
        daemon=True,
    )
    publisher.start()
    assert ready_event.wait(timeout=2.0)

    try:
        recorder = NTRecorder(
            address=f"127.0.0.1:{port}",
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
    unused_port = _find_open_port()
    recorder = NTRecorder(
        address=f"127.0.0.1:{unused_port}",
        duration_sec=1.0,
        output_dir=tmp_path,
    )
    with pytest.raises(RuntimeError, match="Unable to connect to NT4 server"):
        recorder.record(output_file="unreachable.wpilog")
