# Yalix

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

Yalix is a **Y**et **a**nother **L**ISP **i**nterpreter **i**n **X**, where X
is a different programming language. The dialect it mostly
resembles is that of [Racket](http://racket-lang.org/) but borrows
ideas from [Clojure](http://clojure.org/) as well. Yalix is by far
less feature packed than both of the above; it is an experiment to
(a) learn about implementing parsers, interpreters, streams and macros,
and then (b) re-implementing those features in other computer
languages I am not particularly familiar with.

The long term aim of this project is to firstly build a featue rich
implementation in Python which is easy to read, and easy to extend.
The overriding intention is pedagogical rather than optimising for
performance. Secondly, to re-implement Yalix in a number of other
programming langugaes, including itself!

### Current Status

See the sub project directories for implementation specific details

## References

* http://www.ccs.neu.edu/home/matthias/BTLS/
* http://groups.csail.mit.edu/mac/classes/6.001/abelson-sussman-lectures/
* http://courses.cs.washington.edu/courses/cse341/11sp/
* http://racket-lang.org/
* http://www.buildyourownlisp.com/

## (Y F) = (F (Y F))

![screencap](https://raw.github.com/rm-hull/yalix/master/doc/costanza.png)

> "... but what LISP is, is the fixed point of the process that says if I
> knew what LISP was, and substituted it in for eval and apply and so on,
> on the right hand side of all those recusion equations, then if it was
> a real good LISP, it was a real one, then the left hand side would also
> be LISP. So I made sense of that definition. Now, whether or not there's
> an answer, isn't so obvious. I can't attack that.

— _George Costanza on the nature of LISP._

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
