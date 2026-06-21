from memory_pod.active_dock import (
    ActiveDock,
    active_dock_path,
    read_active_dock,
    write_active_dock,
)


def test_write_then_read_round_trips(tmp_path):
    write_active_dock("eddy", "email", home=tmp_path)

    assert read_active_dock(tmp_path) == ActiveDock(base_pod="eddy", shared_pod="email")


def test_write_without_shared_pod(tmp_path):
    write_active_dock("eddy", home=tmp_path)

    assert read_active_dock(tmp_path) == ActiveDock(base_pod="eddy", shared_pod=None)


def test_read_missing_file_returns_none(tmp_path):
    assert read_active_dock(tmp_path) is None


def test_read_corrupt_file_returns_none(tmp_path):
    active_dock_path(tmp_path).write_text("not json {", encoding="utf-8")

    assert read_active_dock(tmp_path) is None


def test_read_missing_base_pod_returns_none(tmp_path):
    active_dock_path(tmp_path).write_text('{"shared_pod": "email"}', encoding="utf-8")

    assert read_active_dock(tmp_path) is None
