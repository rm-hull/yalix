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
    Define(List(Symbol('first'), Symbol('a')), InterOp(lambda a: a[0], Symbol('a'))).eval(env)
    Define(List(Symbol('rest'), Symbol('a')), InterOp(lambda a: a[1], Symbol('a'))).eval(env)
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

    def test_letrec_distinct_bindings(self):
        env = make_env()
        with self.assertRaises(EvaluationError) as cm:
            LetRec(List(List(Symbol('a'), Atom(5)),
                        List(Symbol('b'), Atom(7)),
                        List(Symbol('a'), Atom(8))),
                   List(Symbol('+'), Symbol('a'), Symbol('b'))).eval(env)
        self.assertEqual('\'a\' is not distinct in letrec', cm.exception.message)

    def test_lambda(self):
        env = make_env()
        value = Let(List(Symbol('identity'), Lambda(List(Symbol('x')), Symbol('x'))),  # <-- anonymous fn
                  List(Symbol('identity'), Atom(99))).eval(env)
        self.assertEqual(99, value)

    def test_lambda_duplicated_formals(self):
        env = make_env()
        with self.assertRaises(EvaluationError) as cm:
            Lambda(List(Symbol('x'), Symbol('y'), Symbol('x'), Symbol('z')), Symbol('x')).eval(env)
        self.assertEqual('Formals are not distinct: (x y x z)', cm.exception.message)

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
        with self.assertRaises(EvaluationError) as cm:
            Define(List(Symbol('list*'), Symbol('.'), Symbol('xs'), Symbol('ys')), Symbol('xs')).eval(env)
        self.assertEqual('Only one variadic argument is allowed: (. xs ys)', cm.exception.message)

    def test_lambda_invalid_variadic_spec(self):
        env = make_env()
        with self.assertRaises(EvaluationError) as cm:
            Define(List(Symbol('list*'), Symbol('.'), Symbol('xs'), Symbol('.')), Symbol('xs')).eval(env)
        self.assertEqual('Invalid variadic argument spec: (. xs .)', cm.exception.message)

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

        with self.assertRaises(EvaluationError) as cm:
            List(Symbol('barf'), Atom(3)).eval(env)
        self.assertEqual('Cannot invoke with: \'barf\'', cm.exception.message)

    def test_call_wrong_arity(self):
        env = make_env()

        # Porridge is too cold
        with self.assertRaises(EvaluationError) as cm:
            List(Symbol('+'), Atom(3)).eval(env)
        self.assertEqual('Call to \'+\' applied with insufficient arity: 2 args expected, 1 supplied', cm.exception.message)

        # Porridge is too hot
        with self.assertRaises(EvaluationError) as cm:
            List(Symbol('+'), Atom(3), Atom(4), Atom(5)).eval(env)
        self.assertEqual('Call to \'+\' applied with insufficient arity: 2 args expected, 3 supplied', cm.exception.message)

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
        with self.assertRaises(EvaluationError) as cm:
            Define(Symbol('err'), Atom('atom1'), Atom(3)).eval(env)
        self.assertEqual('Too many arguments supplied to define', cm.exception.message)

    def test_define_too_few_args(self):
        env = make_env()
        with self.assertRaises(EvaluationError) as cm:
            Define().eval(env)
        self.assertEqual('Too few arguments supplied to define', cm.exception.message)

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

    def test_unbound_hash(self):
        u1 = Unbound()
        u2 = Unbound()
        self.assertEqual(hash(u1), hash(u2))
        self.assertEquals(1, len(set([u1, u2])))

    def test_set_PLING_unbound(self):
        env = make_env()
        with self.assertRaises(EvaluationError) as cm:
            Set_PLING(Symbol('froobe'), Atom(91)).eval(env)
        self.assertEqual('Assignment disallowed: \'froobe\' is unbound in local environment', cm.exception.message)

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

    def test_realize_simple_list(self):
        env = make_env()
        atoms = [Atom(value) for value in range(10)]
        linked_list = make_linked_list(*atoms).eval(env)
        arr = Realize(linked_list).eval(env)
        self.assertEqual(range(10), arr)

    def test_realize_single_item(self):
        env = make_env()
        atom = Atom(17)
        value = Realize(atom.eval(env)).eval(env)
        self.assertEqual(17, value)

    def test_realize_nil(self):
        env = make_env()
        value = Realize(None).eval(env)
        self.assertEqual(None, value)

    def test_realize_list_of_list(self):
        env = make_env()
        lol = [make_linked_list(*[Atom(value) for value in range(i)])
               for i in range(1, 10)]

        linked_list = make_linked_list(*lol).eval(env)
        arr = Realize(linked_list).eval(env)
        expected = [range(i) for i in range(1, 10)]
        self.assertEqual(expected, arr)

    def test_repr_exhaust_list__no_print_length(self):
        env = make_env()
        self.assertFalse('*print-length*' in env)
        atoms = [Atom(value) for value in range(10)]
        linked_list = make_linked_list(*atoms).eval(env)
        text = Repr(linked_list).eval(env)
        self.assertEqual('(0 1 2 3 4 5 6 7 8 9)', text)

    def test_repr_curtail_list(self):
        env = make_env()
        env['*print-length*'] = 12
        atoms = [Atom(value) for value in range(100)]
        linked_list = make_linked_list(*atoms).eval(env)
        text = Repr(linked_list).eval(env)
        self.assertEqual('(0 1 2 3 4 5 6 7 8 9 10 11 ...)', text)

    def test_repr_curtail_list_same_size_as_list(self):
        env = make_env()
        env['*print-length*'] = 12
        atoms = [Atom(value) for value in range(12)]
        linked_list = make_linked_list(*atoms).eval(env)
        text = Repr(linked_list).eval(env)
        self.assertEqual('(0 1 2 3 4 5 6 7 8 9 10 11)', text)

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
