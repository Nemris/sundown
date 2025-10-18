"""Common module for custom Hypothesis test strategies."""

from datetime import datetime
import json

from hypothesis import strategies as st

from sundown.comment import ContentKind


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
def deviation_names(draw, with_label=True) -> str:
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
def deviation_urls(draw, valid=True) -> str:
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
def comment_urls(draw, valid=True) -> str:
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
def comments(draw, valid=True) -> dict:
    """
    Return DeviantArt comments.

    Args:
        value: If True, return a blob resembling a comment, else return
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
                "markup": json.dumps(draw(comment_markups())),
                "features": json.dumps(draw(comment_features())),
            },
        },
        "user": {"username": draw(usernames())},
    }


@st.composite
def comment_markups(draw, paragraphs: int = 1, allow_mentions: bool = False) -> dict:
    """
    Return DeviantArt comment markups.

    Args:
        paragraphs: Amount of paragraphs to generate.
        allow_mentions: If True, allow some paragraphs to contain a
            mention instead of text. Note: it's not guaranteed that
                the final markup will have mentions.
    """
    pars = []
    for _ in range(paragraphs):
        con = (
            draw(st.one_of(comment_texts(), user_mentions()))
            if allow_mentions
            else draw(comment_texts())
        )
        par = {"type": "paragraph", "content": [con]}
        pars.append(par)

    return {"document": {"content": pars}}


@st.composite
def comment_features(draw):
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


@st.composite
def comment_texts(draw) -> dict:
    """Return DeviantArt comment texts."""
    alphabet = st.characters(exclude_characters=["\n"])
    return {"type": str(ContentKind.TEXT), "text": draw(st.text(alphabet, min_size=1))}


@st.composite
def comment_timestamps(draw) -> str:
    """Return datetimes used in DeviantArt comments."""
    # NOTE: workaround for https://github.com/python/cpython/issues/120713.
    dt = draw(st.datetimes(min_value=datetime.fromisoformat("1000-01-01T00:00:00")))

    # Mimic DA's timestamp format and timezone.
    return dt.strftime("%Y-%m-%dT%H:%M:%S-0800")


@st.composite
def user_mentions(draw) -> dict:
    """Return DeviantArt user mentions."""
    return {
        "type": str(ContentKind.MENTION),
        "attrs": {"user": {"username": draw(usernames()), "type": ""}},
    }
