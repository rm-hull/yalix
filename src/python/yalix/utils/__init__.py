#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from yalix.utils.color import red, green, bold, faint


def chunks(l, n):
    """ Yield successive n-sized chunks from l. """
    for i in range(0, len(l), n):
        yield l[i:i+n]


def linked_list_to_array(t):
    arr = []
    if isinstance(t, tuple):
        while t:
            arr.append(t[0])
            t = t[1]
    return arr


class log_progress(object):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        sys.stdout.write(faint(self.message + ' ... '))
        sys.stdout.flush()

    def __exit__(self, *exc_info):
        if exc_info:
            sys.stdout.write(bold(green('DONE')))
        else:
            sys.stdout.write(bold(red('FAILED')))
        sys.stdout.write('\n')


def log(message='', *args):
    sys.stdout.write(message.format(*args) + '\n')


def debug(message='', *args):
    log(faint('DEBUG: ' + message), *args)


