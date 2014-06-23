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
        self.assertEqual('b', env['a'])

    def test_lookup_fails(self):
        env = Env()
        with self.assertRaises(KeyError):
            self.assertEqual('b', env['a'])

    def test_overwrite(self):
        env = Env()
        env['a'] = TestAtom('b')
        env['a'] = TestAtom('c')
        self.assertEqual('c', env['a'])

    def test_items(self):
        env = Env()
        self.assertListEqual(list(env.items()), [])
        for i in range(10):
            env[i] = TestAtom(i)
        self.assertEqual(list(range(10)), sorted([k for k, _ in env.items()]))
        self.assertEqual(list(range(10)), sorted([v for _, v in env.items()]))


class LocalStackTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
