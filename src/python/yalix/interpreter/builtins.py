#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError
from yalix.converter import array_to_linked_list, linked_list_to_array
from yalix.interpreter.primitives import BuiltIn, Closure


class Symbol(BuiltIn):
    """
    A symbolic reference, resolved in the environment firstly against lexical
    closures in local symbol stack, then against a global symbol table.
    """

    def __init__(self, name):
        # TODO: validate symbol name is a string and meets a-zA-Z etc
        self.name = name

    def eval(self, env):
        return env[self.name]

class Quote(BuiltIn):
    """
    Makes no effort to call the supplied expression when evaluated
    """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return array_to_linked_list(self.expr)


class Atom_QUESTION(BuiltIn):
    """ Checks if the supplied value is an atom """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        if value is None:
            return False
        else:
            return not isinstance(value, tuple)


class Nil(BuiltIn):
    """ Nil representation """

    def __init__(self):
        pass

    def eval(self, env):
        return None


class Nil_QUESTION(BuiltIn):
    """ Checks if the supplied value is nil """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return self.expr.eval(env) is None


class Cons(BuiltIn):
    """ Constructs memory objects """

    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def eval(self, env):
        return self.expr1.eval(env), self.expr2.eval(env)


class List(BuiltIn):
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


class Car(BuiltIn):
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


class Cdr(BuiltIn):
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


class Let(BuiltIn):
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


class Let_STAR(BuiltIn):
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



class Lambda(BuiltIn):
    """ A recursive n-argument anonymous function """

    def __init__(self, formals, body):
        self.formals = [] if formals is None else formals
        self.body = body

    def eval(self, env):
        return Closure(env, self)


class Cond(BuiltIn):
    """ Conditional """

    def __init__(self, *cond_clauses):
        self.cond_clauses = cond_clauses

    def eval(self, env):
        for test_expr, then_body in self.cond_clauses:
            if test_expr.eval(env):
                return then_body.eval(env)

        return None


class Define(BuiltIn):
    """ Updates entries in the Global Symbol Table """

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def eval(self, env):
        env[self.name] = self.body
        return None



BuiltIn.classes = {
    'symbol': Symbol,
    'quote': Quote,
    'atom?': Atom_QUESTION,
    'nil': Nil,
    'nil?': Nil_QUESTION,
    'cons': Cons,
    'car': Car,
    'cdr': Cdr,
    'list': List,
    'cond': Cond,
    'let': Let,
    'let*': Let_STAR,
    'define': Define
}

