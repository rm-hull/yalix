#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Takes a stream of characters and produces an Abstract Syntax Tree"""

from pyparsing import *
from yalix.interpreter.primitives import *
from yalix.interpreter.builtins import *


def _specialForm(builtinClass):
    def invoke(src, loc, tokens):
        return builtinClass(*tokens)
    return invoke

def _atom(converter):
    def invoke(src, loc, tokens):
        return Atom(converter(tokens[0]))
    return invoke

def scheme_parser(debug=False):
    # Simple BNF representation of S-Expressions

    LPAREN = Suppress('(')
    RPAREN = Suppress(')')

    LBRACKET = Suppress('[')
    RBRACKET = Suppress(']')

    comment = Suppress(Regex(r";.*"))

    # Atoms
    integer = Regex(r"[+-]?\d+")
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?")
    boolean = (Keyword("#t") | Keyword("#f"))

    atom = real | integer | boolean | dblQuotedString

    expr = Forward()

    body = ZeroOrMore(expr)
    binding_form = Word(alphanums + "-/_:*+=!?<>")
    formals = Group(ZeroOrMore(binding_form) + Optional(Keyword('.') + binding_form))

    let = (LPAREN + Suppress('let') + LPAREN + binding_form + expr + RPAREN + body + RPAREN)
    let_STAR = (LPAREN + Suppress('let*') + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN)
    letrec = (LPAREN + Suppress('letrec') + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN)
    if_ = (LPAREN + Suppress('if') + expr + expr + Optional(expr) + RPAREN)
    define = (LPAREN + Suppress('define') + binding_form + expr + RPAREN)
    defun = (LPAREN + Suppress('define') + LPAREN + binding_form + formals + RPAREN + body + RPAREN)
    quote = (LPAREN + Suppress('quote') + expr + RPAREN) | Suppress('\'') + expr
    list_ = (LBRACKET + ZeroOrMore(expr) + RBRACKET) | (LPAREN + Suppress('list') + ZeroOrMore(expr) + RPAREN)
    lambda_ = (LPAREN + (Suppress('lambda') | Suppress('λ')) + LPAREN + formals + RPAREN + body + RPAREN)

    # Built-ins
    built_in = let_STAR | letrec | let | if_ | defun | define | quote | lambda_ | list_

    # Symbols
    symbol = Word(alphanums + "-/_:*+=!?<>")

    # Expressions
    sexp = (LPAREN + expr + ZeroOrMore(expr) + RPAREN)
    expr << (atom | built_in | symbol | sexp)
    expr.ignore(comment).setDebug(debug)

    # Parse actions
    for name, var, fn in [
            ('integer',             integer,            _atom(int)),
            ('real number',         real,               _atom(float)),
            ('boolean',             boolean,            _atom(lambda x: x == '#t')),
            ('string',              dblQuotedString,    _atom(lambda x: x[1:-1])),
            ('symbol',              symbol,             _specialForm(Symbol)),
            ('let',                 let,                _specialForm(Let)),
            ('let* binding',        let_STAR,           _specialForm(Let_STAR)),
            ('letrec binding',      letrec,             _specialForm(LetRec)),
            ('conditional',         if_,                _specialForm(If)),
            ('definition',          define,             _specialForm(Define)),
            ('function definition', defun,              _specialForm(DefineFunction)),
            ('quote',               quote,              _specialForm(Quote)),
            ('list',                list_,              _specialForm(List)),
            ('lambda',              lambda_,            _specialForm(Lambda)),
            ('S-expression',        sexp,               _specialForm(Call))]:
        var.setParseAction(fn)
        var.setName(name)

    return ZeroOrMore(expr)
