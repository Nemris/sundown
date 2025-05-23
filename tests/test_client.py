# pylint: disable=missing-module-docstring

from hypothesis import given
import pytest

from sundown import client
from sundown.client import Client
from tests import strategies as myst


# pylint: disable=missing-function-docstring
@given(myst.input_tags_with_token())
async def test_client_authenticates_after_first_query(tag):
    # We'll mimic the Client#get() interface even if we don't use kwargs.
    # pylint: disable=unused-argument
    async def mock_get(*args, **kwargs):
        return tag if args[1] == client.TOKEN_PAGE else "{}"

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(Client, "get", mock_get)

        async with Client() as c:
            assert not c.authenticated
            _ = await c.query("", {})
            assert c.authenticated


# pylint: disable=missing-function-docstring
@given(myst.input_tags_with_token())
def test_token_extraction_succeeds_if_token_exists(tag):
    assert client.extract_token(tag) in tag


# pylint: disable=missing-function-docstring
@given(myst.input_tags())
def test_token_extraction_fails_if_token_missing(tag):
    with pytest.raises(ValueError):
        client.extract_token(tag)
