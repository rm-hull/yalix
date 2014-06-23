# Yalix

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
* Recursive (letrec) definitions
* Rudimentary support for symbolic computation
* Atoms: ints, real numbers, strings, booleans
* Immutable persistent data structures: linked lists
* Some core library higher-order functions (map, fold, etc.)

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
    
To exit from the REPL, use _CTRL_-D, to abort the current input, use
_CTRL_-C.

If installed, GNU readline is used to allow history and simple editing.
keyword completion is avaible by pressing _TAB_.

### Language Features

## TODO

## References

* http://racket-lang.org/
* http://courses.cs.washington.edu/courses/cse341/11sp/

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
