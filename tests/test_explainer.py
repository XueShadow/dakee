from types import SimpleNamespace

import pytest

import explainer


def test_explanation_uses_hugging_face_auto_provider(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured['client'] = kwargs

        def chat_completion(self, **kwargs):
            captured['request'] = kwargs
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='## Purpose\nIt sorts the input.'))]
            )

    monkeypatch.setattr(explainer, 'InferenceClient', FakeClient)

    result = explainer.explain_algorithm('merge sort', 'test-token', 'test/model')

    assert result == '## Purpose\nIt sorts the input.'
    assert captured['client']['provider'] == 'auto'
    assert captured['client']['api_key'] == 'test-token'
    assert captured['request']['model'] == 'test/model'


def test_missing_token_does_not_use_a_local_fallback():
    with pytest.raises(ValueError, match='HUGGINGFACE_API_KEY'):
        explainer.explain_algorithm('binary search', '')


def test_empty_algorithm_is_rejected():
    with pytest.raises(ValueError, match='Enter an algorithm'):
        explainer.explain_algorithm('   ', 'test-token')


def test_provider_errors_are_reported(monkeypatch):
    class FailingClient:
        def __init__(self, **kwargs):
            pass

        def chat_completion(self, **kwargs):
            raise RuntimeError('provider unavailable')

    monkeypatch.setattr(explainer, 'InferenceClient', FailingClient)

    with pytest.raises(ValueError, match='provider unavailable'):
        explainer.explain_algorithm('binary search', 'test-token')
