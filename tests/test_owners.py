#!/usr/bin/env python

import glob
import os
import unittest
import external.owners as owners

class OwnersTestCase(unittest.TestCase):
    """Tests for `owners.py`."""

    def setUp(self):
        self.owners_db = owners.Database('.', fopen=file, os_path=os.path, glob=glob.glob)
        self.files = ['README.md', 'tests/test_owners.py']

    def test_owners_reviewers_for(self):
        """Test, by demo, usage of owners lib."""
        self.assertGreater(len(self.owners_db.reviewers_for(self.files, 'user@example.com')), 0)

    def test_owners_all_possible_owners(self):
        self.owners_db.load_data_needed_for(self.files)
        self.assertGreater(len(self.owners_db.all_possible_owners(self.files, 'user@example.com')), 0)

if __name__ == '__main__':
    unittest.main()
