#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to evaluate the AST
"""

from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError
from yalix.environment import Env
from yalix.converter import array_to_linked_list, linked_list_to_array
import operator

class Primitive(object):
    __metaclass__ = ABCMeta

#    def __repr__(self):
#        return str(self.eval(Env()))

    @abstractmethod
    def eval(self, env):
        raise NotImplementedError()


class Symbol(Primitive):
    """
    A symbolic reference, resolved in the environment firstly against lexical
    closures in local symbol stack, then against a global symbol table.
    """

    def __init__(self, name):
        # TODO: validate symbol name is a string and meets a-zA-Z etc
        self.name = name

    def eval(self, env):
        return env[self.name]

class Quote(Primitive):
    """
    Makes no effort to call the supplied expression when evaluated
    """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return array_to_linked_list(self.expr)


class Atom(Primitive):
    """ An atom """

    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value


class Atom_QUESTION(Primitive):
    """ Checks if the supplied value is an atom """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        if value is None:
            return False
        else:
            return not isinstance(value, tuple)


class Nil(Primitive):
    """ Nil representation """

    def eval(self, env):
        return None


class Nil_QUESTION(Primitive):
    """ Checks if the supplied value is nil """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return self.expr.eval(env) is None


class Cons(Primitive):
    """ Constructs memory objects """

    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def eval(self, env):
        return self.expr1.eval(env), self.expr2.eval(env)


class List(Primitive):
    """ A convenient Cons wrapper """

    def __init__(self, *args):
        self.args = args

    def eval(self, env):
        if not self.args:
            return None
        else:
            car = self.args[0]
            cdr = List(*self.args[1:])
            return Cons(car, cdr).eval(env)


class Car(Primitive):
    """ Contents of the Address part of Register number """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        if value is None:
            return None
        elif isinstance(value, tuple):
            return value[0]
        else:
            raise EvaluationError('{0} is not a cons-cell', value)


class Cdr(Primitive):
    """ Contents of the Decrement part of Register number """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        if value is None:
            return Nil().eval(env)
        elif isinstance(value, tuple):
            return value[1]
        else:
            raise EvaluationError('{0} is not a cons-cell', value)


class Let(Primitive):
    """ A local binding """

    def __init__(self, var, expr, body):
        self.var = var
        self.expr = expr
        self.body = body

    def eval(self, env):
        name = self.var
        value = self.expr.eval(env)
        extended_env = env.extend(name, value)
        return self.body.eval(extended_env)


class Let_STAR(Primitive):
    """ Multiple local bindings """

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, env):
        if self.bindings == []:
            return self.body.eval(env)
        else:
            name = self.bindings[0][0]
            expr = self.bindings[0][1]
            value = expr.eval(env)
            extended_env = env.extend(name, value)
            return Let_STAR(self.bindings[1:], self.body).eval(extended_env)


class Closure(Primitive):
    """ A closure is not in 'source' programs; it is what functions evaluate to """

    def __init__(self, env, func):
        self.env = env
        self.func = func

    def eval(self, env):
        return self


class Lambda(Primitive):
    """ A recursive n-argument anonymous function """

    def __init__(self, formals, body):
        self.formals = [] if formals is None else formals
        self.body = body

    def eval(self, env):
        return Closure(env, self)


class Call(Primitive):
    """ A function call """

    def __init__(self, funexp, *args):
        if isinstance(funexp, tuple):
            arr = linked_list_to_array(funexp)
            self.funexp = arr[0]
            self.args = arr[1:]
        elif isinstance(funexp, list):
            self.funexp = funexp[0]
            self.args = funexp[1:]
        else:
            self.funexp = funexp
            self.args = args

    def eval(self, env):
        closure = self.funexp.eval(env)
        if not isinstance(closure, Closure):
            raise EvaluationError('Call applied with non-closure: \'{0}\'', closure)

        if len(closure.func.formals) != len(self.args):
            raise EvaluationError('Call applied with invalid arity: {0} args expected, {1} supplied',
                                  len(closure.func.formals),
                                  len(self.args))

        extended_env = closure.env
        for bind_variable, arg in zip(closure.func.formals, self.args):
            extended_env = extended_env.extend(bind_variable, arg.eval(env))

        return closure.func.body.eval(extended_env)


class Cond(Primitive):
    """ Conditional """

    def __init__(self, *cond_clauses):
        self.cond_clauses = cond_clauses

    def eval(self, env):
        for test_expr, then_body in self.cond_clauses:
            if test_expr.eval(env):
                return then_body.eval(env)

        return None


class InterOp(Primitive):
    """ Helper class for wrapping Python functions """
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def eval(self, env):
        values = (a.eval(env) for a in self.args)
        return self.func(*values)


class Define(Primitive):
    """ Updates entries in the Global Symbol Table """

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def eval(self, env):
        env[self.name] = self.body
        return None



env = Env()

lst1 = Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil())))
lst2 = List(Atom(4), Atom(2), Atom(3))

#Eq(Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil()))), lst1).eval(env)
#Eq(lst2, lst1).eval(env)
#
#Eq(Atom(True),
#   Not(Atom(False))).eval(env)

Nil_QUESTION(Nil()).eval(env)
Nil_QUESTION(Atom('Freddy')).eval(env)

Atom_QUESTION(Atom('Freddy')).eval(env)
Atom_QUESTION(Nil()).eval(env)

#Eq(Nil(), Atom(None)).eval(env)

Car(Cdr(lst1)).eval(env)

(Cdr(Nil())).eval(env)

Let("f",
    Atom("Hello"),
    Cons(Symbol("f"),
         Symbol("f"))).eval(env)

Let_STAR([('a', Atom('Hello')),
          ('b', List(Atom(1), Atom(2), Atom(3))),
          ('c', Atom('World')),
          ('c', List(Atom('Big'), Symbol('c')))],  # <-- re-def shadowing
         List(Symbol('a'), Symbol('c'), Symbol('b'))).eval(env)

Let('identity',
    Lambda(['x'], Symbol('x')), # <-- anonymous fn
    Call(Symbol('identity'), Atom(99))).eval(env)

# InterOp, i.e. using Python functions
InterOp(operator.add, Atom(41), Atom(23)).eval(env)

# check unicode, pi & golden ratio
Define('π', Atom(3.14159265358979323846264338327950288419716939937510)).eval(env)
Define('ϕ', Atom(1.618033988749894848204586834)).eval(env)
env['π']
env['ϕ']

Symbol('π').eval(env)
Symbol('ϕ').eval(env)

import random
Define('+', Lambda(['x','y'], InterOp(operator.add, Symbol('x'), Symbol('y')))).eval(env)
Define('-', Lambda(['x','y'], InterOp(operator.sub, Symbol('x'), Symbol('y')))).eval(env)
Define('*', Lambda(['x','y'], InterOp(operator.mul, Symbol('x'), Symbol('y')))).eval(env)
Define('random', Lambda((), InterOp(random.random))).eval(env)
Define('==', Lambda(['x','y'], InterOp(operator.eq, Symbol('x'), Symbol('y')))).eval(env)
Define('<', Lambda(['x','y'], InterOp(operator.lt, Symbol('x'), Symbol('y')))).eval(env)

#from __future__ import print_function
#Define('print', Lambda(['text'], InterOp(print_function, Symbol('text')))).eval(env)

Call(Symbol('+'), Atom(99), Atom(55)).eval(env)
Call([Symbol('+'), Atom(99), Atom(55)]).eval(env)
Call(array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])).eval(env)
array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])


env['+']

Call(Symbol('random')).eval(env)

q = Quote([Symbol('+'), Atom(2), Atom(3)]).eval(env)
q

Call(q).eval(env)

#Call(Quote([Symbol('+'), Atom(2), Atom(3)])).eval(env)

# (let (rnd (random))
#   (cond
#     ((< rnd 0.5)  "Unlucky")
#     ((< rnd 0.75) "Close, but no cigar")
#     (#t           "Lucky")))
#
Let('rnd', Call(Symbol('random')),
    Cond(
      (Call(Symbol('<'), Symbol('rnd'), Atom(0.5)), Atom("Unlucky")),
      (Call(Symbol('<'), Symbol('rnd'), Atom(0.75)), Atom("Close, but no cigar")),
      (Atom(True), Atom("Lucky")))).eval(env)


# (define factorial
#   (lambda (x)
#     (cond
#       ((zero? x) 1)
#       (#t        (* x (factorial (- x 1)))))))
#
Define('zero?', Lambda(['n'], Call(Symbol('=='), Symbol('n'), Atom(0)))).eval(env)
Define('factorial', Lambda(['x'],
                           Cond((Call(Symbol('zero?'), Symbol('x')), Atom(1)),
                                (Atom(True), Call(Symbol('*'),
                                                  Symbol('x'),
                                                  Call(Symbol('factorial'),
                                                       Call(Symbol('-'),
                                                            Symbol('x'),
                                                            Atom(1)))))))).eval(env)

# (factorial 10)
Call(Symbol('factorial'), Atom(10)).eval(env)

