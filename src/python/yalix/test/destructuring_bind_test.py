#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.globals import create_initial_env
from yalix.interpreter import Closure, List, Atom, Symbol, Lambda, Realize, Repr

ENV = create_initial_env()


class DestructuringBindTests(unittest.TestCase):

    def test_fixed_args(self):
        formals = List(Symbol('x'), Symbol('y'))
        params = List(Atom(3), Atom(4))
        extended_env = Closure.bind(ENV, formals, params, ENV)

        self.assertEqual(3, extended_env['x'])
        self.assertEqual(4, extended_env['y'])

    def test_required_and_variadic_args(self):
        formals = List(Symbol('x'), Lambda.VARIADIC_MARKER, Symbol('xs'))
        params = List(Atom(3), Atom(4), Atom(5), Atom(6))
        extended_env = Closure.bind(ENV, formals, params, ENV)

        self.assertEqual(3, extended_env['x'])
        self.assertEqual([4, 5, 6], Realize(extended_env['xs']).eval(extended_env))

    def test_symbol_binding(self):
        pass

    def test_nested_binding(self):
        pass

if __name__ == '__main__':
    unittest.main()
