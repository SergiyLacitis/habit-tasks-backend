import pytest

from habit_tasks.utils import camel_case_to_snake_case


@pytest.mark.parametrize(
    "s,res",
    [
        ("SomeName", "some_name"),
        ("some123Name", "some123_name"),
        ("URLParser", "url_parser"),
        ("HTTPResponse", "http_response"),
    ],
)
def test_camel_case_to_snake_case(s, res):
    assert camel_case_to_snake_case(s) == res
