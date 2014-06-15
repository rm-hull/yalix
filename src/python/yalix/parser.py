#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes a stream of characters and produces an Abstract Syntax Tree
"""

from yalix.interpreter import Atom
from pyparsing import *
import pprint

def simple_sexp_parser():
    # Simple BNF representation of S-Expressions
    alphaword = Word(alphas)
    integer = Word(nums)
    sexp = Forward()

    LPAREN = Suppress("(")
    RPAREN = Suppress(")")
    sexp << ( alphaword | integer | Group( LPAREN + ZeroOrMore(sexp) + RPAREN ) )

    return sexp

def complete_sexp_parser():
    # Internet Draft for BNF representation of S-Expressions
    # http://people.csail.mit.edu/rivest/Sexp.txt
    base_64_char = alphanums + "+/="
    simple_punc = "-./_:*+="
    token_char = alphanums + simple_punc

    LPAREN, RPAREN, LBRACK, RBRACK = map(Suppress, "()[]")

    bytes = Word( printables )
    decimal = "0" | Word( srange("[1–9]"), nums )
    quoted_string = Optional( decimal ) + dblQuotedString
    hexadecimal = "#" + ZeroOrMore( Word(hexnums) ) + "#"
    base_64 = Optional(decimal) + "|" + ZeroOrMore( Word( base_64_char ) ) + "|"
    token = Word( token_char )
    raw = decimal + ":" + bytes
    simple_string = raw | token | base_64 | hexadecimal | quoted_string
    display = LBRACK + simple_string + RBRACK
    string_ = Optional(display) + simple_string

    sexp = Forward()
    list_ = LPAREN + Group( ZeroOrMore( sexp ) ) + RPAREN
    sexp << ( string_ | list_ )

    return sexp


# =============================================================================================

def scheme_parser(debug=False):
    # Simple BNF representation of S-Expressions
    integer = Regex(r"[+-]?\d+").setParseAction(lambda tokens: ('Atom',int(tokens[0])))
    real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?").setParseAction(lambda tokens: ('Atom',float(tokens[0])))
    boolean = (Keyword("#t") | Keyword("#f")).setParseAction(lambda tokens: ('Atom', tokens[0] == '#t'))
    constant = real | integer | boolean | dblQuotedString
    token = Word(alphanums + "-./_:*+=!<>").setParseAction(lambda tokens: ('Symbol', tokens[0]))

    dblQuotedString.setParseAction(lambda s,l,t: ('Atom', removeQuotes(s,l,t)))

    sexp = Forward()

    LPAREN = Suppress("(")
    RPAREN = Suppress(")")
    sexp << ( constant | token | Group( LPAREN +  ZeroOrMore(sexp) + RPAREN ) )

    sexp.setDebug(debug)
    return sexp

# =============================================================================================

test1 = "(define *hello* (list \"world\" -1 #t 3.14159 (list 1 2 3)))"

scheme_parser(True).parseString(test1).asList()
