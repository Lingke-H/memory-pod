from memory_pod.radar import resonance_report


def test_resonance_report_points_to_current_pod_workflows():
    report = resonance_report()

    assert "current MVP scope" in report
    assert "Base Pod and Shared Pod workflows" in report
    assert "Tier 0" not in report
