# pylint: disable=missing-module-docstring

from hypothesis import given
import pytest

from sundown.deviation import Deviation, Kind
from tests import strategies as myst


# pylint: disable=missing-function-docstring
@given(myst.usernames(), myst.ids())
def test_deviation_lowercases_artist_in_urls(user, dev_id):
    d = Deviation(user, Kind.ART, dev_id)

    assert user.lower() in d.url


# pylint: disable=missing-function-docstring
@given(myst.usernames(), myst.ids())
def test_deviation_url_contains_all_parameters(user, dev_id):
    d = Deviation(user, Kind.ART, dev_id)

    assert d.artist.lower() in d.url and d.kind.name.lower() in d.url and d.id in d.url


@given(myst.deviation_urls())
def test_deviation_is_built_from_valid_url(url):
    Deviation.from_url(url)


@given(myst.deviation_urls(valid=False))
def test_deviation_is_not_built_from_invalid_url(url):
    with pytest.raises(NotImplementedError):
        _ = Deviation.from_url(url)


def test_deviation_journal_aliased_to_art():
    d = Deviation("", Kind.JOURNAL, "")

    assert d.kind == Kind.ART
