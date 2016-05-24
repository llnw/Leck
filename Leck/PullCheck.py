#!/usr/bin/env python
# Pull request validation checker
# Loads config to connect to various repos pull-requests comments and validate
#  based on different criteria.
# The expected flow is:
#  LeckPullChecker (initialize connection/config) ->
#   check (checks the repo; iterates over all PRs) ->
#    validate_pr (iterates over a PRs comments and validates)

import glob
import os # TODO consider github/http mock file lib
import external.owners as owners
import subprocess # TODO consider Git API lib

import github3
import json
import re
import ConfigParser

class OwnersDB:
    owners_db = None
    repopath = '.'

    def __init__(self, repopath='.'):
        self.owners_db = owners.Database(repopath, fopen=file, os_path=os.path, glob=glob.glob)
        self.repopath = repopath

    def fetchReset(self, sha='origin/master'):
        PIPE = subprocess.PIPE
        wd = os.path.dirname(self.repopath)

        # git fetch origin # note: requires repo is setup with remote as origin
        process = subprocess.Popen(['git', 'fetch', 'origin'], cwd=wd, stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()
        # git reset sha --hard
        process = subprocess.Popen(['git', 'reset', sha, '--hard'], cwd=wd, stdout=PIPE, stderr=PIPE)
        stdoutput, stderroutput = process.communicate()

        return stdoutput

    def getReviewers(self, files=[], owner=None):
        # TODO validate owners exists
        reviewer = self.owners_db.reviewers_for(files, owner)
        # format as github user
        # TODO iterate all reviewers discovered.
        return '@' + reviewer.pop().split('@')[0]

    def allOwners(self, files=[], author=None):
        self.owners_db.load_data_needed_for(files)
        owners = self.owners_db.all_possible_owners(files, author)
        return owners.keys()

class LeckPullChecker:
    config = ConfigParser.ConfigParser()
    gh = None
    reponame = 'default'
    owners_db = None

    def __init__(self, configfile='config.ini', reponame=None):
        # Initialize connection from config
        self.config.read(configfile)
        self.reponame = reponame if reponame else 'default'
        self.gh = github3.GitHubEnterprise(
            url=self.config.get('default', 'github'),
            token=self.config.get(self.reponame, 'token'))

        # Monkey patch github3 Pull Requests create issue functionality.
        # TODO https://github.com/sigmavirus24/github3.py/issues/332
        def create_issue_comment(self, body):
            """Create a comment on this issue.
            :param str body: (required), comment body
            :returns: :class:`IssueComment <github3.issues.comment.IssueComment>`
            """
            json = None
            if body:
                owner, repo = self.repository
                owner = owner.split('/')[-1]
                url = self._build_url('repos', owner, repo, 'issues', str(self.number), 'comments')
                json = self._json(self._post(url, data={'body': body}), 200)
            return IssueComment(json, self) if json else None
        github3.pulls.PullRequest.create_issue_comment = create_issue_comment

    def check(self, pullnumber=None):
        for section in self.config.sections():
            # TODO skip section if we've been initialized by self.reponame
            if section == 'default':
                continue
            # TODO Submit upstream helper for owner/repo shortname passing
            section_split = section.split('/')
            ownername = section_split[0]
            reponame = section_split[1]
            self.repo = self.gh.repository(ownername, reponame)

            # TODO load up owners from on-disk repo...
            # TODO consider passing repo+ondisk/API representation as encapsulation
            self.owners_db = OwnersDB(self.config.get(section, 'repoforowners'))

            # Run through tests pull-request acceptance
            if pullnumber is None:
                for pr in self.repo.iter_pulls(state='open'):
                    self.validate_pr(pr)
            else:
                self.validate_pr(self.repo.pull_request(pullnumber))
        return self

    def validate_pr(self, pr):
        # Validate the PR on the current base.
        self.owners_db.fetchReset(pr.base.sha)
        review_comments = pr.iter_comments()
        issue_comments = pr.iter_issue_comments()

        # Validate
        self._validate_pr_initial_message(pr, issue_comments)
        self._validate_pr_title(pr, issue_comments)
        self._validate_pr_callout_reviewer(pr, issue_comments)

        # Merge (if possible)
        # TODO Status API check (pass) before allowing to merge
        self._validate_pr_merge(pr, issue_comments, review_comments)
        return self

    def _validate_pr_initial_message(self, pr, issue_comments):
        # TODO: consider breaking these out to loadable methods...
        # TODO: Remove the help message after N comments or by other authors?
        hasinitmsg = False  # TODO: config.get help == True as well
        for ic in issue_comments:
            if 'Leck PR automation' in ic.body_text:
                hasinitmsg = True
                break
        if not hasinitmsg:
            pr.create_issue_comment('''[Leck PR automation](https://github.com/llnw/Leck)

Reviews pull requests for matching criteria:

*  Sum of +1 from authorized reviewers (comment with "+1", "LGTM", or ":+1:", if authorized)
*  Merge comment from an authorized reviewer (comment with "merge", if authorized; to replace the merge button)
*  Summarize pull-request comments into the merge commit (for review in git history)
''')

    def _validate_pr_title(self, pr, issue_comments):
        rtitle = re.compile(self.config.get(self.reponame, 'title'))
        propertitle = rtitle.match(pr.title)

        hastitlemsg = False
        issueid = None
        for ic in issue_comments:
            if 'Title should be in the format' in ic.body_text:
                hastitlemsg = True
                issueid = ic.id
                break
        if not hastitlemsg and not propertitle:
            pr.create_issue_comment('''Title should be in the format: "[#PROJ-1234] Short description."''')
        if hastitlemsg and propertitle and (issueid == ic.id):
            # Remove existing comment if the title has been corrected
            ic.delete()

    def _validate_pr_callout_reviewer(self, pr, issue_comments):
        hasreviewercalloutmsg = False
        for ic in issue_comments:
            if ' please review this.' in ic.body_text:
                hasreviewercalloutmsg = True
                break
        if not hasreviewercalloutmsg:
            fls = []
            for f in pr.iter_files():
                fls.append(f.filename)
            gh_reviewer = self.owners_db.getreviewers(fls, str(pr.user) + '@llnw.com')
            pr.create_issue_comment(gh_reviewer + ''' (randomly selected by OWNERS file) please review this.''')

    def _pr_score(self, pr, issue_comments):
        # Returns true if comments add to > config required
        fls = []
        for f in pr.iter_files():
            fls.append(f.filename)
        commentstotal = 0
        for ic in issue_comments:
            if (str(ic.user) + '@llnw.com') in self.owners_db.allOwners(fls, str(pr.user) + '@llnw.com'):
                if any(x in ic.body_text.lower() for x in ['+1', 'lgtm']):
                    commentstotal += 1
        return (commentstotal >= self.config.get(self.reponame, 'required'))

    def _validate_pr_merge(self, pr, issue_comments, review_comments):
        # TODO: validate status from other systems... (use the status api?)
        #  consider using comments other than reviewers as a blocker.
        if not pr.is_merged() and self._pr_score(pr, issue_comments):
            self.repo.create_status(pr.head.sha, 'success', 'https://github.com/llnw/Leck')

            hasmergemsg = False
            issueid = None
            for ic in issue_comments:
                if 'merge' in ic.body_text:
                    hasmergemsg = True
                    issueid = ic.id
                    break
            if hasmergemsg and (issueid == ic.id):
                # TODO: Summarize PR into commit message
                # participants, merger, approvers, issue comments, review comments
                pass
        else:
            self.repo.create_status(pr.head.sha, 'pending', 'https://github.com/llnw/Leck')

    @staticmethod
    def create_pullcheck_from_hook(hook_type, data, config='config.ini'):
        reponame = None
        pullnumber = None

        js = json.loads(data)

        if (hook_type == 'pull_request'):
            repo = github3.repos.Repository(js['repository'])
            pr = github3.pulls.PullRequest(js['pull_request'])
            reponame = repo.full_name
            pullnumber = pr.number
        elif (hook_type == 'issue_comment'):
            repo = github3.repos.Repository(js['repository'])
            issue = github3.issues.Issue(js['issue'])
            reponame = repo.full_name
            pullnumber = issue.number

        # Note if reponame and pullnumber are None - we should still dtrt (albeit not as targeted).
        lpc = LeckPullChecker(config, reponame)
        lpc.check(pullnumber)
        return lpc

if __name__ == '__main__':
    # Construct based on CLI args
    lpc = LeckPullChecker()
    lpc.check()
