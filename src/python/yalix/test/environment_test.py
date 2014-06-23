#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.environment import Env


class TestAtom():

    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value


class GlobalFrameTests(unittest.TestCase):

    def test_define(self):
        env = Env()
        env['a'] = TestAtom('b')
        self.assertEqual(env['a'], 'b')

    def test_lookup_fails(self):
        env = Env()
        with self.assertRaises(KeyError):
            self.assertEqual(env['a'], 'b')

    def test_overwrite(self):
        env = Env()
        env['a'] = TestAtom('b')
        env['a'] = TestAtom('c')
        self.assertEqual(env['a'], 'c')

    def test_iteritems(self):
        env = Env()
        self.assertListEqual(list(env.iteritems()), [])
        for i in range(10):
            env[i] = TestAtom(i)
        self.assertItemsEqual([k for k, _ in env.iteritems()],
                              range(10))

        self.assertItemsEqual([v for _, v in env.iteritems()],
                              range(10))

class LocalStackTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
