import memory_pod.cli as cli
from memory_pod.augment import AugmentResult
from memory_pod.pods import PodManifest


def test_pod_create_command(monkeypatch, capsys):
    captured = {}

    def fake_create_pod(**kwargs):
        captured.update(kwargs)
        return PodManifest(
            id="senior-review",
            name=kwargs["name"],
            kind=kwargs["kind"],
        )

    monkeypatch.setattr(cli, "create_pod", fake_create_pod)
    monkeypatch.setattr(
        "sys.argv",
        [
            "memory-pod",
            "pod",
            "create",
            "--name",
            "Senior Review",
            "--id",
            "senior-review",
            "--kind",
            "shared",
        ],
    )

    cli.main()

    assert captured["pod_id"] == "senior-review"
    assert captured["kind"] == "shared"
    assert "Created shared Pod" in capsys.readouterr().out


def test_pod_export_command(monkeypatch, capsys, tmp_path):
    output = tmp_path / "review.mpod"
    captured = {}

    def fake_export(pod_id, output_path):
        captured["pod_id"] = pod_id
        captured["output"] = output_path
        return output

    monkeypatch.setattr(cli, "export_pod", fake_export)
    monkeypatch.setattr(
        "sys.argv",
        [
            "memory-pod",
            "pod",
            "export",
            "senior-review",
            "--output",
            str(output),
        ],
    )

    cli.main()

    assert captured == {"pod_id": "senior-review", "output": output}
    assert str(output) in capsys.readouterr().out


def test_augment_command_uses_stack_when_shared_pod_is_docked(monkeypatch):
    captured = {}

    def fake_augment(prompt, stack):
        captured["prompt"] = prompt
        captured["stack"] = stack
        return AugmentResult(
            raw_prompt=prompt,
            profile=stack.base_pod,
            memories=[],
            furnished_prompt=prompt,
            active_pods=stack.active_pods,
        )

    monkeypatch.setattr(cli, "augment_for_stack", fake_augment)
    monkeypatch.setattr(
        "sys.argv",
        [
            "memory-pod",
            "augment",
            "Review this API",
            "--base-pod",
            "jiahan",
            "--shared-pod",
            "senior-review",
        ],
    )

    cli.main()

    assert captured["prompt"] == "Review this API"
    assert captured["stack"].active_pods == ("jiahan", "senior-review")
