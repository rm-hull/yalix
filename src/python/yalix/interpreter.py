#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to
evaluate the AST under the environment
"""

import yalix.utils as utils
from abc import ABCMeta, abstractmethod
from yalix.exceptions import EvaluationError


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
        values = [a.eval(env) for a in self.args]
        return self.func(*values)


class SpecialForm(Primitive):
    """ A proxy for other built-in types """

    def __init__(self, name):
        self.impl = __special_forms__[name]

    def eval(self, env):
        return self


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



# http://code.activestate.com/recipes/474088/
class List(Primitive):
    """ A list """

    def __init__(self, *args):
        self.args = args
        if args:
            self.funexp = self.args[0]
            self.params = self.args[1:]

    def __len__(self):
        return len(self.args)

    def __iter__(self):
        return self.args.__iter__()

    def __getitem__(self, index):
        return self.args.__getitem__(index)

    def make_lazy_list(self, arr):
        t = Atom(None)
        while arr:
            t = List(Symbol('cons'), arr[-1], Delay(t))
            arr = arr[:-1]
        return t

    def quoted_form(self):
        """ Override default implementation to present as a list """
        return self.make_lazy_list(self.args)

    def extend_env(self, env, params, closure):
        """
        Extend the closure's environment by binding the
        params to the functions formals
        """
        extended_env = closure.env
        for i, bind_variable in enumerate(closure.func.formals):
            if bind_variable == Primitive.VARIADIC_MARKER:  # variadic arg indicator
                # Use the next formal as the /actual/ bind variable,
                # evaluate the remaining arguments into a list (NOTE offset from i)
                # and dont process any more arguments
                bind_variable = closure.func.formals[i + 1]
                value = self.make_lazy_list(params[i:]).eval(env)
                extended_env = extended_env.extend(bind_variable, value)
                break
            else:
                value = params[i].eval(env)
                extended_env = extended_env.extend(bind_variable, value)
        return extended_env

    def dispatch(self, env, value):
        tbl = {
            ForwardRef: self.handle_forward_ref,
            Closure: self.handle_closure,
            SpecialForm: self.handle_special_form
        }

        fn = tbl.get(type(value), self.default_handler)
        return fn(env, value)

    def handle_forward_ref(self, env, forward_ref):
        return self.dispatch(env, forward_ref.reference)

    def handle_closure(self, env, closure):
        if not closure.func.has_sufficient_arity(self.params):
            raise EvaluationError(self,
                                  'Call to \'{0}\' applied with insufficient arity: {1} args expected, {2} supplied',
                                  self.funexp.name,  # FIXME: probably ought rely on __repr__ of symbol here....
                                  closure.func.arity(),
                                  len(self.params))

        if not closure.func.is_variadic() and len(closure.func.formals) != len(self.params):
            raise EvaluationError(self,
                                  'Call to \'{0}\' applied with excessive arity: {1} args expected, {2} supplied',
                                  self.funexp.name,  # FIXME: probably ought rely on __repr__ of symbol here....
                                  closure.func.arity(),
                                  len(self.params))

        extended_env = self.extend_env(env, self.params, closure)
        if extended_env['*debug*']:
            utils.debug('{0} {1}', self.funexp.name, extended_env.local_stack)

        return closure.func.body.eval(extended_env)

    def handle_special_form(self, env, special_form):
        """ Don't evaluate params for special forms """
        if env['*debug*']:
            utils.debug('{0} {1}', self.funexp.name, self.params)

        return special_form.impl(*self.params).eval(env)

    def default_handler(self, env, value):
        raise EvaluationError(self, 'Cannot invoke with: \'{0}\'', value)

    def eval(self, env):
        if self.args:
            value = self.funexp.eval(env)
            return self.dispatch(env, value)


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

    def __init__(self, binding, *body):
        self.binding_form = binding.args[0]
        self.expr = binding.args[1]
        self.body = Body(*body)

    def eval(self, env):
        value = self.expr.eval(env)
        extended_env = env.extend(self.binding_form.name, value)
        return self.body.eval(extended_env)


class Let_STAR(BuiltIn):
    """ Multiple local bindings """

    def __init__(self, bindings, *body):
        self.bindings = bindings
        self.body = Body(*body)

    def eval(self, env):
        extended_env = env
        for symbol, expr in self.bindings:
            value = expr.eval(extended_env)
            extended_env = extended_env.extend(symbol.name, value)

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
        for symbol, _ in self.bindings:

            if symbol.name in forward_refs:
                # bindings are NOT shadowed in letrec
                raise EvaluationError(self, "'{0}' is not distinct in letrec", symbol.name)

            ref = ForwardRef()
            forward_refs[symbol.name] = ref
            extended_env = extended_env.extend(symbol.name, ref)

        # Then the binding expressions are evaluated and set in the fwd-refs
        for symbol, expr in self.bindings:
            forward_refs[symbol.name].reference = expr.eval(extended_env)

        return self.body.eval(extended_env)


