#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Takes a stream of characters and produces an Abstract Syntax Tree"""

from pyparsing import *
from yalix.interpreter.primitives import *
from yalix.interpreter.builtins import *

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

    let = (LPAREN + Suppress(Keyword('let')) + LPAREN + binding_form + expr + RPAREN + body + RPAREN)
    let_STAR = (LPAREN + Suppress(Keyword('let*')) + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN)
    letrec = (LPAREN + Suppress(Keyword('letrec')) + LPAREN + Group(OneOrMore(LPAREN + binding_form + expr + RPAREN)) + RPAREN + body + RPAREN)
    if_ = (LPAREN + Suppress(Keyword('if')) + expr + expr + Optional(expr) + RPAREN)
    define = (LPAREN + Suppress(Keyword('define')) + binding_form + expr + RPAREN)
    defun = (LPAREN + Suppress(Keyword('define')) + LPAREN + binding_form + formals + RPAREN + body + RPAREN)
    quote = (LPAREN + Suppress(Keyword('quote')) + expr + RPAREN) | Suppress('\'') + expr
    list_ = (LBRACKET + ZeroOrMore(expr) + RBRACKET) | (LPAREN + Suppress(Keyword('list')) + ZeroOrMore(expr) + RPAREN)
    lambda_ = (LPAREN + (Suppress(Keyword('lambda')) | Suppress(Keyword('λ'))) + LPAREN + formals + RPAREN + body + RPAREN)
    begin = (LPAREN + Suppress(Keyword('begin')) + body + RPAREN)
    delay = (LPAREN + Suppress(Keyword('delay')) + expr + RPAREN)
    set_PLING = (LPAREN + Suppress(Keyword('set!')) + binding_form + expr + RPAREN)

    # Built-ins
    built_in = let_STAR | letrec | let | if_ | defun | define | quote | lambda_ | list_ | begin | delay | set_PLING

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
            ('begin',               begin,              _specialForm(Body)),
            ('delay',               delay,              _specialForm(Delay)),
            ('set!',                set_PLING,          _specialForm(Set_PLING)),
            ('S-expression',        sexp,               _specialForm(Call))]:
        var.setParseAction(fn)
        var.setName(name)

    return ZeroOrMore(expr)
