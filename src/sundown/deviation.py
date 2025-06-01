"""Facilities to manage deviation metadata."""

import dataclasses
from enum import StrEnum


class Kind(StrEnum):
    """Kinds of supported deviations."""

    ART = "1"
    JOURNAL = "1"  # DeviantArt treats journals as art.


@dataclasses.dataclass
class Deviation:
    """A deviation."""

    artist: str
    kind: Kind
    id: str

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
