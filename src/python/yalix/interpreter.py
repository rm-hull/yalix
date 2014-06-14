#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to evaluate the AST
"""

from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError
from yalix.environment import Env


class Primitive:
    __metaclass__ = ABCMeta

    def __repr__(self):
        return str(self.eval(Env()))

    @abstractmethod
    def eval(self, env):
        raise NotImplementedError()


class Var(Primitive):
    """ A variable reference """

    def __init__(self, name):
        # TODO: validate name is a string and meets a-zA-Z etc
        self.name = name

    def eval(self, env):
        return env[self.name]


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


class Not(Primitive):
    """ Negate """
    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return not self.expr.eval(env)


class Eq(Primitive):
    """ Equality check """

    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def eval(self, env):
        value1 = self.expr1.eval(env)
        value2 = self.expr2.eval(env)
        return value1 == value2


class Closure(Primitive):
    """ A closure is not in 'source' programs; it is what functions evaluate to """

    def __init__(self, env, func):
        self.env = env
        self.func = func

    def eval(self, env):
        return self


class Function(Primitive):
    """ A recursive 1-argument function """

    def __init__(self, nameopt, formal, body):
        self.nameopt = nameopt
        self.formal = formal
        self.body = body

    def eval(self, env):
        return Closure(env, self)


class Call(Primitive):
    """ A function call """

    def __init__(self, funexp, actual):
        self.funexp = funexp
        self.actual = actual

    def eval(self, env=()):
        closure = self.funexp.eval(env)
        if isinstance(closure, Closure):
            arg = self.actual.eval(env)
            fn_name = closure.func.nameopt
            bind_variable = closure.func.formal
            extended_env = closure.env.extend(bind_variable, arg)
            if fn_name:
                extended_env = extended_env.extend(fn_name, closure)

            return closure.func.body.eval(extended_env)
        else:
            raise EvaluationError('Call applied with non-closure: \'{0}\'', closure)

# TODO - implement:
#  class Call_STAR(Primitive):
#  class Interop(Primitive):
#  class Define(Primitive):

env = Env().extend('y', Atom(7))
Var("y").eval(env)

lst1 = Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil())))
lst2 = List(Atom(4), Atom(2), Atom(3))
Eq(Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil()))), lst1)
Eq(lst2, lst1)

Eq(Atom(True),
   Not(Atom(False)))

Nil_QUESTION(Nil())
Nil_QUESTION(Atom('Freddy'))

Atom_QUESTION(Atom('Freddy'))
Atom_QUESTION(Nil())

Eq(Nil(),Atom(None))

Car(Cdr(lst1))

(Cdr(Nil()))

Let("f",
    Atom("Hello"),
    Cons(Var("f"),
         Var("f")))

Let_STAR([('a', Atom('Hello')),
          ('b', List(Atom(1),Atom(2),Atom(3))),
          ('c', Atom('World')),
          ('c', List(Atom('Big'),Var('c')))],  # <-- re-def shadowing
         List(Var('a'), Var('c'), Var('b')))

Let('identity',
    Function(None, 'x', Var('x')), # <-- anonymous fn
    Call(Var('identity'), Atom(99)))

