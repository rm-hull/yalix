#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import operator

from yalix.environment import Env
from yalix.interpreter import *


def define_cons():
    return DefineFunction('cons', ['a', 'b'], [],
                          InterOp(lambda a, b: (a, b),
                                  Symbol('a'),
                                  Symbol('b')))

def make_env():
    env = Env()
    env['*debug*'] = Atom(False)
    return env

def make_linked_list(*arr):
    t = Atom(None)
    while arr:
        t = Call(Symbol('cons'), arr[-1], t)
        arr = arr[:-1]
    return t

class BuiltinsTest(unittest.TestCase):

    def test_let_binding(self):
        env = make_env()
        define_cons().eval(env)

        lst = Let("f",
                  Atom("Hello"),
                  make_linked_list(Symbol("f"), Symbol("f"))).eval(env)
        self.assertEqual(('Hello', ('Hello', None)), lst)

    def test_let_STAR_shadow_binding(self):
        env = make_env()
        define_cons().eval(env)

        lst = Let_STAR(['a', Atom('Hello'),
                        'b', make_linked_list(Atom(1), Atom(2), Atom(3)),
                        'c', Atom('World'),
                        'c', make_linked_list(Atom('Big'), Symbol('c'))],  # <-- re-def shadowing
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
        Define('+', [], Lambda(['x', 'y'],
                           InterOp(operator.add,
                                   Symbol('x'),
                                   Symbol('y')))).eval(env)

        Define('<', [], Lambda(['x', 'y'],
                           InterOp(operator.lt,
                                   Symbol('x'),
                                   Symbol('y')))).eval(env)

        DefineFunction('sum', ['n'], [],
                       LetRec(('accum',
                               Lambda(['x'],
                                      If(Call(Symbol('<'), Symbol('x'), Symbol('n')),
                                         Call(Symbol('+'),
                                              Symbol('x'),
                                              Call(Symbol('accum'),
                                                   Call(Symbol('+'),
                                                        Symbol('x'),
                                                        Atom(1)))),
                                         Atom(0)))),
                              Call(Symbol('accum'),
                                   Atom(0)))).eval(env)

        # (sum 45)
        value = Call(Symbol('sum'), Atom(45)).eval(env)
        self.assertEqual(990, value)

    def test_lambda(self):
        env = make_env()
        value = Let('identity', Lambda(['x'], Symbol('x')),  # <-- anonymous fn
                  Call(Symbol('identity'), Atom(99))).eval(env)
        self.assertEqual(99, value)

    def test_lambda_duplicated_formals(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Lambda(['x', 'y', 'x', 'z'], Symbol('x')).eval(env)


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
        Define('π', [], Atom(pi)).eval(env)
        Define('ϕ', [], Atom(rho)).eval(env)

        self.assertAlmostEqual(pi, env['π'])
        self.assertAlmostEqual(rho, env['ϕ'])

        self.assertAlmostEqual(pi, Symbol('π').eval(env))
        self.assertAlmostEqual(rho, Symbol('ϕ').eval(env))

    def test_call(self):
        env = make_env()
        Define('+', [], Lambda(['x', 'y'],
                           InterOp(operator.add,
                                   Symbol('x'),
                                   Symbol('y')))).eval(env)

        self.assertEqual(154, Call(Symbol('+'), Atom(99), Atom(55)).eval(env))

    def test_call_non_closure(self):
        env = make_env()
        Define('barf', [], Atom('barf')).eval(env)

        with self.assertRaises(EvaluationError):
            Call(Symbol('barf'), Atom(3)).eval(env)

    def test_call_wrong_arity(self):
        env = make_env()
        Define('+', [], Lambda(['x', 'y'],
                           InterOp(operator.add,
                                   Symbol('x'),
                                   Symbol('y')))).eval(env)

        # Porridge is too cold
        with self.assertRaises(EvaluationError):
            Call(Symbol('+'), Atom(3)).eval(env)

        # Porridge is too hot
        with self.assertRaises(EvaluationError):
            Call(Symbol('+'), Atom(3), Atom(4), Atom(5)).eval(env)

#    def test_call_variadic_fn(self):
#        # Cheating?
#        # (define (list* . xs) xs)
#        env = make_env()
#        define_cons().eval(env)
#        DefineFunction('list*', ['.', 'xs'], [], Symbol('xs')).eval(env)
#
#        lst1 = Call(Symbol('list*')).eval(env)
#        lst2 = Call(Symbol('list*'), Atom(1)).eval(env)
#        lst3 = Call(Symbol('list*'), Atom(1), Atom(4), Atom(17)).eval(env)
#
#        self.assertEqual(None, lst1)
#        self.assertEqual(1, lst2[0])
#        self.assertEqual(None, lst2[1].eval(env))
#
#        self.assertEqual((1, (4, (17, None))), lst3)

    def test_symbol(self):
        env = make_env().extend('fred', 45)
        s = Symbol('fred')
        self.assertEqual(45, s.eval(env))
        self.assertEqual('fred', repr(s))

    def test_quote_atom(self):
        env = make_env()
        q = Quote(Atom(5)).eval(env)
        self.assertEquals(5, q.value)

    def test_quote_symbol(self):
        env = make_env()
        q = Quote(Symbol('toil')).eval(env)
        self.assertEquals('toil', q.name)

    def test_quote_empty_sexpr(self):
        env = make_env()
        q = Quote(Call()).eval(env)
        self.assertEqual(None, q.value)

    def test_quote_sexpr(self):
        #env = make_env()
        #define_cons().eval(env)
        #Define('+', [], Lambda(['x', 'y'],
        #                   InterOp(operator.add,
        #                           Symbol('x'),
        #                           Symbol('y')))).eval(env)#
        #
        #q = Quote(Call(Symbol('+'), Atom(2), Atom(3))).eval(env)
        #self.assertEqual((Symbol('cons'), (Symbol('+'), (Delay(5), None))),
        #                 q.args)
        pass

    def test_conditional(self):
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

    def test_function_defn(self):
        # Equivalent to:
        #   (define factorial
        #     (lambda (x)
        #       (if (zero? x)
        #         1
        #         (* x (factorial (- x 1))))))
        #
        env = make_env()
        Define('*', [], Lambda(['a', 'b'], InterOp(operator.mul, Symbol('a'), Symbol('b')))).eval(env)
        Define('+', [], Lambda(['a', 'b'], InterOp(operator.add, Symbol('a'), Symbol('b')))).eval(env)
        Define('-', [], Lambda(['a', 'b'], InterOp(operator.sub, Symbol('a'), Symbol('b')))).eval(env)
        Define('=', [], Lambda(['a', 'b'], InterOp(operator.eq, Symbol('a'), Symbol('b')))).eval(env)
        Define('zero?', [], Lambda(['n'], Call(Symbol('='), Symbol('n'), Atom(0)))).eval(env)

        def body(name):
            return If(Call(Symbol('zero?'), Symbol('x')),
                        Atom(1),
                        Call(Symbol('*'),
                            Symbol('x'),
                            Call(Symbol(name),
                                    Call(Symbol('-'),
                                        Symbol('x'),
                                        Atom(1)))))

        # Two variants - define/lambda vs. syntactic sugar version
        Define('factorial1', [], Lambda(['x'], body('factorial1'))).eval(env)
        DefineFunction('factorial2', ['x'], [], body('factorial2')).eval(env)

        # (factorial 10)
        value1 = Call(Symbol('factorial1'), Atom(10)).eval(env)
        self.assertEquals(3628800, value1)

        value2 = Call(Symbol('factorial2'), Atom(10)).eval(env)
        self.assertEquals(3628800, value2)

    def test_set_PLING_unbound(self):
        env = make_env()
        with self.assertRaises(EvaluationError):
            Set_PLING('froobe', Atom(91)).eval(env)


    def test_set_PLING_bound(self):
        # (let (froobe 43)
        #   (set! froobe 91)
        #   (+ froobe 11))
        env = make_env()
        Define('+', [], Lambda(['a', 'b'], InterOp(operator.add, Symbol('a'), Symbol('b')))).eval(env)
        value = Let('froobe', Atom(43),
                    Set_PLING('froobe', Atom(91)),
                    Call(Symbol('+'), Symbol('froobe'), Atom(11))).eval(env)
        self.assertEquals(102, value)




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
