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
    integer = Regex(r"[+-]?\d+")
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?")
    boolean = (Keyword("#t") | Keyword("#f"))

    atom = real | integer | boolean | dblQuotedString

    # Symbols
    symbol = Word(alphanums + "-./_:*+=!?<>")

    expr = Forward()

    body = ZeroOrMore(expr)
    binding_form = Word(alphanums + "-./_:*+=!?<>")
    formals = Group(ZeroOrMore(binding_form))

    let = (LPAREN + Suppress('let') + LPAREN + binding_form + expr + RPAREN + body + RPAREN)
    let_STAR = (LPAREN + Suppress('let*') + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN)
    if_ = (LPAREN + Suppress('if') + expr + expr + Optional(expr) + RPAREN)
    define = (LPAREN + Suppress('define') + binding_form + expr + RPAREN)
    defun = (LPAREN + Suppress('define') + LPAREN + binding_form + formals + RPAREN + body + RPAREN)
    quote = (LPAREN + Suppress('quote') + expr + RPAREN)
    list_ = (LBRACKET + ZeroOrMore(expr) + RBRACKET) | (LPAREN + Suppress('list') + ZeroOrMore(expr) + RPAREN)
    lambda_ = (LPAREN + Suppress('lambda') + LPAREN + formals + RPAREN + body + RPAREN)

    # Built-ins
    built_in = let_STAR ^ let ^ if_ ^ defun ^ define ^ quote ^ lambda_ ^ list_

    sexp = (LPAREN + symbol + ZeroOrMore(expr) + RPAREN)
    expr << (atom | built_in | symbol | sexp)
    expr.setDebug(debug)

    # Parse actions
    integer.setParseAction(lambda tokens: Atom(int(tokens[0])))
    real.setParseAction(lambda tokens: Atom(float(tokens[0])))
    boolean.setParseAction(lambda tokens: Atom(tokens[0] == '#t'))
    dblQuotedString.setParseAction(lambda s, l, t: Atom(removeQuotes(s, l, t)))
    symbol.setParseAction(specialForm(Symbol))
    let.setParseAction(specialForm(Let))
    let_STAR.setParseAction(specialForm(Let_STAR))
    if_.setParseAction(specialForm(If))
    define.setParseAction(specialForm(Define))
    defun.setParseAction(specialForm(DefineFunction))
    quote.setParseAction(specialForm(Quote))
    list_.setParseAction(specialForm(List))
    lambda_.setParseAction(specialForm(Lambda))
    sexp.setParseAction(specialForm(Call))
    return ZeroOrMore(expr)


def parse(text):
    result = scheme_parser().parseString(text, parseAll=True)
    for sexp in result.asList():
        yield sexp
