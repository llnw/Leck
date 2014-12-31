# Leck

*  a.k.a. Gerrit *like* access controls for GitHub peer-review
*  a.k.a. Per-branch "permissions" on GitHub

Rather than embrace the "shiny" merge button on pull-requests, start a dialog and bring people into the conversation by embracing review and helping name and correlate issues. This project acts as a webhook receiver to then look over a pull-request for a few criteria:

*  Sum of +2 from authorized reviewers
*  Proper naming of issues (e.g. xref issues/bug reports)
*  Check to see if tests have run / successfully passed ([status api](https://developer.github.com/v3/repos/statuses/))
*  Merge comment from an authorized reviewer (to replace the merge button)
*  Summarize pull-request comments into the merge commit (for review in git history)


### See also

Similar/related projects

*  http://gerrithub.io (https://gerrit.googlesource.com/plugins/github)
*  https://github.com/christofdamian/plus-pull


Rules concepts

*  [Gerrit: `refs/meta/config`](https://gerrit-review.googlesource.com/Documentation/config-project-config.html)
*  [Chromium: OWNERS Files](http://www.chromium.org/developers/owners-files)
   *  Cleaner to grep and alert than [FreeBSD/MAINTAINERS](https://github.com/freebsd/freebsd/blob/master/MAINTAINERS)


## Externals and dependencies

Most python depencies are captured in `*requirements.txt`:

```sh
pip install -r requirements.txt
# For testing
# pip install -r test-requirements.txt
```

There are some additional dependencies based off the owners "Rules concepts" that have been added directly from external repos (e.g. no dependency configuration). Additional info can be found in `Leck/external/get.sh`.

### Owners and Owners finder example

```python
>>> import glob
>>> import os
>>> import Leck.external.owners as owners
>>> import pprint
>>> owners_db = owners.Database('.', fopen=file, os_path=os.path, glob=glob.glob)
>>> pprint.pprint(owners_db.reviewers_for(['README.md'], 'reviewinguser@example.com'))
set(['cchristensen@llnw.com'])
```

(see also: Tests and [`owners_example.py`](https://gist.github.com/christianchristensen/557e4608d59320a03926))

#### Repo dependency setup for Leck

`config.ini` Should have the associated on disk repo location configured for the section under `repoowner`. The assumptions for this directory are:

*  The repo and the keys to update it are under control of the user running the Leck program (e.g. it will shell out to perform git updates)
*  It will be reset to the pull-requests base of comparison to perform the lookup of the OWNERS information.


## Testing

Some of this utility can be exercised locally and unit-tested for expected behavior. Ultimately Leck is very API and data dependent; therefore, in order to accomplish a reasonable assurance of functionality the data to test the decision logic is stored in `tests/fixtures/` (originally generated and injected by the [VCR.py](https://github.com/kevin1024/vcrpy) lib). These requests response scenarios from the [GitHub API v3](https://developer.github.com/v3/) are used in conjunction with the different test scenarios to validate expected work-flow and configuration behavior.

```sh
make test # Runs lint, pep8, and unittests

# see also
make help
```


## The Name

> [Bart van der Leck](http://en.wikipedia.org/wiki/Bart_van_der_Leck) was a Dutch painter, designer, and ceramacist. With Theo van Doesburg and Piet Mondrian he founded the De Stijl art movement.

![Metz & Co. showroom with wall hangings (left and rear walls) and carpet by Bart van der Leck, and furniture by Gerrit Rietveld](http://upload.wikimedia.org/wikipedia/commons/4/4f/Metz_%26_Co_showroom_001.jpg)

([Mondrian (Perforce), Rietveld (SVN), Gerrit (Git), Leck (GitHub)](https://code.google.com/p/gerrit/wiki/Background))
