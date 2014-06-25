#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yalix.utils as utils
from yalix.exceptions import EvaluationError
from yalix.interpreter.primitives import Atom, Closure, ForwardRef, Primitive

__special_forms__ = ['symbol', 'quote', 'list', 'lambda', 'define', 'if',
                     'let', 'let*', 'letrec']


class BuiltIn(Primitive):
    pass


class Symbol(BuiltIn):
    """
    A symbolic reference, resolved in the environment firstly against lexical
    closures in local symbol stack, then against a global symbol table.
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)

    def eval(self, env):
        try:
            return env[self.name]
        except ValueError as ex:
            raise EvaluationError(self, str(ex))


class Quote(BuiltIn):
    """ Makes no effort to call the supplied expression when evaluated """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return self.expr


class List(BuiltIn):
    """ A convenient Cons wrapper """

    def __init__(self, *args):
        self.args = args

    def eval(self, env):
        return utils.array_to_linked_list([value.eval(env) for value in self.args])


class Body(BuiltIn):
    """
    Evaluates a sequence of expressions, presumably for side effects, returning
    the result of the last evaluated expression.
    """

    def __init__(self, *body):
        self.body = body

    def eval(self, env):
        result = None
        for expr in self.body:
            result = expr.eval(env)
        return result


class Let(BuiltIn):
    """ A local binding """

    def __init__(self, binding_form, expr, *body):
        self.binding_form = binding_form
        self.expr = expr
        self.body = Body(*body)

    def eval(self, env):
        value = self.expr.eval(env)
        extended_env = env.extend(self.binding_form, value)
        return self.body.eval(extended_env)


class Let_STAR(BuiltIn):
    """ Multiple local bindings """

    def __init__(self, bindings, *body):
        self.bindings = bindings
        self.body = Body(*body)

    def eval(self, env):
        extended_env = env
        for name, expr in utils.chunks(self.bindings, 2):
            value = expr.eval(extended_env)
            extended_env = extended_env.extend(name, value)

        return self.body.eval(extended_env)


class LetRec(BuiltIn):
    """ Multiple recursive local bindings, which must not be shadowed """

    def __init__(self, bindings, *body):
        self.bindings = bindings
        self.body = Body(*body)

    def eval(self, env):
        extended_env = env

        # All names are created first and filled with forward
        # references and bound to the environment
        forward_refs = {}
        for name in self.bindings:

            if name in forward_refs:
                # bindings are NOT shadowed in letrec
                raise EvaluationError(self, "'{0}' is not distinct in letrec", name)

            ref = ForwardRef()
            forward_refs[name] = ref
            extended_env = extended_env.extend(name, ref)

        # Then the binding expressions are evaluated and set in the fwd-refs
        for name, expr in utils.chunks(self.bindings, 2):
            forward_refs[name].reference = expr.eval(extended_env)

        return self.body.eval(extended_env)


class Lambda(BuiltIn):
    """ A recursive n-argument anonymous function """

    def __init__(self, formals, *body):
        self.formals = [] if formals is None else formals
        self.body = Body(*body)

    def has_sufficient_arity(self, args):
        if Primitive.VARIADIC_MARKER in self.formals:
            # Must be at least n args (where n is the variadic marker position)
            return len(args) >= self.formals.index(Primitive.VARIADIC_MARKER)
        else:
            # no. args must match exactly
            return len(args) == len(self.formals)

    def eval(self, env):
        if len(self.formals) != len(set(self.formals)):
            raise EvaluationError(self, 'formals are not distinct: {0}', self.formals)

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

    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def eval(self, env):
        env[self.name] = self.expr.eval(env)
        return Symbol(self.name)


class DefineFunction(BuiltIn):
    """ Syntactic sugar for define/lambda """

    def __init__(self, name, formals, *body):
        self.name = name
        self.lambda_ = Lambda(formals, *body)

    def eval(self, env):
        env[self.name] = self.lambda_.eval(env)
        return Symbol(self.name)


class Set_PLING(BuiltIn):
    """ Updates a local binding """

    def __init__(self, binding_form, expr):
        self.binding_form = binding_form
        self.expr = expr

    def eval(self, env):
        try:
            value = self.expr.eval(env)
            env.set_local(self.binding_form, value)
            return None
        except ValueError as ex:
            raise EvaluationError(self, str(ex))
