#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import operator

from yalix.utils import array_to_linked_list
from yalix.environment import Env
from yalix.interpreter.primitives import *
from yalix.interpreter.builtins import *


class BuiltinsTest(unittest.TestCase):

    def test_list(self):
        env = Env()
        lst = List(Atom(4), Atom(2), Atom(3)).eval(env)
        self.assertEqual((4, (2, (3, None))), lst)

    def let_binding_test(self):
        env = Env()
        lst = Let("f",
                  Atom("Hello"),
                  List(Symbol("f"),
                       Symbol("f"))).eval(env)
        self.assertEqual(('Hello', ('Hello', None)), lst)

    def let_STAR_shadow_binding_test(self):
        env = Env()
        lst = Let_STAR(['a', Atom('Hello'),
                        'b', List(Atom(1), Atom(2), Atom(3)),
                        'c', Atom('World'),
                        'c', List(Atom('Big'), Symbol('c'))],  # <-- re-def shadowing
                List(Symbol('a'), Symbol('c'), Symbol('b'))).eval(env)
        self.assertEqual(('Hello', (('Big', ('World', None)), ((1, (2, (3, None))), None))), lst)

    def lambda_test(self):
        env = Env()
        value = Let('identity', Lambda(['x'], Symbol('x')),  # <-- anonymous fn
                  Call(Symbol('identity'), Atom(99))).eval(env)
        self.assertEqual(99, value)

    def interop_test(self):
        # InterOp, i.e. using Python functions
        import operator
        env = Env()
        value = InterOp(operator.add, Atom(41), Atom(23)).eval(env)
        self.assertEqual(64, value)

    def define_unicode_test(self):
        env = Env()
        pi = 3.14159265358979323846264338327950288419716939937510
        rho = 1.618033988749894848204586834

        # check unicode, pi & golden ratio
        Define('π', Atom(pi)).eval(env)
        Define('ϕ', Atom(rho)).eval(env)

        self.assertAlmostEqual(pi, env['π'])
        self.assertAlmostEqual(rho, env['ϕ'])

        self.assertAlmostEqual(pi, Symbol('π').eval(env))
        self.assertAlmostEqual(rho, Symbol('ϕ').eval(env))

    def call_test(self):
        env = Env()
        Define('+', Lambda(['x', 'y'],
                           InterOp(operator.add,
                                   Symbol('x'),
                                   Symbol('y')))).eval(env)

        # Three ways to call
        self.assertEqual(154, Call(Symbol('+'), Atom(99), Atom(55)).eval(env))
        self.assertEqual(154, Call([Symbol('+'), Atom(99), Atom(55)]).eval(env))
        self.assertEqual(154, Call(array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])).eval(env))

    def quote_test(self):
        env = Env()
        Define('+', Lambda(['x', 'y'],
                           InterOp(operator.add,
                                   Symbol('x'),
                                   Symbol('y')))).eval(env)

        q = Quote([Symbol('+'), Atom(2), Atom(3)]).eval(env)
        value = Call(q).eval(env)
        self.assertEqual(5, value)

        # Call(Quote([Symbol('+'), Atom(2), Atom(3)])).eval(env)

    def conditional_test(self):
        # (let (rnd (random))
        #   (if (< rnd 0.5)
        #     "Unlucky"
        #     (if (< rnd 0.75)
        #       "Close, but no cigar"
        #       "Lucky")))
        #
        #Let('rnd',
        #    Call(Symbol('random')),
        #    If(Call(Symbol('<'), Symbol('rnd'), Atom(0.5)),
        #    Atom("Unlucky"),
        #    If(Call(Symbol('<'), Symbol('rnd'), Atom(0.75)),
        #        Atom("Close, but no cigar"),
        #        Atom("Lucky")))).eval(env)
        pass

    def function_defn_test(self):
        # Equivalent to:
        #   (define factorial
        #     (lambda (x)
        #       (if (zero? x)
        #         1
        #         (* x (factorial (- x 1))))))
        #
        env = Env()
        Define('*', Lambda(['a', 'b'], InterOp(operator.mul, Symbol('a'), Symbol('b')))).eval(env)
        Define('+', Lambda(['a', 'b'], InterOp(operator.add, Symbol('a'), Symbol('b')))).eval(env)
        Define('-', Lambda(['a', 'b'], InterOp(operator.sub, Symbol('a'), Symbol('b')))).eval(env)
        Define('=', Lambda(['a', 'b'], InterOp(operator.eq, Symbol('a'), Symbol('b')))).eval(env)
        Define('zero?', Lambda(['n'], Call(Symbol('='), Symbol('n'), Atom(0)))).eval(env)
        Define('factorial', Lambda(['x'],
                                If(Call(Symbol('zero?'), Symbol('x')),
                                    Atom(1),
                                    Call(Symbol('*'),
                                        Symbol('x'),
                                        Call(Symbol('factorial'),
                                                Call(Symbol('-'),
                                                    Symbol('x'),
                                                    Atom(1))))))).eval(env)

        # (factorial 10)
        value = Call(Symbol('factorial'), Atom(10)).eval(env)
        self.assertEquals(3628800, value)


# Should be in globals
#    def test_gensym(self):
#        # (gensym)
#        g = Call(Symbol('gensym')).eval(env)
#        g
#        g.name

    # =============================================================================================

# Should be in parse test
#test2 = """
#(define *hello* ["world" -1 #t 3.14159 [1 2 3]])
#
#(let (rnd (random))
#  (if (< rnd 0.5)
#    "Unlucky"
#    (if (< rnd 0.75)
#      "Close, but no cigar"
#      "Lucky")))
#
#(define factorial
#  (lambda (x)
#    (if (zero? x)
#      1
#      (* x (factorial (- x 1))))))
#
#(factorial 10)
#
#*hello*
#
#"""
#
## No yet fully supported
## (let* ((x 5)
##        (y (+ x 7))
##        (z (+ y x 2)))
##    (* x y z))
#
#for ptree in parse(test2):
#    print ptree.eval(env)
