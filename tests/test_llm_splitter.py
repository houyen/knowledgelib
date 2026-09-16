import os
import sys
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm_splitter import split_text_with_llm


def test_no_api_key_returns_none_without_calling_api(monkeypatch):
    """When no API key is set, returns None immediately without instantiating or calling SDK."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    pages = [(1, "Some document page content")]
    with patch("google.genai.Client") as mock_client:
        result = split_text_with_llm(pages, "doc_test", api_key=None)
        assert result is None
        mock_client.assert_not_called()


def test_empty_pages_returns_none():
    """Empty pages list returns None without any calls."""
    result = split_text_with_llm([], "empty_doc", api_key="fake-key")
    assert result is None


def test_valid_response_parses_units():
    """Valid JSON from LLM is correctly converted to unit dicts with 2-digit numbers."""
    mock_json = """
    [
        {"title": "Introduction to Auth", "content": "Auth is critical for system security."},
        {"title": "Session Management", "content": "Sessions maintain user state across requests."}
    ]
    """

    mock_resp = MagicMock()
    mock_resp.text = mock_json

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_resp

    pages = [(1, "Full document text here")]
    with patch("google.genai.Client", return_value=mock_client_instance):
        result = split_text_with_llm(pages, "auth_guide", api_key="fake-test-key")

    assert result is not None
    assert len(result) == 2
    assert result[0]["num"] == "01"
    assert result[0]["title"] == "Introduction to Auth"
    assert "Auth is critical" in result[0]["content"]

    assert result[1]["num"] == "02"
    assert result[1]["title"] == "Session Management"
    assert "Sessions maintain" in result[1]["content"]


def test_markdown_fenced_json_response_parses_units():
    """LLM wrapping JSON in ```json ... ``` code fence is handled cleanly."""
    mock_json = """```json
    [
        {"title": "Overview", "content": "Overview content here."}
    ]
    ```"""

    mock_resp = MagicMock()
    mock_resp.text = mock_json

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_resp

    pages = [(1, "Doc text")]
    with patch("google.genai.Client", return_value=mock_client_instance):
        result = split_text_with_llm(pages, "doc", api_key="fake-test-key")

    assert result is not None
    assert len(result) == 1
    assert result[0]["title"] == "Overview"


def test_invalid_json_response_returns_none():
    """Non-JSON response returns None without crashing."""
    mock_resp = MagicMock()
    mock_resp.text = "I am sorry, I cannot split this document into JSON."

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_resp

    pages = [(1, "Some text")]
    with patch("google.genai.Client", return_value=mock_client_instance):
        result = split_text_with_llm(pages, "doc", api_key="fake-test-key")

    assert result is None


def test_api_exception_returns_none():
    """API or network exception returns None safely."""
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.side_effect = RuntimeError("Quota exceeded or network timeout")

    pages = [(1, "Some text")]
    with patch("google.genai.Client", return_value=mock_client_instance):
        result = split_text_with_llm(pages, "doc", api_key="fake-test-key")

    assert result is None
