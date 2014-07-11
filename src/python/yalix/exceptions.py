#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yalix.source_view as source_view


class EvaluationError(Exception):
    """ Evaluation specific error handling """

    def __init__(self, primitive, message, *args):
        self.message = message.format(*args)
        self.primitive = primitive

    def __str__(self):
        msg = self.message
        line, col = source_view.line_col(self.primitive)
        if line and col:
            msg += " at line:{0}, col:{1}".format(line, col)
        return msg
