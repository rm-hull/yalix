#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from colors import red, green, blue, faint, bold
except ImportError:
    def identity(x, **kwargs):
        return x
    global red, green, blue
    global bold, faint
    red = identity
    green = identity
    blue = identity
    faint = identity
    bold = identity

try:
    import pygments
    from pygments.lexers.functional import RacketLexer
    from pygments.formatters import Terminal256Formatter

    def highlight_syntax(code, outfile=None):
        if code:
            return pygments.highlight(code,
                                    RacketLexer(),
                                    Terminal256Formatter(style='colorful'),
                                    outfile)
except ImportError:
    def highlight_syntax(code):
        return code
