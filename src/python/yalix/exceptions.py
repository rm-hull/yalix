#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class YalixError(StandardError):
     """ Base Yalix Exception class """

     __metaclass__ = ABCMeta

     def __init__(self, message, *args):
        self.value = message.format(*args)

     def __str__(self):
        return repr(self.value)

class EvaluationError(YalixError):
    """ Evaluation specific error handling """


class EnvironmentError(YalixError):
    """ Enironment specific error handling """

class ParseError(YalixError):
    """ Parse specific error handling """

    def __init__(self, root_cause):
        self.root_cause = root_cause

    def __str__(self):
        return str(self.root_cause)