class Lambda(BuiltIn):
    """ A recursive n-argument anonymous function """

    def __init__(self, formals, *body):
        self.formals = [f.name for f in formals]
        self.body = Body(*body)

    def arity(self):
        if self.is_variadic():
            return self.formals.index(Primitive.VARIADIC_MARKER)
        else:
            return len(self.formals)

    def is_variadic(self):
        return Primitive.VARIADIC_MARKER in self.formals

    def has_sufficient_arity(self, args):
        try:
            # Must be at least n args (where n is the variadic marker position)
            return len(args) >= self.formals.index(Primitive.VARIADIC_MARKER)
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
        return Lambda(List(), self.expr).eval(env)


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

    def __init__(self, *args):
        if len(args) == 0:
            raise EvaluationError(self, "Too few arguments supplied to define")

        self.args = args

    def name(self):
        first = self.args[0]
        if isinstance(first, List):
            return first.args[0].name
        else:
            return first.name

    def docstring(self):
        return [text for text in self.args[1:] if isinstance(text, str) and text.startswith(';^')]

    def body(self):
        return [expr for expr in self.args[1:] if isinstance(expr, Primitive)]

    def set_docstring_on(self, obj):
        params = ''
        if isinstance(obj, Lambda) and obj.formals:
            params = ' ' + str(self.expr.formals).replace(',', '')

        if self.docstring():
            tidied = ['-----------------', self.name() + params] + \
                     ['  ' + x.replace(';^', '  ').strip() for x in self.docstring()]
            setattr(obj, '__docstring__', '\n'.join(tidied))

    def eval(self, env):
        first = self.args[0]
        if isinstance(first, List):
            formals = first.args[1:]
            obj = Lambda(List(*formals), *self.body()).eval(env)
        else:
            body = self.body()
            if len(body) > 1:
                raise EvaluationError(self, "Too many arguments supplied to define")

            obj = body[0].eval(env)

        self.set_docstring_on(obj)

        name = self.name()
        env[name] = obj
        return Symbol(name)


class Set_PLING(BuiltIn):
    """ Updates a local binding """

    def __init__(self, binding_form, expr):
        self.binding_form = binding_form
        self.expr = expr

    def eval(self, env):
        try:
            value = self.expr.eval(env)
            env.set_local(self.binding_form.name, value)
            return None
        except ValueError as ex:
            raise EvaluationError(self, str(ex))


class Realize(Primitive):
    """
    Lazy list unpacker - eagerly takes *ALL* the content from a nested lazy list
    and returns as a nested array of arrays. Should not be used with infinite
    streams.
    """
    def __init__(self, atom_or_list):
        self.atom_or_list = atom_or_list

    def eval(self, env):
        if List(Symbol('atom?'), self.atom_or_list).eval(env):
            return self.atom_or_list.eval(env)
        else:
            arr = []
            current_head = self.atom_or_list
            while current_head is not None:
                value = List(Symbol('first'), current_head)
                arr.append(Realize(value).eval(env))
                current_head = List(Symbol('rest'), current_head).eval(env)
            return arr


class Repr(Primitive):
    """
    A string representation of atoms/lists, implemented with iteration so as
    not to blow Python's stack. Note nested lists are (presently) handled
    with recursion - this may change to an explicit stack.

    List traversal will not extend beyond the *print-length* (if not nil).
    """

    def __init__(self, atom_or_list):
        self.atom_or_list = atom_or_list

    def eval(self, env):
        if List(Symbol('atom?'), self.atom_or_list).eval(env):
            return str(self.atom_or_list.eval(env))
        else:
            current_head = self.atom_or_list
            max_iterations = env['*print-length*']
            ret = '('
            while current_head is not None and (max_iterations is None or max_iterations > 0):
                value = List(Symbol('first'), current_head)
                ret += Repr(value).eval(env)
                current_head = List(Symbol('rest'), current_head).eval(env)
                if max_iterations is not None:
                    max_iterations -= 1
                if current_head is not None:
                    ret += ' '

            if current_head is not None and max_iterations == 0:
                ret += '...'

            ret += ')'
            return ret


__special_forms__ = {
    'symbol': Symbol,
    'quote': Quote,
    'lambda': Lambda,
    'λ': Lambda,
    'define': Define,
    'begin': Body,
    'if': If,
    'let': Let,
    'let*': Let_STAR,
    'letrec': LetRec,
    'set!': Set_PLING,
    'delay': Delay
}
