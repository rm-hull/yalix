#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from yalix.utils.color import red, green, bold, faint


class log_progress(object):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        sys.stdout.write(faint(self.message + ' ... '))

    def __exit__(self, *exc_info):
        if exc_info:
            sys.stdout.write(bold(green('DONE')))
        else:
            sys.stdout.write(bold(red('FAILED')))
        sys.stdout.write('\n')

def log(message='', *args):
    sys.stdout.write(message.format(*args) + '\n')

class GeneratorContextManager(object):

    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        try:
            return self.gen.next()
        except StopIteration:
            raise RuntimeError("generator didn't yield")

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                self.gen.next()
            except StopIteration:
                return
            else:
                raise RuntimeError("generator didn't stop")
        else:
            try:
                self.gen.throw(type, value, traceback)
                raise RuntimeError("generator didn't stop after throw()")
            except StopIteration:
                return True
            except:
                # only re-raise if it's *not* the exception that was
                # passed to throw(), because __exit__() must not raise
                # an exception unless __exit__() itself failed.  But
                # throw() has to raise the exception to signal
                # propagation, so this fixes the impedance mismatch
                # between the throw() protocol and the __exit__()
                # protocol.
                #
                if sys.exc_info()[1] is not value:
                    raise


def contextmanager(func):
    def helper(*args, **kwds):
        return GeneratorContextManager(func(*args, **kwds))
    return helper
