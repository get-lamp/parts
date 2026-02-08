"""
from parser.grammar import Grammar


def test_grammar_keyword_add():
    grammar = Grammar()

    root = grammar.next
    assert root == ["keyword:add", "keyword:list", "keyword:del", "category:identifier", "part:identifier"]

    add = grammar.push(root[0])
    assert add == ["part:identifier", "category:identifier"]

    qty = grammar.push(add[0])
    assert qty == ["part:qty"]

    descript = grammar.push(qty[0])
    assert descript == ["part:description"]

    leaf = grammar.push(descript[0])
    assert leaf is None


def test_grammar_keyword_list():
    grammar = Grammar()

    root = grammar.next
    assert root == ["keyword:add", "keyword:list", "keyword:del", "category:identifier", "part:identifier"]

    list_ = grammar.push(root[1])
    assert list_ == ["category:identifier"]

    slash = grammar.push(list_[0])
    assert slash == [None, "operator:/", "part:identifier"]

    recursion = grammar.push(slash[1])
    assert recursion == [None, "operator:/", "part:identifier"]

    leaf = grammar.push(slash[2])
    assert leaf is None
"""

from parts import parser as g
from unittest.mock import ANY
import pytest


@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        ("CD4009", {None: None, g.OP_PLUS: ANY}),
        ("CD4009 +", {g.NUMBER: None}),
        ("CD4009 + 5", None),
        ("CD4009 + 5 +", None),
        ("add", {g.PART_ID: ANY, g.CAT_ID: ANY}),
    ],
)
def test_parse_success(sentence, expected):
    assert g.parse(sentence) == expected


def test_parse_fail():
    # es, ts = zip(*map(lambda s: s.split(':'), g.parse('').keys()))
    pass
