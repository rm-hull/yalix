#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yalix.utils as utils
from yalix.converter import array_to_linked_list
from yalix.interpreter.primitives import Atom, Closure, Primitive

__special_forms__ = ['symbol',
                     'quote',
                     'list',
                     'lambda',
                     'define',
                     'if',
                     'let',
                     'let*']


class BuiltIn(Primitive):
    pass


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
        return self.expr


class List(BuiltIn):
    """ A convenient Cons wrapper """

    def __init__(self, *args):
        self.args = args

    def eval(self, env):
        return array_to_linked_list([value.eval(env) for value in self.args])


class Let(BuiltIn):
    """ A local binding """

    def __init__(self, binding_form, expr, body):
        self.binding_form = binding_form
        self.expr = expr
        self.body = body

    def eval(self, env):
        value = self.expr.eval(env)
        extended_env = env.extend(self.binding_form, value)
        return self.body.eval(extended_env)


class Let_STAR(BuiltIn):
    """ Multiple local bindings """

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, env):
        extended_env = env
        for name, expr in utils.chunks(self.bindings, 2):
            value = expr.eval(extended_env)
            extended_env = extended_env.extend(name, value)
        return self.body.eval(extended_env)


class LetRec(BuiltIn):
    """ Multiple recursive local bindings, which must not be shadowed """

    def __init__(self, bindings, body):
        self.bindings = bindings
        self.body = body

    def eval(self, env):
        raise NotImplementedError()
        extended_env = env
        # TODO shadow check
        for name, expr in utils.chunks(self.bindings, 2):
            value = expr.eval(extended_env)
            extended_env = extended_env.extend(name, value)
        return self.body.eval(extended_env)


class Lambda(BuiltIn):
    """ A recursive n-argument anonymous function """

    def __init__(self, formals, body):
        self.formals = [] if formals is None else formals
        self.body = body

    def eval(self, env):
        return Closure(env, self)


class If(BuiltIn):
    """ If """

    def __init__(self, test_expr, then_expr, else_expr=Atom(None)):
        self.test_expr = test_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def eval(self, env):
        if self.test_expr.eval(env):
            return self.then_expr.eval(env)
        else:
            return self.else_expr.eval(env)


class Define(BuiltIn):
    """ Updates entries in the Global Symbol Table """

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def eval(self, env):
        env[self.name] = self.body
        return self.body


class DefineFunction(BuiltIn):
    """ Syntactic sugar for define/lambda """

    def __init__(self, name, formals, body):
        self.name = name
        self.lambda_ = Lambda(formals, body)

    def eval(self, env):
        env[self.name] = self.lambda_
        return self.lambda_
