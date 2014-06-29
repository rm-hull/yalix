#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import os
import sys
from datetime import datetime

from pyparsing import ParseException
from yalix.exceptions import EvaluationError
from yalix.completer import Completer
from yalix.interpreter import List, Symbol
from yalix.parser import scheme_parser
from yalix.utils import log_progress, log
from yalix.utils.color import red, green, blue, bold
from yalix.globals import create_initial_env


def version():
    return '0.0.1'


def copyright():
    return """
Copyright (c) {0} Richard Hull.
All Rights Reserved.""".format(datetime.now().year)


def license():
    return """
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
THE SOFTWARE.""".format(datetime.now().year)


def help():
    return """
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

See https://github.com/rm-hull/yalex/ for further information."""


def credits():
    return """
TBD"""


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


def read(count):
    primary_prompt = '\001' + green('\002In [\001') + green('\002{0}\001', style='bold') + green('\002]: \001') + '\002'
    secondary_prompt = ' ' * len(str(count)) + '\001' + green('\002  ...: \001') + '\002'

    prompt = primary_prompt.format(count)
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


def prn(input, result, count):
    primary_prompt = red('Out[') + red('{0}', style='bold') + red(']: ')
    secondary_prompt = ' ' * len(str(count)) + red('  ...: ')
    prompt = primary_prompt.format(count)
    for line in str(result).split('\n'):
        print prompt + line
        prompt = secondary_prompt


def ready():
    log()
    log(bold('Yalix [{0}]') + ' on Python {1} {2}', version(), sys.version, sys.platform)
    log('Type "help", "copyright", "credits" or "license" for more information.')


def source_view(exception):
    if exception.location and exception.source:
        src = exception.source()
        loc = exception.location()

        # pygments magic here
        # to closing bracket
        return src[loc:]


def repl(print_callback=prn):
    env = create_initial_env()
    env['copyright'] = copyright()
    env['license'] = license()
    env['help'] = help()
    env['credits'] = credits()

    init_readline(env)
    ready()


    parser = scheme_parser()
    count = 1
    while True:
        try:
            text = read(count)
            for ast in parser.parseString(text, parseAll=True).asList():

                # Evaluate lazy list representations
                #result = List(Symbol('repr'), ast).eval(env)
                result = ast.eval(env)

                print_callback(text, result, count)
            if text.strip() != '':
                print

        except EOFError:
            log(bold(blue('\nBye!')))
            break

        except KeyboardInterrupt:
            log(bold(red('\nKeyboardInterrupt')))

        except EvaluationError as ex:
            log("{0}: {1}", bold(red(type(ex).__name__)), ex)

            # TODO: Format error logging better
            log(source_view(ex))

        except ParseException as ex:
            log("{0}: {1}", bold(red(type(ex).__name__)), ex)

        count += 1


if __name__ == '__main__':
    repl()
    sys.exit()
