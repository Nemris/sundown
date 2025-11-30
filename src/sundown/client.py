"""Facilities to interface with DeviantArt."""

from __future__ import annotations

from collections.abc import Coroutine
from enum import StrEnum
import functools
import json
from types import TracebackType

import aiohttp
import bs4


# Using this page to save data, as the homepage is too heavy.
TOKEN_PAGE = "https://www.deviantart.com/users/login"


class Error(Exception):
    """A generic error occurred while fetching data."""


class ServerResponseError(Error):
    """There was an error in the server's response."""


class ServerConnectionError(Error):
    """An error occurred while connecting to the server."""


class BadJSONError(Error):
    """The Eclipse API returned invalid JSON data."""


class APIEndpoint(StrEnum):
    """Eclipse endpoints supported by Sundown."""

    COMMENTS = "https://www.deviantart.com/_napi/shared_api/comments/thread"


def authenticate(coro: Coroutine) -> Coroutine:
    """
    Decorator to authenticate Clients with DeviantArt.

    To use, decorate the Client methods that expect the Client to be
    authenticated, such as Eclipse API calls.
    The wrapper expects the first positional argument to be an instance
    of Client.

    Args:
        coro: Client method to decorate.

    Returns:
        The decorated coro, which will perform authentication when
            necessary.
    """

    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        client = args[0]
        if not client.authenticated:
            html = await client.get(TOKEN_PAGE)
            try:
                client.token = extract_token(html)
            except ValueError as exc:
                raise Error(f"{TOKEN_PAGE!r}: token not found") from exc
        return await coro(*args, **kwargs)

    return wrapper


class Client:
    """
    A client that interfaces with DeviantArt.

    This client implements the async context manager protocol.

    Attributes:
        session: An async session used to connect to DeviantArt.
        token: A CSRF token used to perform calls to the Eclipse API.
    """

    def __init__(self) -> None:
        """Initialize an instance of Client."""
        self.session = aiohttp.ClientSession(headers={"Accept-Encoding": "gzip"})
        self.token = ""

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def get(self, url: str, **kwargs) -> str:
        """
        Retrieve the data at url with a GET request.

        Args:
            url: The URL to request.
            **kwargs: Optional keyword arguments to pass to
                aiohttp.ClientSession.get().

        Returns:
            The decoded server response payload.

        Raises:
            ServerResponseError: If there's an error in the server
                response.
            ServerConnectionError: If an error occurs while connecting
                to the server.
        """
        try:
            async with self.session.get(url, **kwargs) as resp:
                resp.raise_for_status()
                return await resp.text()
        except aiohttp.ClientResponseError as exc:
            raise ServerResponseError(
                f"{exc.request_info.url}: {exc.status} {exc.message}"
            ) from exc
        except aiohttp.ServerConnectionError as exc:
            raise ServerConnectionError(exc) from exc

    async def close(self) -> None:
        """Close this client's underlying session."""
        await self.session.close()

    @authenticate
    async def query(self, endpoint: APIEndpoint, params: dict) -> dict:
        """
        Query an Eclipse API endpoint.

        Args:
            url: The API endpoint to query.
            params: Parameters to pass to the API.

        Returns:
            The API's JSON response.

        Raises:
            Error: If an attempt to authenticate failed.
            ServerResponseError: If there was an error in the server's
                response.
            ServerConnectionError: If an error occurred while connecting
                to the server.
            BadJSONError: If the server returned malformed JSON data.
        """
        # Let's assume this is needed by all present and future endpoints.
        params["csrf_token"] = self.token
        try:
            return json.loads(await self.get(endpoint, params=params))
        except json.decoder.JSONDecodeError as exc:
            raise BadJSONError("malformed JSON response") from exc

    @property
    def authenticated(self) -> bool:
        """Whether this client is authenticated to DeviantArt."""
        return self.token != ""


def extract_token(html: str) -> str:
    """
    Extract a CSRF token from HTML data.

    Args:
        html: The HTML data to parse.

    Returns:
        The CSRF token.

    Raises:
        ValueError: If the HTML data doesn't contain a CSRF token.
    """
    soup = bs4.BeautifulSoup(html, features="html.parser")

    try:
        return soup.find("input", attrs={"name": "csrf_token"})["value"]
    except Exception as exc:
        raise ValueError("CSRF token not found in html") from exc
