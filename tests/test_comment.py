# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from datetime import datetime

from hypothesis import given
import pytest

from sundown.comment import (
    Body,
    Comment,
    CommentJSONError,
    ContentKind,
    Metadata,
    Page,
    PageJSONError,
    URL,
)
from sundown import deviation
from tests import strategies as myst


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


@given(myst.comment_pages())
def test_page_is_built_from_valid_json(json):
    Page.from_json(json)


@given(myst.comment_pages(valid=False))
def test_page_is_not_built_from_invalid_json(json):
    # We only care that the error is the same in all occasions.
    with pytest.raises(PageJSONError):
        Page.from_json(json)


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
