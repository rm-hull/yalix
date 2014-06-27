#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to
evaluate the AST under the environment
"""

import yalix.utils as utils
from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError


__special_forms__ = ['symbol', 'quote', 'lambda', 'define', 'if',
                     'let', 'let*', 'letrec', 'set!', 'delay']


class Primitive(object):
    __metaclass__ = ABCMeta
    VARIADIC_MARKER = '.'

#    def __repr__(self):
#        return str(self.eval(Env()))

    @abstractmethod
    def eval(self, env):
        raise NotImplementedError()

    def quoted_form(self):
        return self


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

    def __init__(self, *args):
        self.args = args

    def make_lazy_list(self, arr):
        t = Atom(None)
        while arr:
            t = Call(Symbol('cons'), arr[-1], Delay(t))
            arr = arr[:-1]
        return t

    def quoted_form(self):
        """ Override default implementation to present as a list """
        return self.make_lazy_list(self.args)

    def eval(self, env):
        if self.args:
            funexp = self.args[0]
            params = self.args[1:]
            closure = funexp.eval(env)
            if isinstance(closure, ForwardRef):
                closure = closure.reference

            if not isinstance(closure, Closure):
                raise EvaluationError(self, 'Call applied with non-closure: \'{0}\'', closure)

            if not closure.func.has_sufficient_arity(params):
                raise EvaluationError(self,
                                    'Call to \'{0}\' applied with insufficient arity: {1} args expected, {2} supplied',
                                    funexp.name,  # FIXME: probably ought rely on __repr__ of symbol here....
                                    len(closure.func.formals),
                                    len(params))

            variadic = False
            extended_env = closure.env
            for i, bind_variable in enumerate(closure.func.formals):
                if bind_variable == Primitive.VARIADIC_MARKER:  # variadic arg indicator
                    # Use the next formal as the /actual/ bind variable,
                    # evaluate the remaining arguments into a list (NOTE offset from i)
                    # and dont process any more arguments
                    bind_variable = closure.func.formals[i + 1]
                    value = self.make_lazy_list(params[i:]).eval(env)
                    extended_env = extended_env.extend(bind_variable, value)
                    variadic = True
                    break
                else:
                    value = params[i].eval(env)
                    extended_env = extended_env.extend(bind_variable, value)

            if not variadic and len(closure.func.formals) != len(params):
                raise EvaluationError(self,
                                    'Call to \'{0}\' applied with excessive arity: {1} args expected, {2} supplied',
                                    funexp.name,  # FIXME: probably ought rely on __repr__ of symbol here....
                                    len(closure.func.formals),
                                    len(params))

            if extended_env['*debug*']:
                utils.debug('{0} {1}', funexp.name, extended_env.local_stack)

            return closure.func.body.eval(extended_env)


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
        return self.expr.quoted_form()


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
        try:
            # Must be at least n args (where n is the variadic marker position)
            return len(args) >= list(self.formals).index(Primitive.VARIADIC_MARKER)
        except ValueError:
            # no. args must match exactly
            return len(args) == len(self.formals)

    def eval(self, env):
        if len(self.formals) != len(set(self.formals)):
            raise EvaluationError(self, 'formals are not distinct: {0}', self.formals)

        return Closure(env, self)


class Delay(BuiltIn):

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return Lambda([], self.expr).eval(env)


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

    def __init__(self, name, doc_string, expr):
        self.name = name
        self.expr = expr
        self.doc_string = doc_string

    def params(self):
        if isinstance(self.expr, Lambda) and self.expr.formals:
            return ' ' + str(self.expr.formals).replace('\'', '').replace(',', '')
        return ''

    def set_docstring(self, obj):
        if self.doc_string:
            tidied = ['-----------------', self.name + self.params()] + \
                     ['  ' + x.replace(';^', '  ').strip() for x in self.doc_string]
            setattr(obj, '__docstring__', '\n'.join(tidied))

    def eval(self, env):
        obj = self.expr.eval(env)
        self.set_docstring(obj)
        env.global_frame[self.name] = obj
        return Symbol(self.name)


class DefineFunction(BuiltIn):
    """ Syntactic sugar for define/lambda """

    def __init__(self, name, formals, doc_string, *body):
        self.name = name
        self.formals = formals
        self.doc_string = doc_string
        self.body = body

    def eval(self, env):
        return Define(self.name, self.doc_string,
                      Lambda(self.formals, *self.body)).eval(env)


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
