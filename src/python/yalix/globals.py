#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Some predefined functions injected into an environment
"""
import operator
import random
import math
import threading

from yalix.utils import log_progress
from yalix.parser import scheme_parser
from yalix.environment import Env
from yalix.exceptions import EvaluationError
from yalix.interpreter import Primitive, Atom, InterOp, Lambda, List, \
        Realize, Symbol, SpecialForm, __special_forms__

__core_libraries__ =  ['core', 'hof', 'num', 'macros', 'repr', 'test']

gensym_nextID = 0
gensym_lock = threading.Lock()


def create_initial_env():
    env = Env()
    with log_progress("Creating initial environment"):
        bootstrap_special_forms(env)
        bootstrap_python_functions(env)

    for lib in __core_libraries__:
        with log_progress("Loading library: " + lib):
            bootstrap_lisp_functions(env, "lib/{0}.ylx".format(lib))

    return env


def gensym(prefix='G__'):
    global gensym_nextID
    global gensym_lock
    with gensym_lock:
        old = gensym_nextID
        gensym_nextID += 1
    return Symbol(prefix + str(old))


def interop(fun, arity, variadic=False):
    """ Helper to create a lisp function from a python function """
    bind_variables = [gensym() for _ in range(arity)]

    if variadic:
        # Insert the variadic marker at the last-but one position
        formals = list(bind_variables)
        formals.insert(-1, Symbol(Primitive.VARIADIC_MARKER))
        bind_variables[-1] = Realize(bind_variables[-1])
    else:
        formals = bind_variables

    return Lambda(List(*formals), InterOp(fun, *bind_variables))


def doc(value):
    doc = getattr(value, '__docstring__', None)
    if doc:
        print '-----------------'
        print doc


def source(value):
    from yalix.utils.color import highlight_syntax
    from yalix.source_view import source_view
    src = source_view(value)
    if src:
        print '-----------------'
        print highlight_syntax(source_view(value))


def print_(value):
    print str_(value)


def str_(args=None):
    def strnil(x):
        return '' if x is None else str(x)
    if args is None:
        return ''
    return reduce(lambda x, y: strnil(x) + strnil(y), args)


def format_(format_spec, args=None):
    if args is None:
        args = []
    return format_spec.format(*args)


def error(msg):
    raise EvaluationError(None, msg)


def atom_QUESTION(value):
    """ Checks if the supplied value is an atom """
    return value is None or type(value) in [str, int, long, float, bool, Symbol]


def read_string(value):
    return scheme_parser().parseString(value, parseAll=True).asList()[0]


def bootstrap_lisp_functions(env, from_file):
    for ast in scheme_parser().parseFile(from_file, parseAll=True).asList():
        # TODO: brand AST nodes with filename
        ast.eval(env)


class EvalWrapper(object):

    def __init__(self, env):
        self.env = env

    def __getitem__(self, name):
        return self.env[name]

    def __setitem__(self, name, primitive):
        self.env[name] = primitive.eval(self.env)


def bootstrap_special_forms(env):
    env = EvalWrapper(env)
    for name in __special_forms__.keys():
        env[name] = SpecialForm(name)


def bootstrap_python_functions(env):
    env = EvalWrapper(env)

    env['*debug*'] = Atom(False)
    env['nil'] = Atom(None)
    env['nil?'] = interop(lambda x: x is None, 1)
    env['gensym'] = interop(gensym, 0)
    env['symbol'] = interop(lambda x: Symbol(x), 1)
    env['symbol?'] = interop(lambda x: isinstance(x, Symbol), 1)
    env['interop'] = interop(interop, 2)
    env['doc'] = interop(doc, 1)
    env['source'] = interop(source, 1)
    env['print'] = interop(print_, 1, variadic=True)
    env['format'] = interop(format_, 2, variadic=True)
    env['atom?'] = interop(atom_QUESTION, 1)
    env['str'] = interop(str_, 1, variadic=True)
    env['read-string'] = interop(read_string, 1)  # Read just one symbol
    env['error'] = interop(error, 1)

    # Basic Arithmetic Functions
    env['add'] = interop(operator.add, 2)
    env['sub'] = interop(operator.sub, 2)
    env['mul'] = interop(operator.mul, 2)
    env['div'] = interop(operator.div, 2)
    env['negate'] = interop(operator.neg, 1)

    # String / Sequence Functions
    env['contains?'] = interop(operator.contains, 2)

    # Bitwise Ops
    env['bitwise-and'] = interop(operator.and_, 2)
    env['bitwise-xor'] = interop(operator.xor, 2)
    env['bitwise-invert'] = interop(operator.invert, 2)
    env['bitwise-or'] = interop(operator.or_, 2)
    env['bitwise-and'] = interop(operator.and_, 2)
    env['bitwise-left-shift'] = interop(operator.lshift, 2)
    env['bitwise-right-shift'] = interop(operator.rshift, 2)

    env['not'] = interop(operator.not_, 1)

    # Comparison & Ordering
    env['not='] = interop(operator.ne, 2)
    env['<'] = interop(operator.lt, 2)
    env['<='] = interop(operator.le, 2)
    env['='] = interop(operator.eq, 2)
    env['>='] = interop(operator.ge, 2)
    env['>'] = interop(operator.gt, 2)

    env['random'] = interop(random.random, 0)

    # Number theoretic Functions
    env['ceil'] = interop(math.ceil, 1)
    env['floor'] = interop(math.floor, 1)
    env['mod'] = interop(operator.mod, 2)
    env['trunc'] = interop(math.trunc, 1)

    # Power & Logarithmic Functions
    env['exp'] = interop(math.exp, 1)
    env['log'] = interop(math.log, 2)
    env['log10'] = interop(math.log10, 1)
    env['pow'] = interop(math.pow, 2)
    env['sqrt'] = interop(math.sqrt, 1)

    # Trigonomeric Functions
    env['acos'] = interop(math.acos, 1)
    env['asin'] = interop(math.asin, 1)
    env['atan'] = interop(math.atan, 1)
    env['atan2'] = interop(math.atan2, 1)
    env['cos'] = interop(math.cos, 1)
    env['hypot'] = interop(math.hypot, 2)
    env['sin'] = interop(math.sin, 1)
    env['tan'] = interop(math.tan, 1)

    # Angular Conversion
    env['degrees'] = interop(math.degrees, 1)
    env['radians'] = interop(math.radians, 1)

    # Hyperbolic Functions
    env['acosh'] = interop(math.acosh, 1)
    env['asinh'] = interop(math.asinh, 1)
    env['atanh'] = interop(math.atanh, 1)
    env['cosh'] = interop(math.cosh, 1)
    env['sinh'] = interop(math.sinh, 1)
    env['tanh'] = interop(math.tanh, 1)

    # Constants
    env['math/pi'] = Atom(math.pi)
    env['math/e'] = Atom(math.e)
