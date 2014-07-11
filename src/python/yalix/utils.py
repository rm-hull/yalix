#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import contextlib


def identity(x, **kwargs):
    return x

red = identity
green = identity
blue = identity
faint = identity
bold = identity

try:
    from colors import red, green, blue, faint, bold
except ImportError:
    pass


def highlight_syntax(code, outfile=None):
    try:
        import pygments
        from pygments.lexers.functional import RacketLexer
        from pygments.formatters import Terminal256Formatter

        if code:
            return pygments.highlight(code,
                                      RacketLexer(),
                                      Terminal256Formatter(style='colorful'),
                                      outfile)
    except ImportError:
        return code


@contextlib.contextmanager
def capture():
    import sys
    try:
        from cStringIO import StringIO
    except ImportError:
        from io import StringIO

    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [StringIO(), StringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


class log_progress(object):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        sys.stdout.write(faint(self.message + ' ... '))
        sys.stdout.flush()

    def __exit__(self, type_, value, traceback):
        if value is None:
            sys.stdout.write(bold(green('DONE')))
        else:
            sys.stdout.write(bold(red('FAILED')))
        sys.stdout.write('\n')


def log(message='', *args):
    if message:
        sys.stdout.write(message.format(*args) + '\n')


def debug(message='', *args):
    log(faint('DEBUG: ' + message), *args)

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

