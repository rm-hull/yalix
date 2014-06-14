#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yalix.exceptions import EnvironmentError

class Env:

    def __init__(self, stack=None, globals=None):
        self.stack = stack
        self.globals = globals if globals else {}


    def extend(self, name, value):
        """ Extend the stack: Note that globals are shared across extended environments """
        return Env(stack=((name, value), self.stack), globals=self.globals)

    def __setitem__(self, name, value):
        """ Adds a new global definition """
        self.globals[name] = value

    def __getitem__(self, name):
        """ Look in the stack first for the named item, then try the globals """

        env = self.stack
        while env:
            if env[0][0] == name:
                return env[0][1]
            else:
                env = env[1]

        if name not in self.globals:
            raise EnvironmentError('\'{0}\' is unbound in environment', name)

        return self.globals[name]


e = Env()
e['fred'] = 'bob'
e['fred']


e1 = e.extend('jim', 'jeff')
e2 = e1.extend('tom', 'smith')
e1 == e

e1['jim']
e2['jim']
e2['fred']

e2['elaine'] = 'carter'

e['elaine']
e['f']
