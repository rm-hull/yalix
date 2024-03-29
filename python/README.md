# Python Implementation

### Current Status

This project is the culmination of a couple of weeks worth of hacking,
but so far presents a plausible implementation that can be used for
experimentation. There are many missing features and many (probably)
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
* Lazy evaluation with force/delay/memoize
* Docstring support & colorized source view
* Quoting, Unquoting, Unquote-splicing

#### Features forthcoming

* Hygenic macros
* Fuller coverage of core library
* Performance tweaks around free variables
* Tail recursion

### Downloading and running a REPL

Go to a command line, ensure you have a working python installation, and

```console
$ git clone https://github.com/rm-hull/yalix.git
$ cd yalix/python
$ pipenv install
$ pipenv install -d
$ pipenv shell
$ python main.py
```
and the REPL should hopefully present:

    Creating initial environment ... DONE
    Loading library: core ... DONE
    Loading library: hof ... DONE
    Loading library: num ... DONE
    Loading library: macros ... DONE
    Loading library: repr ... DONE
    Loading library: test ... DONE
    Reading history ... DONE
    Yalix [0.0.1] on Python 3.9.13 (main, May 24 2022, 21:13:51) 
    [Clang 13.1.6 (clang-1316.0.21.2)] darwin
    Type "help", "copyright", "credits" or "license" for more information.
    In [1]: 

To exit from the REPL, use _CTRL_-D, to abort the current input, use _CTRL_-C.
If installed, GNU readline is used to allow history and simple editing.
keyword completion is avaible by pressing _TAB_.

