import pytest
from maplink import compile_regex_from_source

result = [
    (
        "/path/to/{this}.{set}.py",
        "/path/to/(?P<this>[A-Za-z0-9]+).(?P<set>[A-Za-z0-9]+).py",
    ),
    (
        "/path/{another}o/{this}.{set}.py",
        "/path/(?P<another>[A-Za-z0-9]+)o/(?P<this>[A-Za-z0-9]+).(?P<set>[A-Za-z0-9]+).py",
    ),
    (
        "/path/to/{this}.{set:[A-Z_]+}.py",
        "/path/to/(?P<this>[A-Za-z0-9]+).(?P<set>[A-Z_]+).py",
    ),
]


@pytest.mark.parametrize(
    "string_template,expected_regex",
    result,
)
def test_compile_regex_should_handle_mixed_default_and_overrides(
    string_template, expected_regex
):
    regex = compile_regex_from_source(string_template)

    assert regex.pattern == expected_regex


def test_compile_regex_should_error_if_internal_braces_provided():
    with pytest.raises(ValueError):
        compile_regex_from_source("/path/to/{this:[A-Za-z]{5}}.txt")


def test_compile_regex_should_error_if_unmatched_braces():
    pass


def test_compile_regex_should_error_if_invalid_regex():
    pass
