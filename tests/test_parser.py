from unittest.mock import ANY
import pytest
from parts import parser as g


def test_get_word_types_keywords():
    assert g.PART_ID in g._get_word_types("N555")
    assert g.CAT_ID in g._get_word_types("counter")
    assert g.OP_PLUS in g._get_word_types("+")
    assert g.OP_MINUS in g._get_word_types("-")
    assert g.OP_SLASH in g._get_word_types("/")


def test_get_word_types_numbers():
    assert g.NUMBER in g._get_word_types("42")
    assert g.NUMBER in g._get_word_types("0")


@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        # part identifier alone
        ("N555", {None: None, g.OP_PLUS: ANY, g.OP_MINUS: ANY, g.NUMBER: ANY}),
        # part + (expects number next)
        ("N555 +", {g.NUMBER: None}),
        # part - (expects number next)
        ("N555 -", {g.NUMBER: None}),
        # part + number (terminal)
        ("N555 + 5", None),
        # part - number (terminal)
        ("N555 - 1", None),
        # part + number + extra garbage (invalid)
        ("N555 + 5 +", {}),
        # part bare number (set qty, terminal)
        ("N555 0", {None: None}),
        # part bare number + extra (invalid)
        ("N555 0 +", {}),
        # part - number + extra (invalid)
        ("N555 - 1 0", {}),
        # add command root
        ("add", {g.PART_ID: ANY, g.CAT_ID: ANY}),
        # category identifier alone
        ("counter", {None: None, g.OP_SLASH: ANY, g.PART_ID: ANY}),
        # category / (returns callable — pre-existing limitation)
        ("counter /", lambda x: callable(x)),
    ],
)
def test_parse(sentence, expected):
    result = g.parse(sentence)
    if callable(expected):
        assert expected(result)
    else:
        assert result == expected


def test_parse_empty():
    assert g.parse("") == g._grammar


def test_parse_keywords():
    assert g.parse("list") == {g.CAT_ID: ANY}
    assert g.parse("del") == {g.CAT_ID: ANY}
    assert g.parse("datasheet") == {g.CAT_ID: ANY}
