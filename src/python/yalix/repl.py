#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import os
import sys
from datetime import datetime

from pyparsing import ParseException
from yalix.exceptions import YalixError
from yalix.completer import Completer
from yalix.interpreter.primitives import *
from yalix.interpreter.builtins import *
from yalix.parser import parse
from yalix.utils import log_progress, log
from yalix.utils.color import red, green, blue, bold
from yalix.globals import create_initial_env


def version():
    return '0.0.1'


def copyright():
    return Atom("""
Copyright (c) {0} Richard Hull.
All Rights Reserved.""".format(datetime.now().year))


def license():
    return Atom("""
The MIT License (MIT)

Copyright (c) {0} Richard Hull

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.""".format(datetime.now().year))


def help():
    return Atom("""
Yalix is a LISP interpreter: it's dialect most closely resembles that of Racket
or PLT-Scheme. This particular implementation is written in Python, and serves
as a reference implementation only. It is subject to on-going development, and
as such will suffer breaking changes, as well as being buggy and not having
been optimised. It is therefore not recommended for production use.

The main purpose of this software is to provide a pedagogical experience in
writing a LISP interpreter and a core library of functions, in a number of
different computer languages. The intention is that there will eventually be
"Seven LISPs in seven languages", where each implementation is idiomatic in
the target language. Although not fully decided, the languages will most
likely be: Python, Lua, Julia, Java/Scala, Haskell, a.n.other, and course
there really needs to be a Yalix implementation too!

The REPL that you are now connected to has readline capabilities, and stores
a history in ~/.yalix-history. Pressing <TAB> on a partially typed word will
interrogate the environment for matching definitions and will present a word
completion facility.

Documentation for a particular function (e.g. first) can be found by evaluating
the following S-Exp at the prompt:

    (doc first)

See https://github.com/rm-hull/yalex/ for further information.""")


def credits():
    return Atom("""
TBD""")


def init_readline(env):
    try:
        import readline
    except ImportError:
        print "Module readline not available"
    else:
        histfile = os.path.join(os.path.expanduser("~"), ".yalix_history")
        readline.set_completer(Completer(env).complete)
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                with log_progress("Reading history"):
                    readline.read_history_file(histfile)

            except IOError:
                pass
            atexit.register(readline.write_history_file, histfile)


def input_with_prefill(prompt, text):
    try:
        import readline

        def hook():
            readline.insert_text(text)
            readline.redisplay()
        readline.set_pre_input_hook(hook)
        return raw_input(prompt)
    except ImportError:
        return raw_input(prompt)
    finally:
        readline.set_pre_input_hook()


def balance(text, bal=0):
    """
    Checks whether the parens in the text are balanced:
        - zero: balanced
        - negative: too many right parens
        - positive: too many left parens
    """
    if text == '':
        return bal
    elif text[0] == '(' and bal >= 0:
        return balance(text[1:], bal + 1)
    elif text[0] == ')':
        return balance(text[1:], bal - 1)
    else:
        return balance(text[1:], bal)


def read(count, primary_prompt):
    prompt = primary_prompt.format(count)
    secondary_prompt = ' ' * len(str(count)) + green('  ...: ')

    prefill = ''
    entry = ''

    while True:
        entry += input_with_prefill(prompt, prefill) + '\n'
        prompt = secondary_prompt
        parens_count = balance(entry)
        if parens_count == 0:
            return entry
        elif parens_count > 0:
            prefill = '  ' * parens_count


def prn(input, result, count, prompt):
    print prompt.format(count, result)


def ready():
    log()
    log(bold('Yalix [{0}]') + ' on Python {1} {2}', version(), sys.version, sys.platform)
    log('Type "help", "copyright", "credits" or "license" for more information.')


def repl(print_callback=prn):
    env = create_initial_env()
    env['copyright'] = copyright()
    env['license'] = license()
    env['help'] = help()
    env['credits'] = credits()

    init_readline(env)
    ready()

    in_prompt = green('In [') + green(bold('{0}')) + green(']: ')
    out_prompt = red('Out[') + red(bold('{0}')) + red(']: ') + '{1}\n'

    count = 1
    while True:
        try:
            text = read(count, in_prompt)
            for ast in parse(text):
                result = ast.eval(env)
                print_callback(text, result, count, out_prompt)

        except EOFError:
            log(bold(blue('\nBye!')))
            break

        except KeyboardInterrupt:
            log(bold(red('\nKeyboardInterrupt')))

        except (YalixError, ParseException) as ex:
            log("{0}: {1}", bold(red(type(ex).__name__)), ex)
        count += 1

