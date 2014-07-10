#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import operator

from yalix.environment import Env
from yalix.interpreter import *


def make_env():
    env = Env()
    env['*debug*'] = Atom(False)

    Define(List(Symbol('cons'), Symbol('a'), Symbol('b')), InterOp(lambda a, b: (a, b), Symbol('a'), Symbol('b'))).eval(env)
    Define(Symbol('<'), Lambda(List(Symbol('a'), Symbol('b')), InterOp(operator.lt, Symbol('a'), Symbol('b')))).eval(env)
    Define(Symbol('*'), Lambda(List(Symbol('a'), Symbol('b')), InterOp(operator.mul, Symbol('a'), Symbol('b')))).eval(env)
    Define(Symbol('+'), Lambda(List(Symbol('a'), Symbol('b')), InterOp(operator.add, Symbol('a'), Symbol('b')))).eval(env)
    Define(Symbol('-'), Lambda(List(Symbol('a'), Symbol('b')), InterOp(operator.sub, Symbol('a'), Symbol('b')))).eval(env)
    Define(Symbol('='), Lambda(List(Symbol('a'), Symbol('b')), InterOp(operator.eq, Symbol('a'), Symbol('b')))).eval(env)
    Define(Symbol('zero?'), Lambda(List(Symbol('n')), List(Symbol('='), Symbol('n'), Atom(0)))).eval(env)

    return env


def make_linked_list(*arr):
    t = Atom(None)
    while arr:
        t = List(Symbol('cons'), arr[-1], t)
        arr = arr[:-1]
    return t


class Caller(object):

    def __init__(self, funexp, *params):
        self.funexp = funexp
        self.params = params


