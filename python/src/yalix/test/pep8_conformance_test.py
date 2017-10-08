import unittest
import pep8
import os

IGNORES = ['E501']


class PEP8ConformanceTest(unittest.TestCase):

    def get_files(self, rootdir):
        for root, subFolders, files in os.walk(rootdir):
            for f in files:
                if f.endswith('.py') and not f.endswith('_test.py'):
                    yield os.path.join(root, f)

    def test_code_errors(self):
        """Test that we conform to PEP8."""
        pep8style = pep8.StyleGuide(ignore=IGNORES)
        result = pep8style.check_files(self.get_files('.'))
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")