if __name__ == '__main__':
    repl()
    exit()

env = create_initial_env()

lst1 = Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil())))
lst2 = List(Atom(4), Atom(2), Atom(3))

# Eq(Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil()))), lst1).eval(env)
# Eq(lst2, lst1).eval(env)
#
# Eq(Atom(True),
#   Not(Atom(False))).eval(env)

Nil_QUESTION(Nil()).eval(env)
Nil_QUESTION(Atom('Freddy')).eval(env)

Atom_QUESTION(Atom('Freddy')).eval(env)
Atom_QUESTION(Nil()).eval(env)

# Eq(Nil(), Atom(None)).eval(env)

# Car(Cdr(lst1)).eval(env)

(Cdr(Nil())).eval(env)

Let("f",
    Atom("Hello"),
    Cons(Symbol("f"),
         Symbol("f"))).eval(env)

Let_STAR(['a', Atom('Hello'),
          'b', List(Atom(1), Atom(2), Atom(3)),
          'c', Atom('World'),
          'c', List(Atom('Big'), Symbol('c'))],  # <-- re-def shadowing
         List(Symbol('a'), Symbol('c'), Symbol('b'))).eval(env)

Let('identity',
    Lambda(['x'], Symbol('x')),  # <-- anonymous fn
    Call(Symbol('identity'), Atom(99))).eval(env)

# InterOp, i.e. using Python functions
import operator
InterOp(operator.add, Atom(41), Atom(23)).eval(env)

# check unicode, pi & golden ratio
Define('π', Atom(3.14159265358979323846264338327950288419716939937510)).eval(env)
Define('ϕ', Atom(1.618033988749894848204586834)).eval(env)
env['π']
env['ϕ']

Symbol('π').eval(env)
Symbol('ϕ').eval(env)


# from __future__ import print_function
# Define('print', Lambda(['text'], InterOp(print_function, Symbol('text')))).eval(env)

Call(Symbol('+'), Atom(99), Atom(55)).eval(env)
Call([Symbol('+'), Atom(99), Atom(55)]).eval(env)
Call(array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])).eval(env)
array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])


env['+']

Call(Symbol('random')).eval(env)

q = Quote([Symbol('+'), Atom(2), Atom(3)]).eval(env)
q
Call(q).eval(env)

# Call(Quote([Symbol('+'), Atom(2), Atom(3)])).eval(env)

# (let (rnd (random))
#   (if (< rnd 0.5)
#     "Unlucky"
#     (if (< rnd 0.75)
#       "Close, but no cigar"
#       "Lucky")))
#
Let('rnd',
    Call(Symbol('random')),
    If(Call(Symbol('<'), Symbol('rnd'), Atom(0.5)),
       Atom("Unlucky"),
       If(Call(Symbol('<'), Symbol('rnd'), Atom(0.75)),
          Atom("Close, but no cigar"),
          Atom("Lucky")))).eval(env)


# (define factorial
#   (lambda (x)
#     (if (zero? x)
#       1
#       (* x (factorial (- x 1))))))
#
Define('zero?', Lambda(['n'], Call(Symbol('='), Symbol('n'), Atom(0)))).eval(env)
Define('factorial', Lambda(['x'],
                           If(Call(Symbol('zero?'), Symbol('x')),
                              Atom(1),
                              Call(Symbol('*'),
                                   Symbol('x'),
                                   Call(Symbol('factorial'),
                                        Call(Symbol('-'),
                                             Symbol('x'),
                                             Atom(1))))))).eval(env)

# (factorial 10)
Call(Symbol('factorial'), Atom(10)).eval(env)

# (format "{0} PI = {1}" (list 2 (* 2 math/pi)))
Call(Symbol('format'),
     Atom('{0} PI = {1}'),
     List(Atom(2),
          Call(Symbol('*'),
               Atom(2),
               Symbol('math/pi')))).eval(env)

# (gensym)
g = Call(Symbol('gensym')).eval(env)
g
g.name

# =============================================================================================


test2 = """
(define *hello* ["world" -1 #t 3.14159 [1 2 3]])

(let (rnd (random))
  (if (< rnd 0.5)
    "Unlucky"
    (if (< rnd 0.75)
      "Close, but no cigar"
      "Lucky")))

(define factorial
  (lambda (x)
    (if (zero? x)
      1
      (* x (factorial (- x 1))))))

(factorial 10)

*hello*

"""

# No yet fully supported
# (let* ((x 5)
#        (y (+ x 7))
#        (z (+ y x 2)))
#    (* x y z))

for ptree in parse(test2):
    print ptree.eval(env)
