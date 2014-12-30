#!/usr/bin/env python

import unittest
import vcr
import LeckPullCheck

class LeckPullCheckerTestCase(unittest.TestCase):
    """Tests for `LeckPullCheck.py`."""

    @vcr.use_cassette('tests/fixtures/LeckPullCheck.yaml')
    def test_check(self):
        """Does the check method return an instance of it's object?"""
        lpc = LeckPullCheck.LeckPullChecker('tests/config.ini.dist')
        retval = lpc.check()
        self.assertIsInstance(retval, LeckPullCheck.LeckPullChecker)

if __name__ == '__main__':
    unittest.main()
