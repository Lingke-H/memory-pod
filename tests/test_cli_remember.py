import memory_pod.cli as cli
from memory_pod.memory_store import MemoryRecord


def test_remember_subcommand_calls_remember(monkeypatch, capsys):
    calls = {}

    def fake_remember(text, profile="alice", tags=None, **kwargs):
        calls["text"] = text
        calls["profile"] = profile
        calls["tags"] = tags
        return MemoryRecord(id="manual_test", text=text)

    monkeypatch.setattr(cli, "remember", fake_remember)
    monkeypatch.setattr(
        "sys.argv",
        ["memory-pod", "remember", "Alice won a Rhodes scholarship.", "--profile", "alice", "--tag", "bio"],
    )

    cli.main()

    assert calls["text"] == "Alice won a Rhodes scholarship."
    assert calls["profile"] == "alice"
    assert calls["tags"] == ["bio"]

    out = capsys.readouterr().out
    assert "Remembered for 'alice'" in out
    assert "Alice won a Rhodes scholarship." in out


def test_remember_subcommand_defaults_tags_to_empty_list(monkeypatch):
    captured = {}

    def fake_remember(text, profile="alice", tags=None, **kwargs):
        captured["tags"] = tags
        return MemoryRecord(id="manual_test", text=text)

    monkeypatch.setattr(cli, "remember", fake_remember)
    monkeypatch.setattr("sys.argv", ["memory-pod", "remember", "Some fact"])

    cli.main()

    assert captured["tags"] == []
