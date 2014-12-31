#!/usr/bin/env python

import unittest
import vcr
import PullCheck

class LeckPullCheckerTestCase(unittest.TestCase):
    """Tests for `Leck/PullCheck.py`."""

    @vcr.use_cassette('tests/fixtures/LeckPullCheck.yaml')
    def test_check(self):
        """Does the check method return an instance of it's object?"""
        lpc = PullCheck.LeckPullChecker('tests/config.ini.dist')
        retval = lpc.check()
        self.assertIsInstance(retval, PullCheck.LeckPullChecker)

if __name__ == '__main__':
    unittest.main()
