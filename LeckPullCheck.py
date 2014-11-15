#!/usr/bin/env python
# Pull request validation checker
# Loads config to connect to various repos pull-requests comments and validate
#  based on different criteria.

import github3
import ConfigParser


class LeckPullChecker:
    def __init__(self, config='config.yml', reponame=None):
        # Initialize connection from config
        Config = ConfigParser.ConfigParser()
        Config.read(config)
        import pprint
        pprint.pprint(Config.sections())

    def check(self, pullnumber=None):
        # Run through tests pull-request acceptance
        pass

if __name__ == '__main__':
    #Construct based on CLI args
    LeckPullChecker('config.yml.dist')
