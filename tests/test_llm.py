from types import SimpleNamespace

import pytest
from google.genai import errors

from validator import llm as llm_mod
from validator.models import Verdict

OK = Verdict(ready_for_development=True, ready_for_testing=True, summary="s", top_fixes=[]).model_dump_json()


class FakeModels:
    """Stands in for client.models: `overloaded` models always answer 503."""

    def __init__(self, overloaded, retired=()):
        self.overloaded, self.retired, self.calls = set(overloaded), set(retired), []

    def generate_content(self, model, contents, config):
        self.calls.append(model)
        if model in self.retired:
            raise errors.ClientError(404, {"error": {"code": 404, "message": "no longer available", "status": "NOT_FOUND"}})
        if model in self.overloaded:
            raise errors.ServerError(503, {"error": {"code": 503, "message": "high demand", "status": "UNAVAILABLE"}})
        return SimpleNamespace(text=OK)


def _gemini(tmp_path, overloaded, monkeypatch, retired=()):
    monkeypatch.setattr(llm_mod.time, "sleep", lambda s: None)
    g = llm_mod.Gemini("main", "key", cache_dir=tmp_path, fallbacks=["spare"])
    g._client = SimpleNamespace(models=FakeModels(overloaded, retired))
    return g


def test_switches_to_fallback_when_primary_is_overloaded(tmp_path, monkeypatch):
    g = _gemini(tmp_path, {"main"}, monkeypatch)
    assert g.ask("p", Verdict).summary == "s"
    assert g._client.models.calls[-1] == "spare"
    assert g.model == "spare"  # passport names the model that actually answered


def test_reports_only_primary_when_it_answers(tmp_path, monkeypatch):
    g = _gemini(tmp_path, set(), monkeypatch)
    g.ask("p", Verdict)
    assert g.model == "main"


def test_gives_up_with_clear_error_when_all_models_overloaded(tmp_path, monkeypatch):
    g = _gemini(tmp_path, {"main", "spare"}, monkeypatch)
    with pytest.raises(SystemExit, match="main, spare"):
        g.ask("p", Verdict)


def test_overloaded_model_is_not_retried_first_on_next_calls(tmp_path, monkeypatch):
    g = _gemini(tmp_path, {"main"}, monkeypatch)
    g.ask("p1", Verdict)
    calls_before = len(g._client.models.calls)
    g.ask("p2", Verdict)
    assert g._client.models.calls[calls_before:] == ["spare"]


def test_retired_model_is_skipped_without_retries(tmp_path, monkeypatch):
    g = _gemini(tmp_path, set(), monkeypatch, retired={"main"})
    g.ask("p", Verdict)
    assert g._client.models.calls == ["main", "spare"]


def test_fresh_primary_answer_beats_cached_fallback_answer(tmp_path, monkeypatch):
    g = _gemini(tmp_path, {"main"}, monkeypatch)
    g.ask("p", Verdict)  # main overloaded -> answered and cached by spare
    g2 = _gemini(tmp_path, set(), monkeypatch)  # main is back
    g2.ask("p", Verdict)
    assert g2._client.models.calls == ["main"] and g2.model == "main"


def test_bad_request_from_one_model_moves_on_but_bad_key_stops(tmp_path, monkeypatch):
    g = _gemini(tmp_path, set(), monkeypatch)
    real = g._client.models.generate_content

    def first_model_rejects_request(model, contents, config):
        if model == "main":
            raise errors.ClientError(400, {"error": {"code": 400, "message": "schema", "status": "INVALID_ARGUMENT"}})
        return real(model=model, contents=contents, config=config)
    g._client.models.generate_content = first_model_rejects_request
    assert g.ask("p", Verdict).summary == "s" and g.model == "spare"

    def bad_key(**kw):
        raise errors.ClientError(403, {"error": {"code": 403, "message": "key", "status": "PERMISSION_DENIED"}})
    g._client.models.generate_content = bad_key
    with pytest.raises(errors.ClientError):
        g.ask("p2", Verdict)


def test_daily_quota_exhaustion_moves_on_without_waiting(tmp_path, monkeypatch):
    g = _gemini(tmp_path, set(), monkeypatch)
    real = g._client.models.generate_content
    main_attempts = []

    def daily_quota_on_main(model, contents, config):
        if model == "main":
            main_attempts.append(model)
            raise errors.ClientError(429, {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED",
                "details": [{"violations": [{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"}]}]}})
        return real(model=model, contents=contents, config=config)
    g._client.models.generate_content = daily_quota_on_main
    g.ask("p", Verdict)
    assert main_attempts == ["main"]  # no retries: a daily quota won't recover within the run
    assert g.model == "spare"
