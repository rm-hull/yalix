#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.source_view import *


class TestPrimitive(object):
    def __init__(self, source, location):
        self.__source__ = source
        self.__location__ = location


class SourceViewTests(unittest.TestCase):

    def test_find_outer_form_bounds__simple(self):
        src = """
; Some comment
(define x (+ 3 2))

(define (make-counter n)
  (λ ()
    (set! n (+ n 1))))
"""
        prim = TestPrimitive(src, 27)
        self.assertEqual(src, source(prim))
        self.assertEqual('(define x (+ 3 2))', source_view(prim))

    def test_find_outer_form_bounds__parens_in_string(self):
        src = """
; Some comment
(define x "Something here :-)")

"""
        prim = TestPrimitive(src, 27)
        self.assertEqual(src, source(prim))
        self.assertEqual('(define x "Something here :-)")', source_view(prim))

    def test_find_outer_form_bounds__parens_and_dblquote_in_string(self):
        src = """
; Some comment
(define x "Something\\\" here :-)")

"""
        prim = TestPrimitive(src, 27)
        self.assertEqual(src, source(prim))
        self.assertEqual('(define x "Something\\\" here :-)")', source_view(prim))

    def test_find_outer_form_bounds__location_not_in_parens(self):
        src = """
; Some comment
(define x "Something\\\" here :-)")

"""
        prim = TestPrimitive(src, 7)
        self.assertEqual(src, source(prim))
        self.assertEqual(src, source_view(prim))

    def test_find_outer_form_bounds__no_location(self):
        src = """
; Some comment
(define x "Something\\\" here :-)")

"""
        prim = TestPrimitive(src, None)
        self.assertEqual(src, source(prim))
        self.assertEqual(src, source_view(prim))


if __name__ == '__main__':
    unittest.main()
