#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.completer import Completer


class CompleterTests(unittest.TestCase):

    env = {
        'apple': 'APPLE',
        'avocado': 'AVOCADO',
        'apricot': 'APRICOT',
        'orange': 'ORANGE',
        'pear': 'PEAR',
        'strawberry': 'STRAWBERRY',
        'raspberry': 'RASPBERRY',
        'blueberry': 'BLUEBERRY'
    }

    def collect(self, completer, text):
        matches = []
        state = 0
        while True:
            word = completer.complete(text, state)
            if word:
                matches.append(word)
                state += 1
            else:
                break

        return sorted(matches)

    def test_complete_match(self):
        c = Completer(self.env)
        m1 = self.collect(c, 'a')
        m2 = self.collect(c, 'ap')
        m3 = self.collect(c, 'apr')
        self.assertEqual(['apple', 'apricot', 'avocado'], m1)
        self.assertEqual(['apple', 'apricot'], m2)
        self.assertEqual(['apricot'], m3)

    def test_complete_no_match(self):
        c = Completer(self.env)
        m = self.collect(c, 'tom')
        self.assertEqual([], m)


if __name__ == '__main__':
    unittest.main()
