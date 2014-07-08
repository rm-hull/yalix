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
        import md5
        sample_code = "(define (identity x) x)"
        output = utils.highlight_syntax(sample_code)
        m = md5.new()
        m.update(output)
        self.assertEquals('c267147a39718fbcb0033ae6f7b53918', m.hexdigest())

if __name__ == '__main__':
    unittest.main()
