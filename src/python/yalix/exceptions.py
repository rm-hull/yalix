#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class YalixError(StandardError):
    """ Base Yalix Exception class """

    __metaclass__ = ABCMeta

    def __init__(self, message, *args):
        self.value = message.format(*args)

    def __str__(self):
        return self.value

class EvaluationError(YalixError):
    """ Evaluation specific error handling """


class EnvironmentError(YalixError):
    """ Enironment specific error handling """

