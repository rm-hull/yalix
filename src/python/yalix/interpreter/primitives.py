#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to evaluate the AST
"""

from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError
from yalix.converter import linked_list_to_array, array_to_linked_list


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


class ForwardRef(Primitive):
    """
    A forward reference is a placeholder that can be set at a later point
    when the value is available. Evaluating before the reference is set will
    yield None. Evaluating after the reference is set will yield the
    referenced value.
    """

    def __init__(self):
        self.reference = None

    def eval(self, env):
        return self.reference


class Call(Primitive):
    """ A function call (call-by-value) """

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
        if isinstance(closure, ForwardRef):
            closure = closure.reference

        if not isinstance(closure, Closure):
            raise EvaluationError('Call applied with non-closure: \'{0}\'', closure)

        extended_env = closure.env
        for i, bind_variable in enumerate(closure.func.formals):
            if bind_variable == '.':  # variadic arg indicator
                # Use the next formal as the /actual/ bind variable,
                # evaluate the remaining arguments into a list (NOTE offset from i)
                # and dont process any more arguments
                bind_variable = closure.func.formals[i + 1]
                value = array_to_linked_list([arg.eval(env) for arg in self.args[i:]])
                extended_env = extended_env.extend(bind_variable, value)
                return closure.func.body.eval(extended_env)
            else:
                value = self.args[i].eval(env)
                extended_env = extended_env.extend(bind_variable, value)

        if len(closure.func.formals) != len(self.args):
            raise EvaluationError('Call to \'{0}\' applied with incorrect arity: {1} args expected, {2} supplied',
                                  self.funexp.name, # FIXME: probably ought rely on __repr__ of symbol here....
                                  len(closure.func.formals),
                                  len(self.args))
        return closure.func.body.eval(extended_env)
