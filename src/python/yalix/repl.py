#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yalix.interpreter.primitives import *
from yalix.interpreter.builtins import *
from yalix.parser import parse
from yalix.globals import create_initial_env

env = create_initial_env()

lst1 = Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil())))
lst2 = List(Atom(4), Atom(2), Atom(3))

#Eq(Cons(Atom(4), Cons(Atom(2), Cons(Atom(3), Nil()))), lst1).eval(env)
#Eq(lst2, lst1).eval(env)
#
#Eq(Atom(True),
#   Not(Atom(False))).eval(env)

Nil_QUESTION(Nil()).eval(env)
Nil_QUESTION(Atom('Freddy')).eval(env)

Atom_QUESTION(Atom('Freddy')).eval(env)
Atom_QUESTION(Nil()).eval(env)

#Eq(Nil(), Atom(None)).eval(env)

#Car(Cdr(lst1)).eval(env)

(Cdr(Nil())).eval(env)

Let("f",
    Atom("Hello"),
    Cons(Symbol("f"),
         Symbol("f"))).eval(env)

Let_STAR([('a', Atom('Hello')),
          ('b', List(Atom(1), Atom(2), Atom(3))),
          ('c', Atom('World')),
          ('c', List(Atom('Big'), Symbol('c')))],  # <-- re-def shadowing
         List(Symbol('a'), Symbol('c'), Symbol('b'))).eval(env)

Let('identity',
    Lambda(['x'], Symbol('x')), # <-- anonymous fn
    Call(Symbol('identity'), Atom(99))).eval(env)

# InterOp, i.e. using Python functions
import operator
InterOp(operator.add, Atom(41), Atom(23)).eval(env)

# check unicode, pi & golden ratio
Define('π', Atom(3.14159265358979323846264338327950288419716939937510)).eval(env)
Define('ϕ', Atom(1.618033988749894848204586834)).eval(env)
env['π']
env['ϕ']

Symbol('π').eval(env)
Symbol('ϕ').eval(env)


#from __future__ import print_function
#Define('print', Lambda(['text'], InterOp(print_function, Symbol('text')))).eval(env)

Call(Symbol('+'), Atom(99), Atom(55)).eval(env)
Call([Symbol('+'), Atom(99), Atom(55)]).eval(env)
Call(array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])).eval(env)
array_to_linked_list([Symbol('+'), Atom(99), Atom(55)])


env['+']

Call(Symbol('random')).eval(env)

q = Quote([Symbol('+'), Atom(2), Atom(3)]).eval(env)
q
Call(q).eval(env)

#Call(Quote([Symbol('+'), Atom(2), Atom(3)])).eval(env)

# (let (rnd (random))
#   (cond
#     ((< rnd 0.5)  "Unlucky")
#     ((< rnd 0.75) "Close, but no cigar")
#     (#t           "Lucky")))
#
Let('rnd', Call(Symbol('random')),
    Cond(
      (Call(Symbol('<'), Symbol('rnd'), Atom(0.5)), Atom("Unlucky")),
      (Call(Symbol('<'), Symbol('rnd'), Atom(0.75)), Atom("Close, but no cigar")),
      (Atom(True), Atom("Lucky")))).eval(env)


# (define factorial
#   (lambda (x)
#     (cond
#       ((zero? x) 1)
#       (#t        (* x (factorial (- x 1)))))))
#
Define('zero?', Lambda(['n'], Call(Symbol('=='), Symbol('n'), Atom(0)))).eval(env)
Define('factorial', Lambda(['x'],
                           Cond((Call(Symbol('zero?'), Symbol('x')), Atom(1)),
                                (Atom(True), Call(Symbol('*'),
                                                  Symbol('x'),
                                                  Call(Symbol('factorial'),
                                                       Call(Symbol('-'),
                                                            Symbol('x'),
                                                            Atom(1)))))))).eval(env)

# (factorial 10)
Call(Symbol('factorial'), Atom(10)).eval(env)

# (format "{0} PI = {1}" (list 2 (* 2 math/pi)))
Call(Symbol('format'),
     Atom('{0} PI = {1}'),
     List(Atom(2),
          Call(Symbol('*'),
               Atom(2),
               Symbol('math/pi')))).eval(env)

# (gensym)
g = Call(Symbol('gensym')).eval(env)
g
g.name



# =============================================================================================

test1 = "(define *hello* (list \"world\" -1 #t 3.14159 (list 1 2 3)))"

test2 = """
(let (rnd (random))
  (cond
    ((< rnd 0.5)  "Unlucky")
    ((< rnd 0.75) "Close, but no cigar")
    (#t           "Lucky")))
"""

test3 = """
(define factorial
  (lambda (x)
    (cond
      ((zero? x) 1)
      (#t        (* x (factorial (- x 1)))))))

(factorial 10)
"""

parse(test1).next()

list(parse(test3))

for sexp in parse(test3):
    print sexp.eval(env)
