#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import unittest
import yalix.repl as repl
import yalix.utils as utils


def send_inputs(*args):
    # count always starts from 1
    def invoke(count):
        try:
            cmd = args[count - 1]
            if isinstance(cmd, str):
                print 'yield', cmd
                yield cmd
            else:
                print 'raise', cmd
                raise cmd
        except IndexError:
            raise EOFError()
    return invoke


def capture_outputs(collector):
    """ Collector should be dict-like """
    def invoke(result, count):
        collector[count] = result
    return invoke


class ReplTests(unittest.TestCase):

    def test_license(self):
        self.assertTrue(len(repl.license()) > 0)
        self.assertTrue(str(datetime.now().year) in repl.license())

    def test_copyright(self):
        self.assertTrue(len(repl.copyright()) > 0)
        self.assertTrue(str(datetime.now().year) in repl.copyright())

    def test_help(self):
        self.assertTrue(len(repl.help()) > 0)
        self.assertTrue('github.com/rm-hull/yalix' in repl.help())

    def test_init_readline(self):
        with utils.capture() as out:
            repl.init_readline({})

        self.assertTrue('Reading history' in out[0])
        self.assertTrue('DONE' in out[0])

    def test_repl_starts_OK(self):
        commands = send_inputs("(+ 1 2 3 4)", "(iterate inc 0)",
                               KeyboardInterrupt())
        results = {}
        collector = capture_outputs(results)

        with utils.capture() as out:
            repl.repl(inprompt=commands, outprompt=collector)

        print results
        self.assertEqual('10', results[1])
        self.assertEqual('(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 ...)', results[2])
        self.assertTrue('KeyboardInterrupt' in out[0])
        self.assertTrue('Bye!' in out[0])

if __name__ == '__main__':
    unittest.main()
