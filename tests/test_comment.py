# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st
import pytest

from sundown.comment import (
    Body,
    Comment,
    CommentJSONError,
    ContentKind,
    Metadata,
    Page,
    PageIterator,
    PageJSONError,
    URL,
)
from sundown.client import Client
from sundown import deviation
from tests import strategies as myst


def _get_dummy_page_json() -> dict:
    """Returns a minimal comment page JSON."""
    return {
        "hasMore": False,
        "hasLess": False,
        "nextOffset": None,
        "prevOffset": None,
        "thread": [],
    }


@given(myst.comment_urls())
def test_comment_url_is_built_from_valid_url(url):
    URL.from_str(url)


@given(myst.comment_urls(valid=False))
def test_comment_url_is_not_built_from_invalid_url(url):
    with pytest.raises(NotImplementedError):
        _ = URL.from_str(url)


@given(myst.deviation_urls())
def test_comment_url_is_not_built_from_non_comment_url(url):
    with pytest.raises(ValueError):
        _ = URL.from_str(url)


@given(myst.comments())
def test_comment_is_built_from_valid_json(json):
    Comment.from_json(json)


@given(myst.comments(valid=False))
def test_comment_is_not_built_from_invalid_json(json):
    # We only care that the error is the same in all occasions.
    with pytest.raises(CommentJSONError):
        Comment.from_json(json)


async def test_page_iterator_updates_param_offset():
    # We'll mimic the Client#query() interface even if we don't use arguments.
    # pylint: disable=unused-argument
    async def mock_query(*args, **kwargs):
        params = args[-1]

        json = _get_dummy_page_json()
        json["hasMore"] = True
        json["nextOffset"] = params["offset"] + params["limit"]
        return json

    # The actual deviation data is irrelevant.
    d = deviation.PartialDeviation(deviation.Kind.ART, "0")

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(Client, "query", mock_query)

        async with Client() as c:
            pi = PageIterator(c, d, 0, 50)
            p = await anext(pi)

            assert pi.params["offset"] == p.next_offset


async def test_page_iterator_stops_when_no_more_pages_exist():
    # We'll mimic the Client#query() interface even if we don't use arguments.
    # pylint: disable=unused-argument
    async def mock_query(*args, **kwargs):
        return _get_dummy_page_json()

    # The actual deviation data is irrelevant.
    d = deviation.PartialDeviation(deviation.Kind.ART, "0")

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(Client, "query", mock_query)

        async with Client() as c:
            pi = PageIterator(c, d, 0, 50)
            await anext(pi)

            with pytest.raises(StopAsyncIteration):
                await anext(pi)


@given(myst.comment_pages())
def test_page_is_built_from_valid_json(json):
    Page.from_json(json)


@given(myst.comment_pages(valid=False))
def test_page_is_not_built_from_invalid_json(json):
    # We only care that the error is the same in all occasions.
    with pytest.raises(PageJSONError):
        Page.from_json(json)


@given(st.data(), st.integers(min_value=1, max_value=10))
def test_page_returns_correct_length(data, entries):
    # Randomizing but capping the amount of comments in a page.
    json = data.draw(myst.comment_pages(entries))

    assert len(Page.from_json(json)) == entries


@given(st.data(), st.integers(min_value=1, max_value=10))
def test_page_iterates_through_comments(data, entries):
    # Randomizing but capping the amount of comments in a page.
    json = data.draw(myst.comment_pages(entries))

    assert sum(True for c in Page.from_json(json)) == entries


@given(myst.comment_markups(3))
def test_comment_body_finds_all_text(markup):
    body = Body(markup, {})

    con = markup["document"]["content"]
    for line, par in zip(body.text.split("\n"), con):
        assert line == par["content"][0][str(ContentKind.TEXT)]


@given(myst.comment_markups(3, True))
def test_comment_body_considers_mentions_as_text(markup):
    body = Body(markup, {})

    for m in body.mentions:
        assert m in body.text


@given(myst.comment_markups(3, True))
def test_comment_body_finds_all_existing_mentions(markup):
    body = Body(markup, {})
    mentions = sum(
        True
        for par in markup["document"]["content"]
        if par["content"][0]["type"] == ContentKind.MENTION
    )

    assert len(list(body.mentions)) == mentions


@given(myst.comment_markups(3))
def test_comment_body_finds_all_paragraphs(markup):
    body = Body(markup, {})

    assert len(list(body.get_paragraphs())) == len(markup["document"]["content"])


@given(myst.comment_features())
def test_comment_body_finds_wordcount_from_feature(feat):
    body = Body({}, feat)

    # NOTE: this will need adjusting if we'll emulate more features.
    assert body.words == feat[0]["data"]["words"]


@given(myst.ids(), myst.ids())
def test_comment_metadata_returns_good_url(dev_id, comment_id):
    p = deviation.PartialDeviation(deviation.Kind.ART, dev_id)
    m = Metadata(comment_id, p, None, "", datetime.now(), None, 0)

    assert m.url.deviation == p and m.url.comment_id == comment_id
