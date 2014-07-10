#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.exceptions import EvaluationError
import yalix.utils as utils
import yalix.globals as glob


class TestPrimitive():
    pass


class GlobalsTest(unittest.TestCase):

    def test_gensym(self):
        g1 = glob.gensym()
        g2 = glob.gensym()
        g3 = glob.gensym(prefix="Custom")
        self.assertNotEqual(g1.name, g2.name)
        self.assertNotEqual(g1.name, g3.name)
        self.assertNotEqual(g2.name, g3.name)
        self.assertEqual(g1.name[:3], g1.name[:3])

    def test_docstring_None(self):
        with utils.capture() as out:
            glob.doc(TestPrimitive())

        self.assertEqual('', out[0])

    def test_docstring(self):
        prim = TestPrimitive()
        prim.__docstring__ = "Some documentation"
        with utils.capture() as out:
            glob.doc(prim)

        self.assertEqual('-----------------\nSome documentation\n', out[0])

    def test_print(self):
        testcases = [
            (None, ''),
            ([1], '1'),
            (['a'], 'a'),
            (['a', 'b', 1, None, 2, 3], 'ab123')
        ]

        for test_value, expected in testcases:
            with utils.capture() as out:
                glob.print_(test_value)
            self.assertEqual(expected + '\n', out[0])

    def test_create_initial_env(self):
        with utils.capture() as out:
            env = glob.create_initial_env()

        self.assertEqual(env.local_stack, [])
        self.assertTrue(len(env.global_frame) > 0)
        self.assertTrue('Creating initial environment' in out[0])

    def test_format(self):
        self.assertEqual("format_no_args", glob.format_("format_no_args"))
        self.assertEqual("format_arg1_arg2", glob.format_("format_{0}_{1}", ["arg1", "arg2"]))

    def test_error(self):
        with self.assertRaises(EvaluationError) as cm:
            glob.error("A message")
        self.assertEqual("A message", cm.exception.message)

if __name__ == '__main__':
    unittest.main()
