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

    comment = Suppress(Regex(r";.*"))  # TODO

    # Atoms
    integer = Regex(r"[+-]?\d+")
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?")
    boolean = (Keyword("#t") | Keyword("#f"))

    atom = real | integer | boolean | dblQuotedString

    expr = Forward()

    body = ZeroOrMore(expr)
    binding_form = Word(alphanums + "-./_:*+=!?<>")
    formals = Group(ZeroOrMore(binding_form))

    let = (LPAREN + Suppress('let') + LPAREN + binding_form + expr + RPAREN + body + RPAREN)
    let_STAR = (LPAREN + Suppress('let*') + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN)
    if_ = (LPAREN + Suppress('if') + expr + expr + Optional(expr) + RPAREN)
    define = (LPAREN + Suppress('define') + binding_form + expr + RPAREN)
    defun = (LPAREN + Suppress('define') + LPAREN + binding_form + formals + RPAREN + body + RPAREN)
    quote = (LPAREN + Suppress('quote') + expr + RPAREN) | Suppress('\'') + expr
    list_ = (LBRACKET + ZeroOrMore(expr) + RBRACKET) | (LPAREN + Suppress('list') + ZeroOrMore(expr) + RPAREN)
    lambda_ = (LPAREN + (Suppress('lambda') | Suppress('λ')) + LPAREN + formals + RPAREN + body + RPAREN)

    # Built-ins
    built_in = let_STAR ^ let ^ if_ ^ defun ^ define ^ quote ^ lambda_ ^ list_

    # Symbols
    symbol = Word(alphanums + "-./_:*+=!?<>")

    # Expressions
    sexp = (LPAREN + symbol + ZeroOrMore(expr) + RPAREN)
    expr << (atom | built_in | symbol | sexp)
    expr.ignore(comment).setDebug(debug)

    # Parse actions
    integer.setParseAction(lambda tokens: Atom(int(tokens[0]))).setName('integer')
    real.setParseAction(lambda tokens: Atom(float(tokens[0]))).setName('real number')
    boolean.setParseAction(lambda tokens: Atom(tokens[0] == '#t')).setName('boolean')
    dblQuotedString.setParseAction(lambda s, l, t: Atom(removeQuotes(s, l, t))).setName('string')
    symbol.setParseAction(specialForm(Symbol)).setName('symbol')
    let.setParseAction(specialForm(Let)).setName('let binding')
    let_STAR.setParseAction(specialForm(Let_STAR)).setName('let* binding')
    if_.setParseAction(specialForm(If)).setName('conditional')
    define.setParseAction(specialForm(Define)).setName('definition')
    defun.setParseAction(specialForm(DefineFunction)).setName('function definition')
    quote.setParseAction(specialForm(Quote)).setName('quote')
    list_.setParseAction(specialForm(List)).setName('list')
    lambda_.setParseAction(specialForm(Lambda)).setName('lambda')
    sexp.setParseAction(specialForm(Call)).setName('S-expression')
    return ZeroOrMore(expr)


def parse(text):
    result = scheme_parser().parseString(text, parseAll=True)
    for ast in result.asList():
        yield ast
