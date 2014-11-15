# Leck

*  a.k.a. Gerrit *like* access controls for GitHub peer-review
*  a.k.a. Per-branch "permissions" on GitHub

Rather than embrace the "shiny" merge button on pull-requests, start a dialog and bring people into the conversation by embracing review and helping name and correlate issues. This project acts as a webhook reciever to then look over a pull-request for a few criteria:

*  Sum of +2 from authorized reviewers
*  Proper naming of issues (e.g. xref issues/bug reports)
*  Check to see if tests have run / successfully passed ([status api](https://developer.github.com/v3/repos/statuses/))
*  Merge comment from an authroized reviewer (to replace the merge button)
*  Summarize pull-request comments into the merge commit (for review in git history)


### See also

Similar/related projects

*  http://gerrithub.io (https://gerrit.googlesource.com/plugins/github)
*  https://github.com/christofdamian/plus-pull


Rules concepts

*  [Gerrit: `refs/meta/config`](https://gerrit-review.googlesource.com/Documentation/config-project-config.html)
*  [Chromium: OWNERS Files](http://www.chromium.org/developers/owners-files)
