#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit
import os
import sys
from datetime import datetime

from pyparsing import ParseException
from yalix.source_view import source_view
from yalix.exceptions import EvaluationError
from yalix.completer import Completer
from yalix.interpreter import Repr
from yalix.parser import scheme_parser
from yalix.utils import log_progress, log, balance
from yalix.utils import red, green, blue, bold, highlight_syntax
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
likely be: Python, Lua, Go/Rust, Java/Scala, Haskell/Idris, Forth, and course
there really needs to be a Yalix implementation too!

The REPL that you are now connected to has readline capabilities, and stores
a history in ~/.yalix-history. Pressing <TAB> on a partially typed word will
interrogate the environment for matching definitions and will present a word
completion facility.

Documentation for a particular function (e.g. first) can be found by evaluating
the following S-Exp at the prompt:

    (doc map)

The source code for a previously defined function will be shown when the
following is entered at the prompt (Note: special forms will not show any
source):

    (source map)

See https://github.com/rm-hull/yalix/ for further information."""


def credits():
    return """
TBD"""


def init_readline(env):
    try:
        import readline
    except ImportError:
        print("Module readline not available")
    else:
        histfile = os.path.join(os.path.expanduser("~"), ".yalix_history")
        readline.set_completer(Completer(env).complete)
        readline.set_completer_delims('() ')
        readline.parse_and_bind("set blink-matching-paren on")
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                with log_progress("Reading history"):
                    readline.read_history_file(histfile)

            except IOError:
                pass
            atexit.register(readline.write_history_file, histfile)


def input2or3(prompt):
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


def input_with_prefill(prompt, text):
    try:
        import readline

        def hook():
            readline.insert_text(text)
            readline.redisplay()
        readline.set_pre_input_hook(hook)
        return input2or3(prompt)
    except ImportError:
        return input2or3(prompt)
    finally:
        readline.set_pre_input_hook()


def stdin_read(count):
    primary_prompt = '\001' + green('\002In [\001') + green('\002{0}\001', style='bold') + green('\002]: \001') + '\002'
    secondary_prompt = ' ' * len(str(count)) + '\001' + green('\002  ...: \001') + '\002'
    prompt = primary_prompt.format(count)

    prefill = ''
    entry = ''

    while True:
        entry += input_with_prefill(prompt, prefill) + '\n'
        prompt = secondary_prompt
        parens_count = balance(entry)
        if parens_count > 0:
            prefill = '  ' * parens_count
        else:
            yield entry


def stdout_prn(result, count):
    primary_prompt = red('Out[') + red('{0}', style='bold') + red(']: ')
    secondary_prompt = ' ' * len(str(count)) + red('  ...: ')
    prompt = primary_prompt.format(count)
    for line in str(result).split('\n'):
        print(prompt + line)
        prompt = secondary_prompt


def ready():
    log()
    log(bold('Yalix [{0}]') + ' on Python {1} {2}', version(), sys.version, sys.platform)
    log('Type "help", "copyright", "credits" or "license" for more information.')


def left_margin(text):
    """ Make sure text is flushed to the right margin """
    return text.replace('\n', '\n\r        \r')


def repl(inprompt=stdin_read, outprompt=stdout_prn):

    try:
        env = create_initial_env()
    except EvaluationError as ex:
        log("{0}: {1}", red(type(ex).__name__, style='bold'), ex)
        log(highlight_syntax(source_view(ex.primitive)))
        sys.exit()

    env['copyright'] = left_margin(copyright())
    env['license'] = left_margin(license())
    env['help'] = left_margin(help())
    env['credits'] = left_margin(credits())

    init_readline(env)
    ready()

    parser = scheme_parser()
    count = 1
    while True:
        try:
            text = next(inprompt(count))
            for ast in parser.parseString(text, parseAll=True).asList():
                result = ast.eval(env)
                # Evaluate lazy list representations
                result = Repr(result).eval(env)
                outprompt(result, count)

            if text.strip() != '':
                print()

        except EOFError:
            log(blue('\nBye!', style='bold'))
            break

        except KeyboardInterrupt:
            log(red('\nKeyboardInterrupt', style='bold'))

        except EvaluationError as ex:
            log("{0}: {1}", red(type(ex).__name__, style='bold'), ex)
            log(highlight_syntax(source_view(ex.primitive)))

        except ParseException as ex:
            log("{0}: {1}", red(type(ex).__name__, style='bold'), ex)

        count += 1


if __name__ == '__main__':
    repl()
    sys.exit()
