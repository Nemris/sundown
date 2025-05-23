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
