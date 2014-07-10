#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an AST (abstract syntax tree) and an environment in order to
evaluate the AST under the environment
"""

import yalix.utils as utils
from abc import ABCMeta, abstractmethod
from yalix.environment import Env
from yalix.exceptions import EvaluationError


class Primitive(object):
    __metaclass__ = ABCMeta
    VARIADIC_MARKER = '.'

#    def __repr__(self):
#        return str(self.eval(Env()))

    @abstractmethod
    def eval(self, env):
        raise NotImplementedError()

    def call(self, env, caller):
        raise EvaluationError(self, 'Cannot invoke with: \'{0}\'', self)

    def quoted_form(self, env):
        return self.eval(env)


class InterOp(Primitive):
    """ Helper class for wrapping Python functions """
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def eval(self, env):
        values = [a.eval(env) for a in self.args]
        try:
            return self.func(*values)
        except TypeError as ex:
            raise EvaluationError(self, str(ex))


class SpecialForm(Primitive):
    """ A proxy for other built-in types """

    def __init__(self, name):
        self.impl = __special_forms__[name]

    def eval(self, env):
        return self

    def call(self, env, caller):
        """ Don't evaluate params for special forms """
        return self.impl(*caller.params).eval(env)


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

    def extend_env(self, env, params):
        """
        Extend the closure's environment by binding the
        params to the functions formals
        """
        extended_env = self.env
        for i, bind_variable in enumerate(self.func.formals):
            if bind_variable == Primitive.VARIADIC_MARKER:  # variadic arg indicator
                # Use the next formal as the /actual/ bind variable,
                # evaluate the remaining arguments into a list (NOTE offset from i)
                # and dont process any more arguments
                bind_variable = self.func.formals[i + 1]
                value = List.make_lazy_list(params[i:]).eval(env)
                extended_env = extended_env.extend(bind_variable, value)
                break
            else:
                value = params[i].eval(env)
                extended_env = extended_env.extend(bind_variable, value)
        return extended_env

    def call(self, env, caller):
        if not self.func.has_sufficient_arity(caller.params):
            raise EvaluationError(self,
                                  'Call to \'{0}\' applied with insufficient arity: {1} args expected, {2} supplied',
                                  caller.funexp.name,  # FIXME: probably ought rely on __repr__ of symbol here....
                                  self.func.arity(),
                                  len(caller.params))

        if not self.func.is_variadic() and len(self.func.formals) != len(caller.params):
            raise EvaluationError(self,
                                  'Call to \'{0}\' applied with excessive arity: {1} args expected, {2} supplied',
                                  caller.funexp.name,  # FIXME: probably ought rely on __repr__ of symbol here....
                                  self.func.arity(),
                                  len(caller.params))

        extended_env = self.extend_env(env, caller.params)
        return self.func.body.eval(extended_env)


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

    def call(self, env, caller):
        """ Don't evaluate params for special forms """
        return self.reference.call(env, caller)


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

    @classmethod
    def make_lazy_list(cls, arr):
        t = Atom(None)
        while arr:
            t = List(Symbol('cons'), arr[-1], Delay(t))
            arr = arr[:-1]
        return t

    def splice_args(self, args, env):
        for arg in args:
            if isinstance(arg, UnquoteSplice):
                for elem in self.splice_args(arg.eval(env), env):
                    yield elem
            else:
                yield arg

    def quoted_form(self, env):
        """ Override default implementation to present as a list """
        quote = SyntaxQuote if SyntaxQuote.ID in env else Quote
        return List.make_lazy_list([quote(a) for a in self.splice_args(self.args, env)]).eval(env)

    def eval(self, env):
        if self.args:
            value = self.funexp.eval(env)
            if env['*debug*']:
                utils.debug('{0} {1}', self.funexp.name, self.params)
            try:
                return value.call(env, self)
            except AttributeError:
                raise EvaluationError(self, 'Cannot invoke with: \'{0}\'', value)


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

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __ne__(self, other):
        return not self == other

    def eval(self, env):
        try:
            return env[self.name]
        except ValueError as ex:
            raise EvaluationError(self, str(ex))

    def quoted_form(self, env):
        if self.name.endswith('#') and SyntaxQuote.ID in env:
            unique_id = env[SyntaxQuote.ID]
            name = "{0}__{1}__auto__".format(self.name[:-1], unique_id)
            return Symbol(name)
        else:
            return self


class Quote(BuiltIn):
    """ Makes no effort to call the supplied expression when evaluated """

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return self.expr.quoted_form(env)

    def quoted_form(self, env):
        return self.expr


