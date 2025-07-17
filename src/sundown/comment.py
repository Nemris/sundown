"""Facilities to manage comments and comment pages."""

from __future__ import annotations

from collections.abc import Iterator
import dataclasses
from enum import StrEnum
import re

from sundown.deviation import Deviation, Kind


URL_PATTERN = re.compile(r"www\.deviantart\.com/comments/(\d+)/(\d+)/(\d+)")


class ContentKind(StrEnum):
    """Kinds of supported content entries."""

    PARAGRAPH = "paragraph"
    TEXT = "text"
    MENTION = "da-mention"


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


@dataclasses.dataclass
class Body:
    """
    A comment's body.

    Args:
        markup: Markup of the comment.
        features: Additional metrics such as wordcount.
    """

    markup: dict
    features: dict

    def __post_init__(self) -> None:
        self.features = {f["type"]: f["data"] for f in self.features}

    @property
    def text(self) -> str:
        """The comment's plain text."""
        contents = (
            c
            for p in self.get_paragraphs()
            for c in p["content"]
            if c["type"] in (ContentKind.TEXT, ContentKind.MENTION)
        )

        lines = [
            (
                c["text"]
                if c["type"] == ContentKind.TEXT
                else c["attrs"]["user"]["username"]
            )
            for c in contents
        ]

        return "\n".join(lines)

    @property
    def mentions(self) -> Iterator[str]:
        """The mentions in this comment."""
        mentions = (
            c
            for p in self.get_paragraphs()
            for c in p["content"]
            if c["type"] == ContentKind.MENTION
        )

        return (m["attrs"]["user"]["username"] for m in mentions)

    @property
    def words(self) -> int:
        """The length of this comment, in words."""
        return self.features["WORD_COUNT_FEATURE"]["words"]

    def get_paragraphs(self) -> Iterator[dict]:
        """
        Get the paragraphs in the markup.

        Returns:
            A list of the paragraphs contained in the markup.
        """
        return (
            c
            for c in self.markup["document"]["content"]
            if c["type"] == ContentKind.PARAGRAPH
        )