![screenshot](https://raw.github.com/rm-hull/yalix/master/doc/python-screenshot.png)

### Language Features

Yalix is intended as a 'minimalist' LISP. As such it takes direction primarily
from PLT-Scheme and Racket.

#### Atoms

Integers, Real numbers, Hexadeicmal numbers (prefixed with 0x), Strings and
Booleans are all supported. `nil` is classed as an atom, as are
[symbols](#symbolic-computing).

```
Yalix [0.0.1] on Python 2.7.6 (default, Mar 22 2014, 22:59:56)
[GCC 4.8.2] linux2
Type "help", "copyright", "credits" or "license" for more information.
In [1]: 5
Out[1]: 5

In [2]: (atom? 6.3)
Out[2]: True

In [3]: (* 11 (+ 2.9 4.5))
Out[3]: 81.4

In [4]: 0xFFFF
Out[4]: 65535

In [5]: #t
Out[5]: True

In [6]: #f
Out[6]: False
```

#### Lazy Lists

Lists can be arbitrarily nested, and there is some syntactic sugar to make
creation simple:

```
In [7]: (list "a" "b" (list "d" "e"))
Out[7]: ('a' 'b' ('d' 'e'))

In [8]: (cons 1 2)
Out[8]: ; not working with (repr) presently ... <yalix.interpreter.Closure object at 0x7f9b114c4d10>

In [9]: (cons 1 (cons 2 (cons 3 nil)))
Out[9]: (1 2 3)

In [10]: (first (cons 1 2))
Out[10]: 1
```

The REPL will use `*print-length*` (which should be numeric & positive; root
binding is 20) to output lists in a human-readable form, and they will get
curtailed after 20 elements are output. This is to prevent infinite lists
being output, for example:

```
In [11]: (iterate inc 0)
Out[11]: (0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 ...)
```

Note that `...` is used to denote the list printing has been curtailed, not that
the list ended at that point.

Lists are lazily-evaluated by way of "thunks" by default, and represented by
CONS-cells, whose internal structure is currently implemented as a tuple.

Many construction functions will utilize the `delay` procedure to automatically
create memoized lazy lists. `cdr` will **NOT** automatically sense if it should
force evaluation, however `rest` and `next` will. It is not mandatory that `cons`
creates lazy structures.

Access into and traversal of lists is via `car`/`cdr`, or `first`/`second`/`rest`/`next`/`nth`.
`take` and `drop` (and variants) have also been implemented.

#### Let bindings

Let binding operate as per Racket, with three variations:

```
In [12]: (let (a 5)
    ...:   (+ a a))
Out[12]: 10

In [13]: (let* ((a 5)
    ...:        (b 7)
    ...:        (c (+ a b)))
    ...:   (/ (+ b c) a))
Out[13]: 3
```

The third variant, _letrec_, allows forward references like:

```
(letrec ((is-even? (lambda (n)
                       (or (zero? n)
                           (is-odd? (dec n)))))
         (is-odd? (lambda (n)
                      (and (not (zero? n))
                           (is-even? (dec n))))))
    (is-odd? 11))
```
Although this example wont quite work just yet because _or_ & _and_ haven't
been implemented yet!

#### Lambdas and function definitions

An anonymous function can be defined in the global stack as follows:

```
In [14]: (define sqr
    ...:   (lambda (x) (* x x)))
Out[14]: sqr

In [15]: (sqr 3.75)
Out[15]: 14.0625

In [16]: sqr
Out[16]: <yalix.interpreter.Closure object at 0x7fe12b3ab9d0>
```

Lambda's can be defined inside let bindings, and the unicode lambda symbol 'λ'
may be used instead. Note the _alternate_ syntactic sugar form of `define` which
combines a binding-form and formals, which incorporates the outer lambda.

```
In [17]: (define (range n)
    ...:   (letrec ((accum (λ (x)
    ...:              (if (< x n)
    ...:                (cons x (accum (inc x)))))))
    ...:     (accum 0)))
Out[17]: range
```
Functions are first class objects and can be passed around into and out
of other functions:

```
In [18]: (map sqr (range 10))
Out[18]: (0 1 4 9 16 25 36 49 64 81)

In [19]: (define (comp f g)
    ...:   (λ (x)
    ...:     (f (g x))))
Out[19]: comp

In [20]: (map (comp inc sqr) (range 10))
Out[20]: (1 2 5 10 17 26 37 50 65 82)
```

#### Variadic functions

Arguments in a variadic function are collected up into a list. Racket uses a
dot '.' to indicate collecting values - so do we. Clojure uses ampersand.
We may support that.

```
In [21]: (define  (str . xs)
    ...:     (fold + "" xs))
Out[21]: str

In [22]: (str "hello" "big" "bad" "world")
Out[22]: hellobigbadworld
```

#### Symbolic computing

Symbol references are looked-up in the environment, first in the local
stack if appropriate, then in the global frame.

Symbols can be created, and treated as first class objects, either in
quoted form, or using `(quote ...)`:

```
In [23]: (symbol "fred")
Out[23]: fred

In [24]: (symbol? fred)
EvaluationError: 'fred' is unbound in environment

In [25]: (symbol? 'fred)
Out[25]: True

In [26]: (gensym)
Out[26]: G__84

In [27]: (gensym)
Out[27]: G__85

In [28]: (symbol? (gensym))
Out[28]: True

In [29]: (gensym)
Out[29]: G__87
```

#### Metalinguistic evaluation

The parser can be invoked directly by calling `read-string`:

```
In [30]: (read-string "(+ 14 (factorial 12))")
Out[30]: <yalix.interpreter.Call object at 0x7fe12b3ff090>
```

This returns an un-evaluated s-expression which may then be directly
evaluated under an environment (Note: 'Call' as an object name may change):

```scheme
In [31]: (eval (read-string "(+ 11 (* 5 6))"))
Out[31]: 41

In [32]: (define x '(4 5 6))
Out[32]: x

In [33]: (eval x)
Out[33]: (4 5 6)

In [34]: (define y (eval x))
Out[34]: y

In [35]: (first y)
Out[35]: 4

In [36]: (second y)
Out[36]: 5

In [37]: (third y)
Out[37]: 6
```

`apply` has not yet been implemented, so the circle is not yet complete.

#### Macros

Quoting, syntax-quoting, unquoting and unquote-splicing are all supported:

```
In [38]: (define x 5)
Out[38]: x

In [39]: (define lst '(a b c))
Out[39]: lst

In [40]: `(fred x ~x lst ~lst 7 8 ~@lst)
Out[40]: (fred x 5 lst (a b c) 7 8 a b c)
```

#### Comments

The semi-colon character is used to represent a comment to the end of the
current line. Comments are stripped out by the parser and are not passed
to the interpreter.

```
In [41]: ; this is a comment, which is ignored
In [42]:
```

#### Debugging

A basic trace facility shows call invocations. It can be started in the
global frame by setting `*debug*` to a truth value, and will produce lots
of output:

```
In [43]: (define *debug* #t)
DEBUG: repr [('x', *debug*)]
DEBUG: atom? [('G__6', *debug*)]
DEBUG: repr-atom [('G__7', *debug*)]
Out[43]: *debug*

In [44]: (range 3)
DEBUG: range [('n', 3)]
DEBUG: iterate [('f', <yalix.interpreter.Closure object at 0x7f9802c6d490>), ('x', 0)]
DEBUG: memoize [('f', <yalix.interpreter.Closure object at 0x7f9802cb8610>)]
DEBUG: cons [('a', 0), ('b', <yalix.interpreter.Closure object at 0x7f9802c74790>)]
DEBUG: take [('n', 3), ('xs', <yalix.interpreter.Closure object at 0x7f9802c99f50>)]
DEBUG: pos? [('n', 3)]
DEBUG: > [('G__47', 3), ('G__48', 0)]
DEBUG: first [('xs', <yalix.interpreter.Closure object at 0x7f9802c99f50>)]

             ---  8<  ---  Lots of logging elided  ---  8<  ---

DEBUG: force [('delayed-object', <yalix.interpreter.Closure object at 0x7f9802c8d790>)]
DEBUG: atom? [('G__6', <yalix.interpreter.Closure object at 0x7f9802c8d790>)]
DEBUG: nil? [('G__0', <yalix.interpreter.Closure object at 0x7f9802c8d790>)]
DEBUG: delayed-object [('x', <yalix.interpreter.Closure object at 0x7f9802ccb810>)]
DEBUG: fold [('f', <yalix.interpreter.Closure object at 0x7f9802cfa090>), ('val', '(0 1 2)'), ('xs', None)]
DEBUG: empty? [('G__0', None)]
Out[44]: (0 1 2)
```

Of course, `*debug*` can be set inside a let binding as well, to either `#t` or `#f`,
and will be honoured in that lexical scope.

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
* ~~Support docstrings - no definition in Racket, per se. Suggest something which
  uses a deviation of the standard comment (;^) to scoop
  documentation into meta-data on the function definition. Accessed via a `(doc
  factorial)` from the REPL.~~

#### Interpreter
* ~~Lazy evaluation with `force`, `delay`, `memoize`
  (see [lazy-lists](https://github.com/rm-hull/yalix/tree/feature/lazy-lists) branch).~~
* Implement `defmacro`, `macro-expand`, splicing, backticks, etc.
* Implement `apply` as a method or special form
* Destructuring-bind
* Support namespaces with requires and use directives.

#### Core Library
* Macro implementations for `and`, `or`, `cond`, etc.
* ~~Convert list syntactic sugar from built-in to use variadic definition.~~
* Continue implementation of HOF's: `filter`, `remove`, `take`, `drop`, etc.
* ~~Implementation of common predicates: `odd?`, `even?`, `zero?`, `pos?`, `neg?`~~
* File I/O interop

#### Other
* Use [code.InteractiveConsole](https://docs.python.org/2/library/code.html#code.InteractiveConsole)
* ~~Make it work with PyPy~~
* ~~Unit testing~~
* ~~Travis CI integration~~
* ~~PEP8 conformance~~
