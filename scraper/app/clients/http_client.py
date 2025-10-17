"""
Async HTTP client for fetching web pages.

This module provides an asynchronous HTTP client using aiohttp with
built-in retry logic, timeout handling, and connection pooling for
efficient concurrent requests.
"""

import asyncio
import logging
from typing import Optional
import ssl

import aiohttp
from aiohttp import ClientTimeout, ClientError
import certifi


logger = logging.getLogger(__name__)


# Default configuration
DEFAULT_TIMEOUT = 5.0  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds (base delay for exponential backoff)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


async def fetch_html(
    url: str,
    session: Optional[aiohttp.ClientSession] = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    headers: Optional[dict] = None,
) -> Optional[str]:
    """
    Fetch HTML content from a URL with retry logic and error handling.

    This function attempts to fetch HTML content from the specified URL
    using aiohttp. It includes automatic retry logic with exponential
    backoff for handling transient network errors and timeouts.

    Args:
        url: The URL to fetch
        session: Optional aiohttp ClientSession. If None, a new session
                 will be created for this request.
        timeout: Request timeout in seconds (default: 5.0)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Base delay in seconds for exponential backoff (default: 1.0)
        headers: Optional custom headers. If None, default User-Agent is used.

    Returns:
        HTML content as a string if successful, None if all retries failed.

    Raises:
        None - All exceptions are caught and logged, returning None on failure.

    Example:
        >>> html = await fetch_html("https://example.com")
        >>> if html:
        ...     print(f"Fetched {len(html)} bytes")
        ... else:
        ...     print("Failed to fetch page")
    """
    # Set default headers with User-Agent if not provided
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
    elif "User-Agent" not in headers:
        headers["User-Agent"] = DEFAULT_USER_AGENT

    # Create a new session if none provided
    should_close_session = False
    if session is None:
        session = await get_session()
        should_close_session = True

    # Configure timeout
    timeout_config = ClientTimeout(total=timeout)

    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            logger.debug(
                f"Fetching URL (attempt {attempt + 1}/{max_retries}): {url}"
            )

            async with session.get(
                url, timeout=timeout_config, headers=headers
            ) as response:
                # Check for successful status code
                if response.status == 200:
                    html = await response.text()
                    logger.debug(
                        f"Successfully fetched {len(html)} bytes from {url}"
                    )
                    if should_close_session:
                        await session.close()
                    return html
                else:
                    logger.warning(
                        f"HTTP {response.status} error for {url} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

        except asyncio.TimeoutError:
            logger.warning(
                f"Timeout fetching {url} (attempt {attempt + 1}/{max_retries})"
            )
        except ClientError as e:
            logger.warning(
                f"Client error fetching {url}: {e} "
                f"(attempt {attempt + 1}/{max_retries})"
            )
        except Exception as e:
            logger.error(
                f"Unexpected error fetching {url}: {e} "
                f"(attempt {attempt + 1}/{max_retries})"
            )

        # Wait before retrying (exponential backoff)
        if attempt < max_retries - 1:
            delay = retry_delay * (2**attempt)  # Exponential backoff
            logger.debug(f"Waiting {delay:.1f}s before retry...")
            await asyncio.sleep(delay)

    # All retries exhausted
    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
    if should_close_session:
        await session.close()
    return None


async def get_session(
    connector_limit: int = 100,
    connector_limit_per_host: int = 10,
    ssl_verify: bool = True,
) -> aiohttp.ClientSession:
    """
    Create and return a configured aiohttp ClientSession.

    This function creates a new ClientSession with optimized connection
    pooling settings. The session should be reused across multiple requests
    for better performance and then properly closed when done.

    Args:
        connector_limit: Maximum total number of simultaneous connections
                        (default: 100)
        connector_limit_per_host: Maximum number of simultaneous connections
                                  to a single host (default: 10)
        ssl_verify: Whether to verify SSL certificates (default: True)

    Returns:
        Configured aiohttp ClientSession with connection pooling.

    Example:
        >>> async with await get_session() as session:
        ...     html1 = await fetch_html("https://example.com/page1", session)
        ...     html2 = await fetch_html("https://example.com/page2", session)

    Note:
        The caller is responsible for closing the session when done:
        >>> session = await get_session()
        >>> # ... use session ...
        >>> await session.close()
    """
    # Configure SSL context
    ssl_context = None
    if ssl_verify:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    else:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(
        limit=connector_limit,
        limit_per_host=connector_limit_per_host,
        ttl_dns_cache=300,  # Cache DNS lookups for 5 minutes
        ssl=ssl_context,
    )

    session = aiohttp.ClientSession(
        connector=connector,
        headers={"User-Agent": DEFAULT_USER_AGENT},
    )

    logger.debug(
        f"Created new ClientSession with connection limits: "
        f"total={connector_limit}, per_host={connector_limit_per_host}, "
        f"ssl_verify={ssl_verify}"
    )

    return session


async def fetch_multiple(
    urls: list[str],
    session: Optional[aiohttp.ClientSession] = None,
    max_concurrent: int = 5,
    **fetch_kwargs,
) -> list[Optional[str]]:
    """
    Fetch multiple URLs concurrently with a concurrency limit.

    This function fetches multiple URLs in parallel while respecting a
    maximum concurrency limit to avoid overwhelming the server or network.

    Args:
        urls: List of URLs to fetch
        session: Optional shared aiohttp ClientSession
        max_concurrent: Maximum number of concurrent requests (default: 5)
        **fetch_kwargs: Additional keyword arguments passed to fetch_html

    Returns:
        List of HTML strings (or None for failed fetches) in the same order
        as the input URLs.

    Example:
        >>> urls = ["https://example.com/1", "https://example.com/2"]
        >>> results = await fetch_multiple(urls, max_concurrent=2)
        >>> successful = [html for html in results if html is not None]
        >>> print(f"Successfully fetched {len(successful)}/{len(urls)} pages")
    """
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(url: str) -> Optional[str]:
        async with semaphore:
            return await fetch_html(url, session=session, **fetch_kwargs)

    # Create tasks for all URLs
    tasks = [fetch_with_semaphore(url) for url in urls]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=False)

    logger.info(
        f"Fetched {len(urls)} URLs: "
        f"{sum(1 for r in results if r is not None)} successful, "
        f"{sum(1 for r in results if r is None)} failed"
    )

    return results
