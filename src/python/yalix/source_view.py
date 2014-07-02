#!/usr/bin/env python
# -*- coding: utf-8 -*-


def file(primitive):
    return getattr(primitive, '__file__', None)


def source(primitive):
    return getattr(primitive, '__source__', None)


def location(primitive):
    return getattr(primitive, '__location__', None)


def find_outer_form_bounds(primitive):
    src = source(primitive)
    loc = location(primitive)
    if src is None or loc is None:
        return None

    n = len(src)
    while loc > 0 and src[loc-1:loc+1] != '\n(':
        loc -= 1

    start = loc
    in_string = False
    count_parens = 1
    loc += 1
    while loc < n and count_parens > 0:

        c = src[loc]
        if in_string:
            if c == '"':
                in_string = src[loc-1] == '\\'
        else:
            if c == '(':
                count_parens += 1
            elif c == ')':
                count_parens -= 1
            elif c == '"':
                in_string = True
        loc += 1

    end = loc

    return start, end

def source_view(primitive):
    src = source(primitive)
    if src is not None:
        bounds = find_outer_form_bounds(primitive)
        if bounds:
            start, end = bounds
            return src[start:end]
        else:
            return src # [location(primitive):]
