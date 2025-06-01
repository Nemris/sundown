# pylint: disable=missing-module-docstring

from hypothesis import given

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


def test_deviation_journal_aliased_to_art():
    d = Deviation("", Kind.JOURNAL, "")

    assert d.kind == Kind.ART
