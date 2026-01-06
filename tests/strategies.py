"""Common module for custom Hypothesis test strategies."""

from datetime import datetime
import json

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from sundown.comment import ContentKind, MarkKind


@st.composite
def input_tags(draw) -> str:
    """Return HTML input tags with a random name."""
    return f'<input name="{draw(input_field_values())}"/>'


@st.composite
def input_tags_with_token(draw) -> str:
    """Return HTML input tags with a CSRF token."""
    return f'<input name="csrf_token" value="{draw(input_field_values())}"/>'


@st.composite
def input_field_values(draw) -> str:
    """Return values for HTML input tag fields."""
    return draw(st.from_regex(r'[^"]+', fullmatch=True))


@st.composite
def ids(draw) -> str:
    """Return stringified IDs greater than zero."""
    return str(draw(st.integers(1)))


@st.composite
def usernames(draw) -> str:
    """
    Return DeviantArt usernames.

    Valid usernames are at least three characters long and can include
    ASCII letters, digits and hyphens, the latter never as the first or
    last character.
    """
    return draw(st.from_regex(r"[A-Za-z0-9]+[A-Za-z0-9-]+[A-Za-z0-9]+", fullmatch=True))


@st.composite
def deviation_names(draw, with_label: bool = True) -> str:
    """
    Return DeviantArt deviation names.

    Args:
        with_label: If True, prepend the deviation ID with a random
            label.
    """
    id_ = draw(ids())

    if with_label:
        label = draw(st.from_regex(r"[A-Za-z0-9-]+", fullmatch=True))
        return "-".join([label, id_])
    return id_


@st.composite
def deviation_urls(draw, valid: bool = True) -> str:
    """
    Return DeviantArt deviation URLs.

    Args:
        valid: If True, ensure the deviation category is valid, else
            use a randomized string.
    """
    if valid:
        kind = st.one_of(st.just("art"), st.just("journal"))
    else:
        kind = st.from_regex(r"[a-z]+", fullmatch=True).filter(
            lambda n: n not in ["art", "journal"]
        )
    return "/".join(
        [
            "www.deviantart.com",
            draw(usernames()),
            draw(kind),
            draw(deviation_names(with_label=False)),
        ]
    )


@st.composite
def comment_urls(draw, valid: bool = True) -> str:
    """
    Return DeviantArt comment URLs.

    Args:
        valid: If True, ensure the deviation type is valid, else use a
            randomized value.
    """
    if valid:
        type_id = 1
    else:
        type_id = draw(st.integers(min_value=2))
    return "/".join(
        ["www.deviantart.com/comments", str(type_id), draw(ids()), draw(ids())]
    )


@st.composite
def comment_pages(draw, entries: int = 1, valid: bool = True) -> dict:
    """
    Return DeviantArt comment pages.

    Args:
        entries: Amount of comments to place in the page. Note: comments
            are not unique.
        valid: If True, return a blob resembling a page, else return a
            page with invalid metadata.
    """
    has_more = draw(st.booleans())
    has_less = draw(st.booleans())

    # next_offset is at least 1 because we're always at least on the
    # zeroth comment.
    next_offset = draw(st.integers(min_value=1)) if has_more else None
    prev_offset = draw(st.integers(min_value=0)) if has_less else None
    if (next_offset and prev_offset) and next_offset < prev_offset:
        next_offset, prev_offset = prev_offset, next_offset

    page = {
        "hasMore": has_more,
        "hasLess": has_less,
        "nextOffset": next_offset,
        "prevOffset": prev_offset,
        "thread": [draw(comments())] * entries,
    }

    if not valid:
        del page["hasMore"]

    return page


@st.composite
def comments(draw, valid: bool = True) -> dict:
    """
    Return DeviantArt comments.

    Args:
        valid: If True, return a blob resembling a comment, else return
            an empty dict.
    """
    if not valid:
        return {}

    # We convert the required IDs to ints to simulate the data returned
    # by the API.
    if parent_id := draw(st.one_of(st.none(), ids())):
        parent_id = int(parent_id)

    return {
        "commentId": int(draw(ids())),
        "typeId": 1,
        "itemId": int(draw(ids())),
        "parentId": parent_id,
        "posted": draw(comment_timestamps()),
        "edited": draw(st.one_of(st.none(), comment_timestamps())),
        "replies": draw(st.integers()),
        "textContent": {
            "html": {
                "markup": json.dumps(draw(comment_markups([]))),
                "features": json.dumps(draw(comment_features())),
            },
        },
        "user": {"username": draw(usernames())},
    }


@st.composite
def comment_markups(
    draw, contents: list[SearchStrategy[dict]], paragraphs: int = 1
) -> dict:
    """
    Return DeviantArt comment markups.

    Args:
        contents: Strategies to generate paragraph contents. Each
            paragraph will contain only one content, shrinking to
            strategies earlier in the list (see Hypothesis one_of()
            documentation).
        paragraphs: Amount of paragraphs to generate.
    """
    pars = []
    for _ in range(paragraphs):
        p = {"type": "paragraph"}

        if not contents:
            pars.append(p)
            continue

        p["content"] = [draw(st.one_of(contents))]
        pars.append(p)

    return {"document": {"content": pars}}


@st.composite
def comment_features(draw) -> list[dict]:
    """Return DeviantArt comment features."""
    # Only consider the wordcount for the time being.
    return [
        {
            "type": "WORD_COUNT_FEATURE",
            "data": {
                "words": draw(st.integers(min_value=1)),
            },
        }
    ]


def comment_hard_breaks() -> SearchStrategy[dict]:
    """Return a strategy that generates DeviantArt comment hard breaks."""
    return st.just({"type": str(ContentKind.HARD_BREAK)})


@st.composite
def comment_texts(draw, with_link: bool = False) -> dict:
    """
    Return DeviantArt comment texts.

    Args:
        with_link: If True, include a "link" mark in the object.
    """
    alphabet = st.characters(exclude_characters=["\n"])
    text = {"type": str(ContentKind.TEXT), "text": draw(st.text(alphabet, min_size=1))}

    if with_link:
        text["marks"] = [draw(comment_links())]

    return text


@st.composite
def comment_links(draw) -> dict:
    """Return DeviantArt comment marks of type "link"."""
    return {"type": str(MarkKind.LINK), "attrs": {"href": draw(comment_urls())}}


@st.composite
def comment_timestamps(draw) -> str:
    """Return datetimes used in DeviantArt comments."""
    # NOTE: workaround for https://github.com/python/cpython/issues/120713.
    dt = draw(st.datetimes(min_value=datetime(1000, 1, 1)))

    # Mimic DA's timestamp format and timezone.
    return dt.strftime("%Y-%m-%dT%H:%M:%S-0800")


@st.composite
def user_mentions(draw) -> dict:
    """Return DeviantArt user mentions."""
    return {
        "type": str(ContentKind.MENTION),
        "attrs": {"user": {"username": draw(usernames()), "type": ""}},
    }
