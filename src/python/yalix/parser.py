#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Takes a stream of characters and produces an Abstract Syntax Tree"""

from pyparsing import *
from yalix.interpreter import *

ParserElement.enablePackrat()


def _brand(obj, src, loc):
    """ As the object was derived from some source, brand it so """
    setattr(obj, '__source__', src)
    setattr(obj, '__location__', loc)
    return obj


def _specialForm(builtinClass):
    def invoke(src, loc, tokens):
        return _brand(builtinClass(*tokens), src, loc)
    return invoke


def _atom(converter):
    def invoke(src, loc, tokens):
        return _brand(Atom(converter(tokens[0])), src, loc)
    return invoke


def scheme_parser(debug=False):
    # Simple BNF representation of S-Expressions

    LPAREN = Suppress('(')
    RPAREN = Suppress(')')

    comment = Suppress(Regex(r";[^^].*"))
    docString = Regex(r";\^.*")

    # Atoms
    integer = Regex(r"[+-]?\d+") + Suppress(Optional('L'))
    hex_ = Regex(r"0x[0-9a-fA-F]+")
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?")
    boolean = (Keyword("#t") | Keyword("#f"))
    symbol = Word(alphanums + "-/_:*+=!?<>.") | Keyword('λ')

    atom = real | hex_ | integer | boolean | dblQuotedString | symbol

    expr = Forward()

    quote = Suppress('\'') + expr

    # Expressions
    sexp = (LPAREN + ZeroOrMore(expr) + RPAREN)
    expr << (atom | quote | sexp | docString)
    expr.ignore(comment).setDebug(debug)

    # Parse actions
    for name, var, fn in [
            ('integer',             integer,            _atom(int)),
            ('real number',         real,               _atom(float)),
            ('hex',                 hex_,               _atom(lambda x: int(x, 0))),
            ('boolean',             boolean,            _atom(lambda x: x == '#t')),
            ('string',              dblQuotedString,    _atom(lambda x: x[1:-1])),
            ('symbol',              symbol,             _specialForm(Symbol)),
            ('quote',               quote,              _specialForm(Quote)),
            ('S-expression',        sexp,               _specialForm(List))]:
        var.setParseAction(fn)
        var.setName(name)

    return ZeroOrMore(expr)
