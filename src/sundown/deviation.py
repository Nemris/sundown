"""Facilities to manage deviation metadata."""

from __future__ import annotations

import dataclasses
from enum import StrEnum
import re


URL_PATTERN = re.compile(
    r"www\.deviantart\.com/([A-Za-z0-9\-]+)/([a-z\-]+)/(?:.+-)?(\d+)"
)


class Kind(StrEnum):
    """Kinds of supported deviations."""

    ART = "1"
    JOURNAL = "1"  # DeviantArt treats journals as art.


@dataclasses.dataclass
class Deviation:
    """
    A deviation.

    Args:
        artist: Deviation artist.
        kind: Deviation kind.
        id: Deviation ID.
    """

    artist: str
    kind: Kind
    id: str

    @classmethod
    def from_url(cls, url: str) -> Deviation:
        """
        Build a Deviation from a deviation URL.

        Args:
            url: The string representation of a deviation URL.

        Returns:
            A Deviation built from the provided URL.

        Raises:
            ValueError: If url is not a valid deviation URL.
            NotImplementedError: If the deviation kind in the URL is
                not implemented.
        """
        try:
            artist, kind, id_ = URL_PATTERN.search(url).groups()
        except AttributeError as exc:
            raise ValueError(f"{url!r}: invalid deviation URL") from exc

        try:
            return cls(artist, Kind[kind.upper()], id_)
        except KeyError as exc:
            raise NotImplementedError(f"{kind!r}: kind not implemented") from exc

    @property
    def url(self) -> str:
        """This deviation's URL."""
        return "/".join(
            [
                "https://www.deviantart.com",
                self.artist.lower(),
                self.kind.name.lower(),
                self.id,
            ]
        )


@dataclasses.dataclass
class PartialDeviation:
    """
    A deviation with only the ID and kind, and no artist.

    Args:
        kind: Deviation kind.
        id: Deviation ID.
    """

    kind: Kind
    id: str

    def promote(self, artist: str) -> Deviation:
        """
        Promote this PartialDeviation to a Deviation.

        Args:
            artist: The creator of the deviation.

        Returns:
            A complete Deviation instantiated from this
            PartialDeviation's metadata.
        """
        return Deviation(artist, self.kind, self.id)
