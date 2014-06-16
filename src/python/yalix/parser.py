#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes a stream of characters and produces an Abstract Syntax Tree
"""

#from yalix.interpreter import Atom
from pyparsing import *
from yalix.interpreter.primitives import Atom, BuiltIn, Sexp
from yalix.interpreter.builtins import Symbol
import operator
import pprint

class SexpConverter(TokenConverter):
    """
    Converter to return the matched tokens as a Sexp
    """
    def __init__(self, expr):
        super(SexpConverter, self).__init__(expr)
        #self.saveAsList = True

    def postParse(self, instring, loc, tokenlist):
        return Sexp(*tokenlist)


def scheme_parser(debug=False):
    # Simple BNF representation of S-Expressions

    # Atoms
    integer = Regex(r"[+-]?\d+").setParseAction(lambda tokens: Atom(int(tokens[0])))
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?").setParseAction(lambda tokens: Atom(float(tokens[0])))
    boolean = (Keyword("#t") | Keyword("#f")).setParseAction(lambda tokens: Atom(tokens[0] == '#t'))
    dblQuotedString.setParseAction(lambda s,l,t: Atom(removeQuotes(s,l,t)))

    atom = real | integer | boolean | dblQuotedString

    # Symbols
    symbol = Word(alphanums + "-./_:*+=!?<>").setParseAction(lambda tokens: Symbol(tokens[0]))

    # Built-ins
    built_in = reduce(operator.or_,
                      map(Keyword,
                          sorted(BuiltIn.classes.keys(),
                                 reverse=True, key=lambda x: len(x))))

    built_in.setParseAction(lambda tokens: BuiltIn(tokens[0]))

    LPAREN = Suppress("(")
    RPAREN = Suppress(")")

    body = Forward()
    body << ( atom | SexpConverter(LPAREN + built_in + ZeroOrMore(body) + RPAREN) | symbol | Group( LPAREN + ZeroOrMore(body) + RPAREN ) )

    form = Forward()
    form << OneOrMore( atom | SexpConverter(LPAREN + built_in + ZeroOrMore(body) + RPAREN) | symbol | SexpConverter( LPAREN + ZeroOrMore(form) + RPAREN ) )
    form.setDebug(debug)
    return form


def parse(text):
    result = scheme_parser().parseString(text, parseAll=True)
    for sexp in result.asList():
        yield sexp