class SyntaxQuote(Quote):

    ID = 'G__syntax_quote_id'

    def eval(self, env):
        if SyntaxQuote.ID not in env:
            env = env.extend(SyntaxQuote.ID, Env.next_id())
        return self.expr.quoted_form(env)


class Unquote(BuiltIn):

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        if isinstance(value, List):
            value = value.eval(env)
        return value


class UnquoteSplice(BuiltIn):

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        list_ = self.expr.eval(env)
        return Realize(list_).eval(env)


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
        if self.is_variadic():
            if sum(1 for f in self.formals if f == Primitive.VARIADIC_MARKER) > 1:
                raise EvaluationError(self, 'invalid variadic argument spec: {0}', self.formals)

            if self.formals.index(Primitive.VARIADIC_MARKER) != len(self.formals)-2:
                raise EvaluationError(self, 'only one variadic argument is allowed: {0}', self.formals)

        if len(self.formals) != len(set(self.formals)):
            raise EvaluationError(self, 'formals are not distinct: {0}', self.formals)

        return Closure(env, self)


class Promise(Closure):

    def __init__(self, closure):
        self.closure = closure
        self.realized = False
        self.result = None

    def eval(self, env):
        return self

    def call(self, env, caller):
        if not self.realized:
            self.result = self.closure.call(env, caller)
            self.realized = True

        return self.result

class Delay(BuiltIn):
    """
    Creates a promise that when forced, evaluates the body to produce its
    value. The result is then cached so that further uses of force produces
    the cached value immediately.
    """

    def __init__(self, *body):
        self.body = body

    def eval(self, env):
        return Promise(Lambda(List(), *self.body).eval(env))


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


class Unbound(BuiltIn):
    def eval(self, env):
        return self

    def __eq__(self, other):
        return isinstance(other, Unbound)

    def __ne__(self, other):
        return not self == other


class Define(BuiltIn):
    """ Updates entries in the Global Symbol Table """

    def __init__(self, *args):
        if len(args) == 0:
            raise EvaluationError(self, "Too few arguments supplied to define")
        self.args = args

    def name(self):
        first = self.args[0]
        if isinstance(first, List):
            return first.args[0]
        else:
            return first

    def docstring(self):
        return [text for text in self.args[1:] if isinstance(text, str) and text.startswith(';^')]

    def body(self):
        return [expr for expr in self.args[1:] if isinstance(expr, Primitive)]

    def set_docstring_on(self, obj):
        params = ''
        if isinstance(obj, Closure) and obj.func.formals:
            params = ' ' + str(obj.func.formals).replace(',', '').replace('\'', '')

        if self.docstring():
            tidied = [repr(self.name()) + params] + \
                     ['  ' + x.replace(';^', '  ').strip() for x in self.docstring()]
            setattr(obj, '__docstring__', '\n'.join(tidied))

    def set_source_on(self, obj):
        if isinstance(obj, Closure):
            for attr in ['__source__', '__location__']:
                setattr(obj, attr, getattr(self.name(), attr, None))

    def eval(self, env):
        symbol = self.name()
        first = self.args[0]
        if isinstance(first, List):
            formals = first.args[1:]
            obj = Lambda(List(*formals), *self.body()).eval(env)
        else:
            body = self.body()
            body_size = len(body)
            if body_size > 1:
                raise EvaluationError(self, "Too many arguments supplied to define")
            elif body_size == 0:
                obj = Unbound()
            else:
                obj = body[0].eval(env)

        self.set_docstring_on(obj)
        self.set_source_on(obj)

        env[repr(symbol)] = obj
        return symbol


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

    def isatom(self, value):
        return value is None or type(value) in [str, int, long, float, bool, Symbol]

    def eval(self, env):
        if self.isatom(self.atom_or_list):
            return str(self.atom_or_list)
        elif type(self.atom_or_list) == tuple:
            current_head = self.atom_or_list
            max_iterations = env['*print-length*']
            ret = '('
            while current_head is not None and (max_iterations is None or max_iterations > 0):
                value = List(Symbol('first'), Atom(current_head)).eval(env)
                ret += Repr(value).eval(env)
                current_head = List(Symbol('rest'), Atom(current_head)).eval(env)
                if max_iterations is not None:
                    max_iterations -= 1
                if current_head is not None:
                    ret += ' '

            if current_head is not None and max_iterations == 0:
                ret += '...'

            ret += ')'
            return ret
        else:
            return str(self.atom_or_list.eval(env))


class Eval(BuiltIn):

    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return self.expr.quoted_form(env).eval(env)


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
    'delay': Delay,
    'eval': Eval
}