class BuiltinsTest(unittest.TestCase):

    def test_let_binding(self):
        env = make_env()

        lst = Let(List(Symbol("f"), Atom("Hello")),
                  make_linked_list(Symbol("f"), Symbol("f"))).eval(env)
        self.assertEqual(('Hello', ('Hello', None)), lst)

    def test_let_STAR_shadow_binding(self):
        env = make_env()

        lst = Let_STAR(List(List(Symbol('a'), Atom('Hello')),
                            List(Symbol('b'), make_linked_list(Atom(1), Atom(2), Atom(3))),
                            List(Symbol('c'), Atom('World')),
                            List(Symbol('c'), make_linked_list(Atom('Big'), Symbol('c')))),  # <-- re-def shadowing
                make_linked_list(Symbol('a'), Symbol('c'), Symbol('b'))).eval(env)
        self.assertEqual(('Hello', (('Big', ('World', None)), ((1, (2, (3, None))), None))), lst)

    def test_letrec(self):
        # (define (sum n)
        #   (letrec ((accum (λ (x)
        #                     (if (< x n)
        #                       (+ x (accum (+ x 1)))
        #                       0))))
        #     (accum 0)))
        env = make_env()

        Define(List(Symbol('sum'), Symbol('n')),
                       LetRec(List(List(Symbol('accum'),
                                    Lambda(List(Symbol('x')),
                                            If(List(Symbol('<'), Symbol('x'), Symbol('n')),
                                                List(Symbol('+'),
                                                    Symbol('x'),
                                                    List(Symbol('accum'),
                                                        List(Symbol('+'),
                                                                Symbol('x'),
                                                                Atom(1)))),
                                            Atom(0))))),
                              List(Symbol('accum'), Atom(0)))).eval(env)

        # (sum 45)
        value = List(Symbol('sum'), Atom(45)).eval(env)
        self.assertEqual(990, value)

    def test_lambda(self):
        env = make_env()
        value = Let(List(Symbol('identity'), Lambda(List(Symbol('x')), Symbol('x'))),  # <-- anonymous fn
                  List(Symbol('identity'), Atom(99))).eval(env)
        self.assertEqual(99, value)

    def test_lambda_duplicated_formals(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Lambda(List(Symbol('x'), Symbol('y'), Symbol('x'), Symbol('z')), Symbol('x')).eval(env)

    def test_lambda_variadic(self):
        env = make_env()
        Define(List(Symbol('list*'), Symbol('.'), Symbol('xs')), Symbol('xs')).eval(env)
        values = List(Symbol('list*'), Atom(1), Atom(2), Atom(3)).eval(env)
        caller = Caller('n/a')
        self.assertEqual(1, values[0])
        values = values[1].call(env, caller)
        self.assertEqual(2, values[0])
        values = values[1].call(env, caller)
        self.assertEqual(3, values[0])
        values = values[1].call(env, caller)
        self.assertEqual(None, values)

    def test_lambda_only_one_variadic_arg(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Define(List(Symbol('list*'), Symbol('.'), Symbol('xs'), Symbol('ys')), Symbol('xs')).eval(env)

    def test_lambda_invalid_variadic_spec(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Define(List(Symbol('list*'), Symbol('.'), Symbol('xs'), Symbol('.')), Symbol('xs')).eval(env)

    def test_interop(self):
        # InterOp, i.e. using Python functions
        import operator
        env = make_env()
        value = InterOp(operator.add, Atom(41), Atom(23)).eval(env)
        self.assertEqual(64, value)

    def test_define_unicode(self):
        env = make_env()
        pi = 3.14159265358979323846264338327950288419716939937510
        rho = 1.618033988749894848204586834

        # check unicode, pi & golden ratio
        Define(Symbol('π'), Atom(pi)).eval(env)
        Define(Symbol('ϕ'), Atom(rho)).eval(env)

        self.assertAlmostEqual(pi, env['π'])
        self.assertAlmostEqual(rho, env['ϕ'])

        self.assertAlmostEqual(pi, Symbol('π').eval(env))
        self.assertAlmostEqual(rho, Symbol('ϕ').eval(env))

    def test_call(self):
        env = make_env()
        self.assertEqual(154, List(Symbol('+'), Atom(99), Atom(55)).eval(env))

    def test_call_non_closure(self):
        env = make_env()
        Define(Symbol('barf'), Atom('barf')).eval(env)

        with self.assertRaises(EvaluationError):
            List(Symbol('barf'), Atom(3)).eval(env)

    def test_call_wrong_arity(self):
        env = make_env()

        # Porridge is too cold
        with self.assertRaises(EvaluationError):
            List(Symbol('+'), Atom(3)).eval(env)

        # Porridge is too hot
        with self.assertRaises(EvaluationError):
            List(Symbol('+'), Atom(3), Atom(4), Atom(5)).eval(env)

    def test_symbol(self):
        env = make_env().extend('fred', 45)
        s = Symbol('fred')
        self.assertEqual(45, s.eval(env))
        self.assertEqual('fred', repr(s))

    def test_symbol_equality(self):
        s1 = Symbol('fred')
        s2 = Symbol('fred')
        s3 = Symbol('jim')
        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)

    def test_symbol_hash(self):
        s1 = Symbol('fred')
        s2 = Symbol('fred')
        s3 = Symbol('jim')
        self.assertEqual(hash(s1), hash(s2))
        self.assertNotEqual(hash(s1), hash(s3))
        self.assertNotEqual(hash(s1), hash('fred'))
        self.assertNotEqual(hash(s2), hash('fred'))
        self.assertNotEqual(hash(s2), hash('jim'))
        self.assertEquals(2, len(set([s1, s2, s3])))

    def test_quote_atom(self):
        env = make_env()
        q = Quote(Atom(5)).eval(env)
        self.assertIsInstance(q, int)
        self.assertEquals(5, q)

    def test_quote_symbol(self):
        env = make_env()
        q = Quote(Symbol('toil')).eval(env)
        self.assertIsInstance(q, Symbol)
        self.assertEquals('toil', q.name)

    def test_quote_empty_sexpr(self):
        env = make_env()
        q = Quote(List()).eval(env)
        self.assertEqual(None, q)

    def test_quote_sexpr(self):
        #env = make_env()
        #
        #q = Quote(List(Symbol('+'), Atom(2), Atom(3))).eval(env)
        #self.assertEqual((Symbol('cons'), (Symbol('+'), (Delay(5), None))),
        #                 q.args)
        pass

    def test_conditional(self):
        # (let (a 5)
        #   (+ a 7))
        #
        env = make_env()
        value = Let(List(Symbol('a'), Atom(5)),
                    List(Symbol('+'), Symbol('a'), Atom(7))).eval(env)
        self.assertEquals(12, value)

    def test_delay(self):
        env = make_env()
        value = Delay(Atom(5)).eval(env)
        self.assertIsInstance(value, Closure)
        self.assertEqual(5, value.call(env, Caller('n/a')))

    def test_function_defn(self):
        # Equivalent to:
        #   (define factorial
        #     (lambda (x)
        #       (if (zero? x)
        #         1
        #         (* x (factorial (- x 1))))))
        #
        env = make_env()

        def body(name):
            return If(List(Symbol('zero?'), Symbol('x')),
                        Atom(1),
                        List(Symbol('*'),
                            Symbol('x'),
                            List(Symbol(name),
                                    List(Symbol('-'),
                                        Symbol('x'),
                                        Atom(1)))))

        # Two variants - define/lambda vs. syntactic sugar version
        Define(Symbol('factorial1'), Lambda(List(Symbol('x')), body('factorial1'))).eval(env)
        Define(List(Symbol('factorial2'), Symbol('x')), body('factorial2')).eval(env)

        # (factorial 10)
        value1 = List(Symbol('factorial1'), Atom(10)).eval(env)
        self.assertEquals(3628800, value1)

        value2 = List(Symbol('factorial2'), Atom(10)).eval(env)
        self.assertEquals(3628800, value2)

    def test_define_too_many_args(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Define(Symbol('err'), Atom('atom1'), Atom(3)).eval(env)

    def test_define_too_few_args(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Define().eval(env)

    def test_define_no_args(self):
        env = make_env()
        Define(Symbol('unbound')).eval(env)
        self.assertEqual(Unbound(), Symbol('unbound').eval(env))

    def test_unbound_equality(self):
        env = make_env()
        u1 = Unbound()
        u2 = Unbound()
        self.assertEqual(u1, u2)
        self.assertEqual(u1.eval(env), u2)
        self.assertEqual(u1, u2.eval(env))
        self.assertEqual(u1.eval(env), u2.eval(env))
        self.assertNotEqual(u1, None)
        self.assertNotEqual(u1, Atom(3))

    def test_set_PLING_unbound(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Set_PLING(Symbol('froobe'), Atom(91)).eval(env)

    def test_set_PLING_bound(self):
        # (let (froobe 43)
        #   (set! froobe 91)
        #   (+ froobe 11))
        env = make_env()
        value = Let(List(Symbol('froobe'), Atom(43)),
                    Set_PLING(Symbol('froobe'), Atom(91)),
                    List(Symbol('+'), Symbol('froobe'), Atom(11))).eval(env)
        self.assertEquals(102, value)

    def test_special_form_eval(self):
        env = make_env()
        sf = SpecialForm('quote')
        self.assertEquals(sf, sf.eval(env))

    def test_special_form_call(self):
        env = make_env()
        symbol = Symbol('test')
        caller = Caller("unused", symbol)
        sf = SpecialForm('quote')
        value = sf.call(env, caller)
        self.assertEquals(value, symbol)


# Should be in globals
#    def test_gensym(self):
#        # (gensym)
#        g = List(Symbol('gensym')).eval(env)
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
