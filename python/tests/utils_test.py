#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import yalix.utils as utils


class UtilsTest(unittest.TestCase):

    def test_log_progress_reports_FAILED(self):
        with utils.capture() as out:
            with self.assertRaises(KeyError):
                with utils.log_progress("Testing log message"):
                    raise KeyError
        self.assertTrue('Testing log message' in out[0])
        self.assertTrue('FAILED' in out[0])

    def test_log_progress_reports_DONE(self):
        with utils.capture() as out:
            with utils.log_progress("Testing log message"):
                pass
        self.assertTrue('Testing log message' in out[0])
        self.assertTrue('DONE' in out[0])

    def test_syntax_highligher(self):
        import hashlib
        sample_code = "(define (identity x) x)"
        output = utils.highlight_syntax(sample_code)
        if output != sample_code:
            # Pygments in action
            m = hashlib.sha224(output.encode('utf-8'))
            self.assertEquals(
                'a1d31477532d54019ac8ef9289a450faaf6127ad3e5246aef3b9353d', m.hexdigest())

    def test_balance_empty(self):
        self.assertEqual(0, utils.balance(''))

    def test_balance_single_parens(self):
        self.assertEqual(0, utils.balance('()'))
        self.assertEqual(-1, utils.balance(')('))
        self.assertEqual(0, utils.balance('  ( )   '))
        self.assertEqual(0, utils.balance('(sfs sfsfs sdf) sfs'))

    def test_balance_unbalanced_parens(self):
        self.assertEqual(1, utils.balance('(sfs sfsfs sdf sfs'))
        self.assertEqual(-1, utils.balance('sfs sfsfs sdf sfs)'))

    def test_balance_nested_parens(self):
        self.assertEqual(0, utils.balance('(sfs (sfsfs) (sdf (sfs)))'))
        self.assertEqual(0, utils.balance('(sfs (sfsfs (sdf (sfs))))'))
        self.assertEqual(0, utils.balance('(((((sfs) sfsfs) sdf) sfs))'))


if __name__ == '__main__':
    unittest.main()
