#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yalix.exceptions import EvaluationError
from yalix.converter import array_to_linked_list
from yalix.interpreter.primitives import Closure, Primitive

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

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l. """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def eval(self, env):
        extended_env = env
        for name, expr in self.chunks(self.bindings, 2):
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

    def __init__(self, test_expr, then_expr, else_expr=Nil()):
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
