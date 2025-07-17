# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from hypothesis import given
import pytest

from sundown.comment import Body, ContentKind, URL
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
