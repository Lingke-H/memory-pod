from memory_pod.rewriter import build_rewrite_prompt, polish_locally


RAW_PROMPT = "improve my resume"
FURNISHED_PROMPT = """[Hidden Context]
Relevant Facts
- I am a stats student with two web projects.

[User Query]
improve my resume
"""


def test_build_rewrite_prompt_contains_inputs_and_safety_constraints():
    prompt = build_rewrite_prompt(RAW_PROMPT, FURNISHED_PROMPT)

    assert RAW_PROMPT in prompt
    assert FURNISHED_PROMPT in prompt
    assert "do not invent facts" in prompt.lower()
    assert "preserve the user's intent" in prompt.lower()
    assert "one clean, copy-ready prompt" in prompt.lower()


def test_polish_locally_falls_back_when_ollama_unavailable(monkeypatch):
    monkeypatch.setattr("memory_pod.rewriter.ollama_available", lambda *_, **__: False)

    result = polish_locally(RAW_PROMPT, FURNISHED_PROMPT)

    assert result.text == FURNISHED_PROMPT.strip()
    assert result.used_local_ai is False
    assert "unavailable" in result.note.lower()


def test_polish_locally_uses_fake_ollama_success(monkeypatch):
    monkeypatch.setattr("memory_pod.rewriter.ollama_available", lambda *_, **__: True)
    monkeypatch.setattr(
        "memory_pod.rewriter._ollama_generate",
        lambda *_, **__: "You are an expert resume coach. Improve my resume.",
    )

    result = polish_locally(RAW_PROMPT, FURNISHED_PROMPT)

    assert result.text == "You are an expert resume coach. Improve my resume."
    assert result.used_local_ai is True
    assert "local" in result.note.lower()


def test_polish_locally_falls_back_on_empty_ollama_response(monkeypatch):
    monkeypatch.setattr("memory_pod.rewriter.ollama_available", lambda *_, **__: True)
    monkeypatch.setattr("memory_pod.rewriter._ollama_generate", lambda *_, **__: "   ")

    result = polish_locally(RAW_PROMPT, FURNISHED_PROMPT)

    assert result.text == FURNISHED_PROMPT.strip()
    assert result.used_local_ai is False
    assert "empty" in result.note.lower()
