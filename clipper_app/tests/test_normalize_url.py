import pytest

from clipper_app.clipper import normalize_url


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ""),
        ("   ", ""),
        ("example.com", "https://example.com"),
        ("http://example.com", "http://example.com"),
        ("https://example.com", "https://example.com"),
        ("HTTPS://Example.com", "HTTPS://Example.com"),
        ("ftp://example.com", "ftp://example.com"),
        ("mailto:user@example.com", "mailto:user@example.com"),
    ],
)
def test_normalize_url(raw, expected):
    assert normalize_url(raw) == expected
