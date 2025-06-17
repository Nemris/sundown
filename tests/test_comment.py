# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from hypothesis import given
import pytest

from sundown.comment import URL
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
