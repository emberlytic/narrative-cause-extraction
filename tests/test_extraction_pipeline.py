import json

import pytest

import extraction_pipeline as ep


def test_parse_result_parses_valid_json_text():
    text = json.dumps(
        {
            "confirmed_cause": "Electrical fault",
            "probable_cause": "",
            "confidence": "confirmed",
            "reasoning": "The report explicitly names the cause.",
        }
    )
    result = ep._parse_result(text)
    assert result["confirmed_cause"] == "Electrical fault"
    assert result["confidence"] == "confirmed"


def test_parse_result_raises_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        ep._parse_result("not valid json")


def test_build_prompt_does_not_condense_short_report(monkeypatch):
    def fail_if_called(report_text):
        raise AssertionError("_condense_report should not be called for a short report")

    monkeypatch.setattr(ep, "_condense_report", fail_if_called)

    short_report = "Conclusion: burst pipe caused the flooding." * 10  # well under threshold
    assert len(short_report) <= ep.CONDENSE_THRESHOLD_CHARS

    prompt = ep._build_prompt(short_report)
    assert short_report in prompt


def test_build_prompt_condenses_report_over_threshold(monkeypatch):
    long_report = "x" * (ep.CONDENSE_THRESHOLD_CHARS + 1)

    def fake_condense(report_text):
        assert report_text == long_report
        return "CONDENSED: burst pipe caused the flooding."

    monkeypatch.setattr(ep, "_condense_report", fake_condense)

    prompt = ep._build_prompt(long_report)
    assert "CONDENSED: burst pipe caused the flooding." in prompt
    assert long_report not in prompt


def test_condense_report_sends_condense_prompt_to_llm(monkeypatch):
    captured = {}

    def fake_call_llm_text(prompt):
        captured["prompt"] = prompt
        return "condensed text"

    monkeypatch.setattr(ep, "_call_llm_text", fake_call_llm_text)

    result = ep._condense_report("full report text")

    assert result == "condensed text"
    assert "full report text" in captured["prompt"]
    assert "Condense" in captured["prompt"]


def test_call_llm_text_uses_openai_by_default(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setattr(ep, "_call_openai_text", lambda prompt: "openai response")
    monkeypatch.setattr(
        ep, "_call_anthropic_text", lambda prompt: (_ for _ in ()).throw(AssertionError("should not be called"))
    )

    assert ep._call_llm_text("hello") == "openai response"


def test_call_llm_text_uses_anthropic_when_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(ep, "_call_anthropic_text", lambda prompt: "anthropic response")
    monkeypatch.setattr(
        ep, "_call_openai_text", lambda prompt: (_ for _ in ()).throw(AssertionError("should not be called"))
    )

    assert ep._call_llm_text("hello") == "anthropic response"
