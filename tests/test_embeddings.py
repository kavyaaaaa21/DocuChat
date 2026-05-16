"""
test_embeddings.py — Tests for services/embeddings.py
"""

import pytest
from unittest.mock import patch, MagicMock
from services.embeddings import generate_embeddings
from conftest import FAKE_EMBEDDING, EMBEDDING_DIM


def make_embedding_response(vectors):
    mock_items    = [MagicMock(embedding=v) for v in vectors]
    mock_response = MagicMock()
    mock_response.data = mock_items
    return mock_response


class TestGenerateEmbeddings:

    @patch("services.embeddings.client")
    def test_returns_list_of_vectors(self, mock_client):
        mock_client.embeddings.create.return_value = make_embedding_response([FAKE_EMBEDDING])
        result = generate_embeddings(["Hello world."])
        assert isinstance(result, list)
        assert isinstance(result[0], list)

    @patch("services.embeddings.client")
    def test_vector_dimension_matches(self, mock_client):
        mock_client.embeddings.create.return_value = make_embedding_response([FAKE_EMBEDDING])
        result = generate_embeddings(["text"])
        assert len(result[0]) == EMBEDDING_DIM

    @patch("services.embeddings.client")
    def test_output_count_matches_input_count(self, mock_client):
        embeddings = [FAKE_EMBEDDING[:] for _ in range(4)]
        mock_client.embeddings.create.return_value = make_embedding_response(embeddings)
        result = generate_embeddings(["a", "b", "c", "d"])
        assert len(result) == 4

    @patch("services.embeddings.client")
    def test_large_batch_is_split(self, mock_client):
        """Input > 100 texts should trigger multiple API calls."""
        single_embed = make_embedding_response([FAKE_EMBEDDING] * 100)
        mock_client.embeddings.create.return_value = single_embed

        texts = [f"text {i}" for i in range(250)]
        result = generate_embeddings(texts)

        assert mock_client.embeddings.create.call_count == 3   # 100+100+50
        assert len(result) == 250

    def test_raises_on_empty_input(self):
        with pytest.raises(ValueError, match="No texts provided"):
            generate_embeddings([])

    @patch("services.embeddings.client")
    def test_newlines_replaced_with_spaces(self, mock_client):
        """Texts should have newlines stripped before being sent to the API."""
        mock_client.embeddings.create.return_value = make_embedding_response([FAKE_EMBEDDING])
        generate_embeddings(["line one\nline two"])

        call_args = mock_client.embeddings.create.call_args
        sent_input = call_args.kwargs.get("input") or call_args.args[0]
        assert "\n" not in sent_input[0]

    @patch("services.embeddings.client")
    def test_uses_configured_embedding_model(self, mock_client):
        mock_client.embeddings.create.return_value = make_embedding_response([FAKE_EMBEDDING])

        with patch("services.embeddings.settings") as s:
            s.EMBEDDING_MODEL = "text-embedding-3-large"
            generate_embeddings(["text"])

        call_kwargs = mock_client.embeddings.create.call_args.kwargs
        assert call_kwargs["model"] == "text-embedding-3-large"
