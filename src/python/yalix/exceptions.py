#!/usr/bin/env python
# -*- coding: utf-8 -*-


class EvaluationError(Exception):
    """ Evaluation specific error handling """

    def __init__(self, primitive, message, *args):
        self.message = message.format(*args)
        self.primitive = primitive

    def __str__(self):
        return self.message

    def source(self):
        return getattr(self.primitive, '__source__', None)

    def location(self):
        return getattr(self.primitive, '__location__', None)

