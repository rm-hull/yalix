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

#    def test_syntax_highligher(self):
#        import hashlib
#        sample_code = "(define (identity x) x)"
#        output = utils.highlight_syntax(sample_code)
#        if output != sample_code:
#            # Pygments in action
#            m = hashlib.sha224(output.encode('utf-8'))
#            self.assertEquals('7ec4fce8a935c23538e701e1da3dfc6ce124ee5555cd90e7b5cd877e', m.hexdigest())

if __name__ == '__main__':
    unittest.main()
