"""Facilities to manage comments and comment pages."""

from __future__ import annotations

import dataclasses
import re

from sundown.deviation import Deviation, Kind


URL_PATTERN = re.compile(r"www\.deviantart\.com/comments/(\d+)/(\d+)/(\d+)")


@dataclasses.dataclass
class URL:
    """
    A URL to a comment.

    Args:
        deviation: Deviation being commented to.
        comment_id: ID of the comment.
    """

    deviation: Deviation
    comment_id: str

    def __str__(self) -> str:
        return "/".join(
            [
                "https://www.deviantart.com/comments",
                self.deviation.kind,
                self.deviation.id,
                self.comment_id,
            ]
        )

    @classmethod
    def from_str(cls, url: str) -> URL:
        """
        Build a URL from a string representation of a comment URL.

        The deviation field in the resulting URL instance will have an
        empty artist field.

        Args:
            url: Comment URL.

        Returns:
            An instance of URL pointing to the comment referenced by
                url.

        Raises:
            ValueError: If url isn't a valid comment URL.
            NotImplementedError: If the deviation kind in the url is
                not implemented.
        """
        try:
            dev_kind, dev_id, comment_id = URL_PATTERN.search(url).groups()
        except AttributeError as exc:
            raise ValueError(f"{url!r}: invalid comment URL") from exc

        try:
            dev = Deviation("", Kind(dev_kind), dev_id)
        except ValueError as exc:
            raise NotImplementedError(f"{dev_kind!r}: kind not implemented") from exc

        return cls(dev, comment_id)
