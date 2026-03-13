"""Tests for librarian agent logic.

Mocks both Ollama and Assay API responses to test:
- Thread summarization prompt building
- Link discovery JSON parsing
- Quality vote scoring
- State persistence
"""

import json
from unittest.mock import MagicMock

import pytest

# We need to import from scripts/, which isn't a package.
# Add scripts/ to path for testing.
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


@pytest.fixture(autouse=True)
def _set_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ASSAY_BASE_URL", "http://test:8000/api/v1")
    monkeypatch.setenv("ASSAY_API_KEY", "sk_test_key")
    monkeypatch.setenv("OLLAMA_URL", "http://test:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3.5:9b")
    monkeypatch.setenv("LIBRARIAN_STATE", str(tmp_path / "state.json"))


def _mock_ollama_response(text: str):
    """Create a mock httpx response for Ollama generate."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"response": text}
    mock.raise_for_status = MagicMock()
    return mock


def _mock_assay_response(data: dict):
    """Create a mock httpx response for Assay API."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


class TestLinkDiscoveryParsing:
    """Test that find_related_threads correctly parses Ollama JSON output."""

    def test_parses_valid_json_lines(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response(
            '{"id": "abc-123", "link_type": "extends", "reason": "both about X"}\n'
            '{"id": "def-456", "link_type": "contradicts", "reason": "opposite claims"}'
        )

        results = librarian.find_related_threads(
            client,
            "new-id",
            "New thread",
            "Summary of new thread",
            {
                "abc-123": {"title": "Old thread 1", "summary": "About X"},
                "def-456": {"title": "Old thread 2", "summary": "About Y"},
            },
        )

        assert len(results) == 2
        assert results[0]["id"] == "abc-123"
        assert results[0]["link_type"] == "extends"
        assert results[1]["id"] == "def-456"
        assert results[1]["link_type"] == "contradicts"

    def test_ignores_invalid_json(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response(
            "Here are the related threads:\n"
            '{"id": "abc-123", "link_type": "extends", "reason": "related"}\n'
            "This is not JSON\n"
            '{"id": "bad", "link_type": "invalid_type", "reason": "bad type"}'
        )

        results = librarian.find_related_threads(
            client, "new-id", "New", "Sum",
            {"abc-123": {"title": "Old", "summary": "Old sum"}},
        )

        assert len(results) == 1
        assert results[0]["id"] == "abc-123"

    def test_empty_existing_returns_empty(self):
        import librarian

        client = MagicMock()
        results = librarian.find_related_threads(
            client, "new-id", "New", "Sum", {}
        )
        assert results == []

    def test_excludes_self_from_existing(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response("")

        results = librarian.find_related_threads(
            client,
            "self-id",
            "Title",
            "Summary",
            {"self-id": {"title": "Same", "summary": "Same sum"}},
        )

        # Should not even call Ollama if only self exists
        assert results == []


class TestQualityScoring:
    """Test that should_upvote_answer correctly interprets Ollama rating."""

    def test_score_4_upvotes(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response("4")
        assert librarian.should_upvote_answer(client, "Q title", "Good answer") is True

    def test_score_5_upvotes(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response("5")
        assert librarian.should_upvote_answer(client, "Q title", "Great answer") is True

    def test_score_3_does_not_upvote(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response("3")
        assert librarian.should_upvote_answer(client, "Q title", "Meh answer") is False

    def test_score_1_does_not_upvote(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response("1")
        assert librarian.should_upvote_answer(client, "Q title", "Bad answer") is False

    def test_garbage_response_does_not_upvote(self):
        import librarian

        client = MagicMock()
        client.post.return_value = _mock_ollama_response("I think this is good")
        assert librarian.should_upvote_answer(client, "Q", "A") is False


class TestStatePersistence:
    """Test that state loads and saves correctly."""

    def test_load_missing_state_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LIBRARIAN_STATE", str(tmp_path / "missing.json"))
        # Re-import to pick up new env
        import importlib
        import librarian
        importlib.reload(librarian)
        librarian.STATE_PATH = tmp_path / "missing.json"

        state = librarian.load_state()
        assert state == {"summaries": {}, "linked_pairs": [], "voted_ids": []}

    def test_save_and_load_roundtrip(self, tmp_path):
        import librarian
        librarian.STATE_PATH = tmp_path / "test-state.json"

        state = {
            "summaries": {"q1": {"title": "T1", "summary": "S1"}},
            "linked_pairs": ["q1:q2:extends"],
            "voted_ids": ["a1"],
        }
        librarian.save_state(state)
        loaded = librarian.load_state()
        assert loaded == state
