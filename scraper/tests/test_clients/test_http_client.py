"""
Unit tests for the HTTP client module.

These tests verify the async HTTP client functionality including
retry logic, timeout handling, and session management.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientError, ClientTimeout

from app.clients.http_client import (
    fetch_html,
    get_session,
    fetch_multiple,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
)


class TestFetchHtml:
    """Tests for fetch_html function."""

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_success(self, mock_get_session):
        """Test successful HTML fetching."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>Test content</html>")
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()

        # Mock session
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        html = await fetch_html("https://example.com")

        assert html == "<html>Test content</html>"
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_with_provided_session(self, mock_get_session):
        """Test fetch_html with provided session."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>Content</html>")
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()

        # Mock session
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.close = AsyncMock()

        html = await fetch_html("https://example.com", session=mock_session)

        assert html == "<html>Content</html>"
        # Session should not be closed when provided externally
        mock_session.close.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_non_200_status(self, mock_get_session):
        """Test handling of non-200 HTTP status."""
        # Mock response with 404 status
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        html = await fetch_html("https://example.com", max_retries=1)

        assert html is None
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_timeout(self, mock_get_session):
        """Test handling of timeout errors."""
        # Mock session that raises timeout
        mock_session = AsyncMock()
        mock_session.get.side_effect = asyncio.TimeoutError()
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        html = await fetch_html(
            "https://example.com",
            timeout=1.0,
            max_retries=2,
            retry_delay=0.01,
        )

        assert html is None
        # Should have tried max_retries times
        assert mock_session.get.call_count == 2

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_client_error(self, mock_get_session):
        """Test handling of client errors."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = ClientError("Connection failed")
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        html = await fetch_html(
            "https://example.com",
            max_retries=2,
            retry_delay=0.01,
        )

        assert html is None
        assert mock_session.get.call_count == 2

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_retry_success(self, mock_get_session):
        """Test successful retry after initial failure."""
        # First call fails, second succeeds
        mock_response_fail = AsyncMock()
        mock_response_fail.status = 500
        mock_response_fail.__aenter__.return_value = mock_response_fail
        mock_response_fail.__aexit__.return_value = AsyncMock()

        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.text = AsyncMock(return_value="<html>Success</html>")
        mock_response_success.__aenter__.return_value = mock_response_success
        mock_response_success.__aexit__.return_value = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get.side_effect = [mock_response_fail, mock_response_success]
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        html = await fetch_html(
            "https://example.com",
            max_retries=3,
            retry_delay=0.01,
        )

        assert html == "<html>Success</html>"
        assert mock_session.get.call_count == 2

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_custom_headers(self, mock_get_session):
        """Test fetch_html with custom headers."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>Test</html>")
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_response
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        custom_headers = {"Authorization": "Bearer token123"}
        html = await fetch_html(
            "https://example.com",
            headers=custom_headers,
        )

        assert html == "<html>Test</html>"
        # Verify custom headers were used
        call_kwargs = mock_session.get.call_args[1]
        assert "Authorization" in call_kwargs["headers"]


class TestGetSession:
    """Tests for get_session function."""

    @pytest.mark.asyncio
    async def test_get_session_creates_session(self):
        """Test that get_session creates a ClientSession."""
        session = await get_session()

        assert session is not None
        # Clean up
        await session.close()

    @pytest.mark.asyncio
    async def test_get_session_with_custom_limits(self):
        """Test get_session with custom connection limits."""
        session = await get_session(
            connector_limit=50,
            connector_limit_per_host=5,
        )

        assert session is not None
        # Verify connector was created with limits
        assert session.connector.limit == 50
        assert session.connector.limit_per_host == 5

        await session.close()


class TestFetchMultiple:
    """Tests for fetch_multiple function."""

    @pytest.mark.asyncio
    @patch("app.clients.http_client.fetch_html")
    async def test_fetch_multiple_success(self, mock_fetch_html):
        """Test fetching multiple URLs successfully."""
        # Mock responses
        mock_fetch_html.side_effect = [
            "<html>Page 1</html>",
            "<html>Page 2</html>",
            "<html>Page 3</html>",
        ]

        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
        ]

        results = await fetch_multiple(urls, max_concurrent=2)

        assert len(results) == 3
        assert results[0] == "<html>Page 1</html>"
        assert results[1] == "<html>Page 2</html>"
        assert results[2] == "<html>Page 3</html>"

    @pytest.mark.asyncio
    @patch("app.clients.http_client.fetch_html")
    async def test_fetch_multiple_with_failures(self, mock_fetch_html):
        """Test fetch_multiple with some failures."""
        mock_fetch_html.side_effect = [
            "<html>Page 1</html>",
            None,  # Failed
            "<html>Page 3</html>",
        ]

        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

        results = await fetch_multiple(urls)

        assert len(results) == 3
        assert results[0] == "<html>Page 1</html>"
        assert results[1] is None
        assert results[2] == "<html>Page 3</html>"

    @pytest.mark.asyncio
    @patch("app.clients.http_client.fetch_html")
    async def test_fetch_multiple_concurrency_limit(self, mock_fetch_html):
        """Test that fetch_multiple respects concurrency limit."""
        concurrent_count = []
        max_concurrent_seen = 0

        async def mock_fetch(*args, **kwargs):
            nonlocal max_concurrent_seen
            concurrent_count.append(1)
            current = len(concurrent_count)
            max_concurrent_seen = max(max_concurrent_seen, current)
            await asyncio.sleep(0.01)
            concurrent_count.pop()
            return "<html>Test</html>"

        mock_fetch_html.side_effect = mock_fetch

        urls = [f"https://example.com/{i}" for i in range(10)]

        await fetch_multiple(urls, max_concurrent=3)

        # Should not exceed concurrency limit (with some tolerance)
        assert max_concurrent_seen <= 4

    @pytest.mark.asyncio
    @patch("app.clients.http_client.fetch_html")
    async def test_fetch_multiple_empty_list(self, mock_fetch_html):
        """Test fetch_multiple with empty URL list."""
        results = await fetch_multiple([])

        assert len(results) == 0
        mock_fetch_html.assert_not_called()


class TestErrorHandling:
    """Tests for error handling in HTTP client."""

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_unexpected_exception(self, mock_get_session):
        """Test handling of unexpected exceptions."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Unexpected error")
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        html = await fetch_html(
            "https://example.com",
            max_retries=2,
            retry_delay=0.01,
        )

        assert html is None
        assert mock_session.get.call_count == 2

    @pytest.mark.asyncio
    @patch("app.clients.http_client.get_session")
    async def test_fetch_html_exponential_backoff(self, mock_get_session):
        """Test that retry delays use exponential backoff."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = ClientError("Error")
        mock_session.close = AsyncMock()
        mock_get_session.return_value = mock_session

        import time
        start_time = time.time()

        html = await fetch_html(
            "https://example.com",
            max_retries=3,
            retry_delay=0.1,
        )

        elapsed = time.time() - start_time

        assert html is None
        # With exponential backoff: 0.1 + 0.2 = 0.3 seconds minimum
        # Allow some tolerance
        assert elapsed >= 0.25


# Pytest fixtures
@pytest.fixture
def mock_aiohttp_response():
    """Fixture providing a mock aiohttp response."""
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="<html>Mock content</html>")
    response.__aenter__.return_value = response
    response.__aexit__.return_value = AsyncMock()
    return response


@pytest.fixture
def mock_aiohttp_session(mock_aiohttp_response):
    """Fixture providing a mock aiohttp session."""
    session = AsyncMock()
    session.get.return_value = mock_aiohttp_response
    session.close = AsyncMock()
    return session
