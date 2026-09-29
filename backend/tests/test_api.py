from urllib.error import HTTPError

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers.base import HuggingFaceProvider, LocalProvider

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_empty_text_validation():
    response = client.post('/api/analyze', json={'text': '   '})
    assert response.status_code == 422


def test_analysis_has_expected_schema():
    text = (
        'CJ announces he will marry Princess. Teddie, Bobbie, Alex, and Gabbie react '
        'with anger and sadness. Their mother demands respect and family unity. Bobbie '
        'feels resentment toward her mother after years of pressure. The sisters argue over '
        'responsibility and forgiveness.'
    )
    response = client.post('/api/analyze', json={'text': text})
    assert response.status_code == 200
    payload = response.json()
    assert payload['success'] is True
    data = payload['data']
    assert 'summary' in data
    assert 'themes' in data
    assert 'characters' in data
    assert 'relationships' in data
    assert 'conflicts' in data
    assert 'emotions' in data
    assert 'important_scenes' in data
    assert 'relational_dialectics' in data
    assert 'insights' in data


def test_huggingface_provider_reports_bad_api_key(monkeypatch):
    def fake_urlopen(_request, timeout=90):
        raise HTTPError('https://router.huggingface.co/v1/chat/completions', 400, 'Bad Request', hdrs=None, fp=None)

    monkeypatch.setattr('app.providers.base.urlopen', fake_urlopen)

    with pytest.raises(ValueError, match='Hugging Face request failed|Bad Request'):
        HuggingFaceProvider('invalid-key').analyze_text('A short story.')


def test_local_provider_uses_csv_metadata():
    text = (
        'Movie title: Toy Story\n'
        'Genres: Adventure|Animation|Children|Comedy\n'
        'Average rating: 4.15 from 1500 ratings\n'
        'Community tags: family, animation, fun\n'
    )

    result = LocalProvider().analyze_text(text)

    assert 'Toy Story' in result['summary']
    assert 'Adventure' in result['summary']
    assert any(theme['name'] == 'Family' for theme in result['themes'])
    assert result['characters'][0]['name'] == 'Toy Story'
