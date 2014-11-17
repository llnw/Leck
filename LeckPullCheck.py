#!/usr/bin/env python
# Pull request validation checker
# Loads config to connect to various repos pull-requests comments and validate
#  based on different criteria.

import github
import re
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
        for section in self.config.sections():
            if section == 'default':
                continue
            repo = self.gh.get_repo(section)
            # Run through tests pull-request acceptance
            if pullnumber is None:
                for pr in repo.get_pulls():
                    self.validate_pr(pr)
            else:
                self.validate_pr(repo.get_pull(pullnumber))
        return self

    def validate_pr(self, pr):
        review_comments = pr.get_comments()
        issue_comments = pr.get_issue_comments()

        # Validate
        self._validate_pr_initial_message(pr, issue_comments)
        self._validate_pr_title(pr, issue_comments)
        # Merge (if possible)
        self._validate_pr_merge(pr, issue_comments, review_comments)
        return self

    def _validate_pr_initial_message(self, pr, issue_comments):
        # TODO: consider breaking these out to loadable methods...
        hasinitmsg = False # TODO: config.get help == True as well
        for ic in issue_comments:
            if 'Leck PR automation' in ic.body:
                hasinitmsg = True
                break
        if not hasinitmsg:
            pr.create_issue_comment('''### Leck PR automation

Reviews pull requests for matching criteria:

*  Sum of +2 from authorized reviewers (comment with "+1" or ":+1:", if authorized)
*  Merge comment from an authroized reviewer (comment with "merge", if authorized; to replace the merge button)
*  Summarize pull-request comments into the merge commit (for review in git history)

More info: [Leck](http://example.com/leckhelp)
''')

    def _validate_pr_title(self, pr, issue_comments):
        rtitle = re.compile(self.config.get(self.repo, 'title'))
        propertitle = rtitle.match(pr.title)

        hastitlemsg = False
        issueid = None
        for ic in issue_comments:
            if 'Title should be in the format' in ic.body:
                hastitlemsg = True
                issueid = ic.id
                break
        if not hastitlemsg and not propertitle:
            pr.create_issue_comment('''Title should be in the format: "[#PROJ-1234] Short description."''')
        if hastitlemsg and propertitle and (issueid == ic.id):
            # Remove existing comment if the title has been corrected
            ic.delete()

    def _pr_score(self, pr, issue_comments):
        # Returns true if comments add to > config required
        commentstotal = 0
        for ic in issue_comments:
            if '+1' in ic.body:
	        commentstotal += 1
            if '-1' in ic.body:
                commentstotal -= 1
        return (commentstotal >= self.config.get(self.repo, 'required'))

    def _validate_pr_merge(self, pr, issue_comments, review_comments):
        if pr.mergeable and self._pr_score(pr, issue_comments):
            hasmergemsg = False
            issueid = None
            for ic in issue_comments:
                if 'merge' in ic.body:
                    hasmergemsg = True
                    issueid = ic.id
                    break
            if hasmergemsg and (issueid == ic.id):
                # Remove existing comment if the title has been corrected
                ic.delete()
                # TODO: Summarize PR into commit message
                # participants, merger, approvers, issue comments, review comments

if __name__ == '__main__':
    #Construct based on CLI args
    lpc = LeckPullChecker('config.ini.dist')
    lpc.check()
