#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.environment import Env


class GlobalFrameTests(unittest.TestCase):

    def test_define(self):
        env = Env()
        env['a'] = 1
        self.assertEqual(1, env['a'])

    def test_lookup_fails(self):
        env = Env()
        with self.assertRaises(KeyError):
            env['a']

    def test_overwrite(self):
        env = Env()
        env['a'] = 1
        env['a'] = 2
        self.assertEqual(2, env['a'])

    def test_items(self):
        env = Env()
        self.assertListEqual(list(env.items()), [])
        for i in range(10):
            env[i] = i
        self.assertEqual(list(range(10)), sorted([k for k, _ in env.items()]))
        self.assertEqual(list(range(10)), sorted([v for _, v in env.items()]))


class LocalStackTests(unittest.TestCase):

    def test_extend(self):
        env = Env()
        env['a'] = 1
        new_env = env.extend('x', 2)

        # Original environment should not change
        self.assertEqual(1, env['a'])
        with self.assertRaises(KeyError):
            env['x']

        self.assertEqual(1, new_env['a'])
        self.assertEqual(2, new_env['x'])

    def test_shadowing(self):
        env = Env()
        new_env_a = env.extend('x', 2)
        new_env_b = new_env_a.extend('x', 5)

        # Make sure new_env didnt change, but new_env_2 did
        with self.assertRaises(KeyError):
            env['x']

        self.assertEqual(2, new_env_a['x'])
        self.assertEqual(5, new_env_b['x'])

    def test_freevars(self):
        env = Env()
        env = env.extend('a', 3)
        env = env.extend('b', 17)
        env = env.extend('c', 6)
        for x in range(10):
            env = env.extend('b', x)
        env = env.extend('b', 55)
        env = env.extend('c', 12)

        self.assertEqual(3,  env['a'])
        self.assertEqual(55, env['b'])
        self.assertEqual(12, env['c'])

        # Check local stack does not have excessive content
        self.assertEqual(3, len(env.local_stack))

    def test_non_existent_set_local(self):
        env = Env()
        with self.assertRaises(KeyError):
            env['a']
        with self.assertRaises(KeyError):
            env.set_local('a', 5)

    def test_set_local_doesnt_bleed(self):
        env = Env()
        env['a'] = 12  # Global frame

        extended_env = env.extend('a', 16)  # local shadowing
        self.assertEqual(12, env['a'])
        self.assertEqual(16, extended_env['a'])

        # Now update global 'a' in original env - check it doesnt bleed into extended
        env['a'] = 50
        self.assertEqual(50, env['a'])
        self.assertEqual(16, extended_env['a'])

        # Update 'a' in extended_env, check no bleeding again
        extended_env.set_local('a', 46)
        self.assertEqual(50, env['a'])
        self.assertEqual(46, extended_env['a'])

if __name__ == '__main__':
    unittest.main()
