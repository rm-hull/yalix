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


