#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yalix.interpreter import *
from yalix.globals import create_initial_env

env = create_initial_env()

Call(Symbol('format'),
     Atom('{0} PI = {1}'),
     List(Atom(2),
          Call(Symbol('*'),
               Atom(2),
               Symbol('math/pi')))).eval(env)

g = Call(Symbol('gensym')).eval(env)

g
g.name

