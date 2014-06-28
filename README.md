# Yalix [![Build Status](https://secure.travis-ci.org/rm-hull/yalix.png)](http://travis-ci.org/rm-hull/yalix)


> One night, around 3am, I was watching an infomercial for a product 
> claiming to restore men's hair. As I watched the story of one 
> formerly-bald individual, I became overwhelmed with joy. "At last!", 
> my brain said to itself, "This man has gotten the love and success 
> he deserves! What an incredible product this is, giving hope to the 
> hopeless!"
> 
> Throughout the intervening years I've found myself wondering if I 
> could somehow recreate the emotional abandon and appreciation for 
> life induced by chronic sleep deprivation. The ultimate solution 
> would be some kind of potion — a couple quaffs to unleash my inner 
> Richard Simmons, but not for too long.

— _Clojure for the Brave and True_ 

Yalix is a LISP interpreter written in Python. The dialect it mostly
resembles is that of [Racket](http://racket-lang.org/) but is by far
less feature packed. It is an experiment to (a) learn implementing parsers
and interpreters, (b) implementing parsers and interpreters in other
computer languages I am not familiar with.

The long term aim of this project is to firstly build a featue rich 
implementation in Python which is easy to read, and easy to extend. 
The overriding intention is pedagogical rather than optimising for 
performance. Secondly, to re-implement Yalix in a number of other
programming langugaes, including itself!

### Current Status

This project is the culmination of about a weeks worth of hacking, but
so far presents a plausible implementation that can be used for 
experimentiion. There are many missing features and many (probably)
hidden bugs.

The master branch _should_ be fairly stable; any new features will be
developer under feature branches.

#### Features implemented

* Lexical scoping & closures
* Parsing S-expressions
* Evaluation of S-expressions
* Named and anonymous functions (lambdas)
* Variadic functions
* Recursive (letrec) bindings
* Rudimentary support for symbolic computation
* Atoms: ints, real numbers, strings, booleans
* Immutable persistent data structures: linked lists
* Some core library higher-order functions (map, fold, etc.)
* Semi-colon comments

#### Features forthcoming

* Lazy evaluation with force/delay/memoize
* Hygenic macros
* Fuller coverage of core library
* Performance tweaks around free variables
* Tail recursion

### Downloading and running a REPL

Go to a command line, ensure you have a working python installation, and

    $ git clone https://github.com/rm-hull/yalix.git
    $ cd yalix/src/python/
    $ export PYTHONPATH=.:$PYTHONPATH
    $ python yalix/repl.py

and the REPL should hopefully present:

    Creating initial environment ... DONE
    Reading history ... DONE

    Yalix [0.0.1] on Python 2.7.6 (default, Mar 22 2014, 22:59:56) 
    [GCC 4.8.2] linux2
    Type "help", "copyright", "credits" or "license" for more information. 
    In [1]: 
    
To exit from the REPL, use _CTRL_-D, to abort the current input, use _CTRL_-C.
If installed, GNU readline is used to allow history and simple editing.
keyword completion is avaible by pressing _TAB_.

If [ansicolors](https://pypi.python.org/pypi/ansicolors/1.0.2) is installed, 
then the Yalix REPL will make use of color if supported by the terminal:

![screenshot](https://raw.github.com/rm-hull/yalix/master/doc/screenshot.png)

Install ansicolors with:

    $ sudo pip install ansicolors

### Language Features

Yalix is intended as a 'minimalist' LISP. As such it takes direction primarily
from PLT-Scheme and Racket.

#### Atoms

Integers, Real numbers, Strings and Booleans are all supported:

```scheme
Yalix [0.0.1] on Python 2.7.6 (default, Mar 22 2014, 22:59:56) 
[GCC 4.8.2] linux2
Type "help", "copyright", "credits" or "license" for more information.
In [1]: 5
Out[1]: 5

In [2]: (atom? 6.3)
Out[2]: True

In [3]: (* 11 (+ 2.9 4.5))
Out[3]: 81.4

In [4]: nil
Out[4]: None

In [5]: #t
Out[5]: True

In [6]: #f
Out[6]: False
```

#### Lists

Lists are represented by CONS-cells, can be arbitrarily nested, and there
is some syntactic sugar to make creation simple:

```scheme
In [7]: [1 2 3 4]
Out[7]: (1, (2, (3, (4, None))))

In [8]: (list "a" "b" (list "d" "e"))
Out[8]: ('a', ('b', (('d', ('e', None)), None)))

In [9]: (cons 1 2)
Out[9]: (1, 2)

In [10]: (cons 1 (cons 2 (cons 3 nil)))
Out[10]: (1, (2, (3, None)))
```

The internal representation is currently a 2-element tuple, but **this is
liable to change** so that it prints as a conventional list - to be done as
part of implementing lazy lists.

Access into and traversal of lists is via `car`/`cdr`, or `first`/`second`/`rest`/`next`.
Expect that `take` and `drop` (and variants) will be implemented shortly.

#### Let bindings

Let binding operate as per Racket, with three variations:

```scheme
In [11]: (let (a 5)
    ...:   (+ a a))
Out[11]: 10

In [12]: (let* ((a 5)
    ...:        (b 7)
    ...:        (c (+ a b)))
    ...:   (/ (+ b c) a))
Out[12]: 3
```

The third variant, _letrec_, allows forward references like:

```scheme
(letrec ((is-even? (lambda (n)
                       (or (zero? n)
                           (is-odd? (dec n)))))
         (is-odd? (lambda (n)
                      (and (not (zero? n))
                           (is-even? (dec n))))))
    (is-odd? 11))
```
Although this example wont work because _or_ & _and_ haven't been implemented yet!

#### Lambdas and function definitions

An anonymous function can be defined in the global stack as follows:

```scheme
In [13]: (define sqr
    ...:   (lambda (x) (* x x)))
Out[13]: sqr

In [14]: (sqr 3.75)
Out[14]: 14.0625

In [15]: sqr
Out[15]: <yalix.interpreter.primitives.Closure object at 0x7fe12b3ab9d0>
```

Lambda's can be defined inside let bindings, and the unicode lambda symbol 'λ'
may be used instead. Note the _alternate_ syntactic sugar form of `define` which
combines a binding-form and formals, which incorporates the outer lambda.

```scheme
In [16]: (define (range n)
    ...:   (letrec ((accum (λ (x) 
    ...:              (if (< x n)
    ...:                (cons x (accum (inc x)))))))
    ...:     (accum 0)))
Out[16]: range
```
Functions are first class objects and can be passed around into and out 
of other functions:

```scheme
In [17]: (map sqr (range 10))
Out[17]: (0, (1, (4, (9, (16, (25, (36, (49, (64, (81, None))))))))))

In [18]: (define (comp f g)
    ...:   (λ (x) 
    ...:     (f (g x))))
Out[18]: comp

In [19]: (map (comp inc sqr) (range 10))
Out[19]: (1, (2, (5, (10, (17, (26, (37, (50, (65, (82, None))))))))))
```

#### Variadic Functions

Arguments in a variadic function are collected up into a list. Racket uses a 
dot '.' to indicate collecting values - so do we. Clojure uses ampersand. 
We may support that.

```scheme
In [20]: (define  (str . xs)
    ...:     (fold + "" xs))
Out[20]: str

In [21]: (str "hello" "big" "bad" "world")
Out[21]: hellobigbadworld
```

#### Symbolic computing

Symbol references are looked-up in the environment, first in the local
stack if appropriate, then in the global frame.

Symbols can be created, and treated as first class objects, either in
quoted form, or using `(quote ...)`:

```scheme
In [22]: (symbol "fred")
Out[22]: fred

In [23]: (symbol? fred)
EvaluationError: 'fred' is unbound in environment

In [24]: (symbol? 'fred)
Out[24]: True

In [25]: (gensym)
Out[25]: G__84

In [26]: (gensym)
Out[26]: G__85

In [27]: (symbol? (gensym))
Out[27]: True

In [28]: (gensym)
Out[28]: G__87
```

#### Metalinguistic evaluation

The parser can be invoked directly by calling `read-string`:

```scheme
In [29]: (read-string "(+ 14 (factorial 12))")
Out[29]: <yalix.interpreter.primitives.Call object at 0x7fe12b3ff090>
```

This returns an un-evaluated s-expression which may then be directly 
evaluated under an environment (Note: 'Call' as an object name may change):

```scheme
In [30]: (eval (read-string "(+ 11 (* 5 6))") 
Out[30]: 41
```

`apply` has not yet been implemented, so the circle is not yet complete.

#### Comments

The semi-colon character is used to represent a comment to the end of the
current line. Comments are stripped out by the parser and are not passed
to the interpreter.

```scheme
In [31]: ; this is a comment, which is ignored 
In [12]: 
```

### Implementation Details

There are five main parts, all implemented in a couple of hundred lines of
Python code:

* **Parser** - implemented using _pyparsing_ - this reads a stream of text 
  characters from a string or file, converting to an abstract syntax tree
  (AST) representation of the tokens. Each form has a specific parse action
  which creates an action which can be evaluated under an environment.

* **Environment** - comprising a _global frame_ and a _local stack_: the
  global frame is used for storing definitions and is represented by a
  dictionary, while the local stack is used to keep track of variables
  bound under closures. Each call into a lambda extends the local stack
  in order to preserve lexical scope properly.

* **Interpreter** - recursively evaluates an AST under some environment.
  There are some primitive types (such as Atoms, Closures, Forward references,
  Python InterOp, etc) which evaluate into simple terms, and some language
  features like Symbols, Quotes, Lambdas, List representations, Let bindings,
  Conditionals and definitions which combine to allow complex computation to 
  be realized.

* **REPL** - a simple read/evaluate/print loop, which features a simplified
  formatter and rudimentary exception reporting.

* **Core Library** - Bootstraps some interop functions from Python to perform
  arithmetic and other 'numeric-tower' type operations, cons-cell construction
  & manipulation, and higher-order functions like map, filter & fold.

## TODO

#### Parser
* Support docstrings - no definition in Racket, per se. Suggest something like
  below, which uses a deviation of the standard comment (;^) to scoop
  documentation into meta-data on the function definition. Accessed via a `(doc
  factorial)` from the REPL.

```scheme
(define (factorial n)
  ;^ The factorial of a non-negative integer n, denoted by n!, is
  ;^ the product of all positive integers less than or equal to n.
  (if (= n 0)
    1
    (* n (factorial (- n 1)))))
```

#### Interpreter
* Lazy evaluation with `force`, `delay`, `memoize` 
  (see [lazy-lists](https://github.com/rm-hull/yalix/tree/feature/lazy-lists) branch).
* Implement `defmacro`, `macro-expand`, splicing, backticks, etc.
* Implement `apply` as a method or special form
* Destructuring-bind
* Support namespaces with requires and use directives.

#### Core Library
* Macro implementations for `and`, `or`, `cond`, etc.
* Convert list from built-in to something like:

```scheme
(define (list . xs)
  (if (empty? xs)
    nil
    (cons
      (car xs)
      (list (cdr xs)))))
```

* Continue implementation of HOF's: `filter`, `remove`, `take`, `drop`, etc.
* Implementation of common predicates: `odd?`, `even?`, `zero?`, `pos?`, `neg?`
* File I/O interop

#### Other
* Make it work with PyPy
* Unit testing
* Travis CI integration

## References

* http://www.ccs.neu.edu/home/matthias/BTLS/
* http://groups.csail.mit.edu/mac/classes/6.001/abelson-sussman-lectures/
* http://courses.cs.washington.edu/courses/cse341/11sp/
* http://racket-lang.org/

## Contributing

You're more than welcome to pitch in, there are loads of interesting
features I'd like to implement (as well as a few bugs to squash) - take a
look at the TODO list and the references above.

If there's any you feel you'd specifically like to have a go at, create an
[issue](https://github.com/rm-hull/yallic/issues/new) and I'll back-fill it
with some background information to get you going, and it can then be used as
the discussion focus.

Fork the repo, create a feature branch and once the feature is complete, submit
a pull request. Also, please try and add some tests where practical (demo's and
examples even more so) and keep this README up-to-date, and make sure you've pulled
from origin master before doing a PR.

## License

The MIT License (MIT)

Copyright (c) 2014 Richard Hull

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
