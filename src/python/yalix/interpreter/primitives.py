#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to evaluate the AST
"""

from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError
from yalix.converter import linked_list_to_array


class Primitive(object):
    __metaclass__ = ABCMeta

#    def __repr__(self):
#        return str(self.eval(Env()))

    @abstractmethod
    def eval(self, env):
        raise NotImplementedError()


class InterOp(Primitive):
    """ Helper class for wrapping Python functions """
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def eval(self, env):
        values = (a.eval(env) for a in self.args)
        return self.func(*values)


class Atom(Primitive):
    """ An atom """

    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value


class Closure(Primitive):
    """ A closure is not in 'source' programs; it is what functions evaluate to """

    def __init__(self, env, func):
        self.env = env
        self.func = func

    def eval(self, env):
        return self


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