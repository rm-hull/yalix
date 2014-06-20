#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Takes a stream of characters and produces an Abstract Syntax Tree"""

from pyparsing import *
from yalix.interpreter.primitives import *
from yalix.interpreter.builtins import *


def specialForm(builtinClass):
    def invoke(tokens):
        return builtinClass(*tokens)
    return invoke


def scheme_parser(debug=False):
    # Simple BNF representation of S-Expressions

    LPAREN = Suppress('(')
    RPAREN = Suppress(')')

    LBRACKET = Suppress('[')
    RBRACKET = Suppress(']')

    # Atoms
    integer = Regex(r"[+-]?\d+").setParseAction(lambda tokens: Atom(int(tokens[0])))
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?").setParseAction(lambda tokens: Atom(float(tokens[0])))
    boolean = (Keyword("#t") | Keyword("#f")).setParseAction(lambda tokens: Atom(tokens[0] == '#t'))
    dblQuotedString.setParseAction(lambda s, l, t: Atom(removeQuotes(s, l, t)))

    atom = real | integer | boolean | dblQuotedString

    # Symbols
    symbol = Word(alphanums + "-./_:*+=!?<>").setParseAction(specialForm(Symbol))

    expr = Forward()

    body = ZeroOrMore(expr)
    binding_form = Word(alphanums + "-./_:*+=!?<>")
    let = (LPAREN + Suppress('let') + LPAREN + binding_form + expr + RPAREN + body + RPAREN).setParseAction(specialForm(Let))
    let_STAR = (LPAREN + Suppress('let*') + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN).setParseAction(specialForm(Let_STAR))
    if_ = (LPAREN + Suppress('if') + expr + expr + Optional(expr) + RPAREN).setParseAction(specialForm(If))
    define = (LPAREN + Suppress('define') + binding_form + expr + RPAREN).setParseAction(specialForm(Define))
    quote = (LPAREN + Suppress('quote') + expr + RPAREN).setParseAction(specialForm(Quote))
    list_ = (LBRACKET + ZeroOrMore(expr) + RBRACKET).setParseAction(specialForm(List))

    formals = (LPAREN + Group(ZeroOrMore(binding_form)) + RPAREN)
    lambda_ = (LPAREN + Suppress('lambda') + formals + body + RPAREN).setParseAction(specialForm(Lambda))

    # Built-ins
    built_in = let ^ if_ ^ define ^ quote ^ lambda_ ^ list_

    sexp = (LPAREN + symbol + ZeroOrMore(expr) + RPAREN).setParseAction(specialForm(Call))
    expr << (atom | built_in | symbol | sexp)
    expr.setDebug(debug)
    return ZeroOrMore(expr)


def parse(text):
    result = scheme_parser().parseString(text, parseAll=True)
    for sexp in result.asList():
        yield sexp
