"""Common module for custom Hypothesis test strategies."""

from hypothesis import strategies as st


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
