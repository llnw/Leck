#!/usr/bin/env python
# Pull request validation checker
# Loads config to connect to various repos pull-requests comments and validate
#  based on different criteria.

import github
import ConfigParser


class LeckPullChecker:
    config = ConfigParser.ConfigParser()
    gh = None
    repo = 'default'

    def __init__(self, configfile='config.ini', reponame=None):
        # Initialize connection from config
        self.config.read(configfile)
        self.repo = reponame if reponame else 'default'
        self.gh = github.Github(base_url=self.config.get('default', 'github'), login_or_token=self.config.get(self.repo, 'token'))

    def check(self, pullnumber=None):
        # Run through tests pull-request acceptance
        import pprint
        repo = self.gh.get_repo('cchristensen/salt-pillar')
        pr = repo.get_pull(1)
        #pr.create_issue_comment('create_issue_comment HELLO WORLD')
        comments = pr.get_comments()
        pprint.pprint(comments)
        c = None
        for c in comments:
            print 'HI'
            pprint.pprint(c)
        issue_comments = pr.get_issue_comments()
        for ic in issue_comments:
            print 'H2'
            pprint.pprint(ic)
        return self

if __name__ == '__main__':
    #Construct based on CLI args
    lpc = LeckPullChecker('config.ini.dist')
    lpc.check()
