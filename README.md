# DAPKA

Project repo for: Declarative And Procedural Knowledge in Agents (DAPKA).

# binary dependencies

The package assumes you have `gh` and `jq` cli installed and available.
The `gh` cli should be authenticated with the user whose behalf the
repository mining will be conducted.

# editable install

Navigate to the directory that houses the starter and do:
first clone the repo from the remote and then
setup the development dependencies
```bash
python3  -m pip install -r dev-requirements.txt
```

then setup the dev editable install
```bash
python3 -m pip install -e .
```

now the local env has an editable install

# running tests

in the top level of the package you cloned locally do:
```bash
pytest  tests
```

if anything fails then try to get the cases to pass

# updating version
when you tag a commit for a release you must do:


```
git tag -a vX.Y.Z
```
o/w git won't find the tag.
In particular

```
git tag -s vX.Y.Z
```

won't work, so DO NOT do the latter

to get the cwd version number you do
```
python3 -m setuptools_scm
```

from top level directory.

To see all the files which are tracked you do
```
python3 -m setuptools_scm ls
```

If you amend a commit that already has a tag you need to update the
tag-commit relation to have the new tag. If your tag is vX.Y.Z and
the commit is `abcdef` after the amend then you do
```
git tag -f vX.Y.Z abcdef
```
to update the commit-tag relation so that setuptools_scm will pick up the
new tag.

when you push to the remote tags will not be updated in the push by default
so you need to do
```
git push --follow-tags
```

# Using Locally

The main execution can be done once the repo is cloned locally, regardless of it an executable install is made or not.
Run `git clone` to clone the repo locally, then navigate to the root of the repo. At the repo root do:

```bash
python3 src/dapka/repo_utils.py --owner rlucas7 --repo suggerere
```
and provided your `gh` cli is authenticated with your github account and you have `jq` available on your path as well, 
you will see something like:

```bash
/Users/rlucas7/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
Pull requests with Copilot comments: defaultdict(<class 'list'>, {1: [{'id': 'PRR_kwDOOAMMVM6w7Mt_', 'author': {'login': 'copilot-pull-request-reviewer'}, 'authorAssociation': 'NONE', 'body': '## Pull Request Overview\n\nThis PR introduces a simple multiply function along with corresponding tests to validate its behavior.\n- Added a multiply function in src/collections2/multiply.py.\n- Introduced pytest-based tests using parameterization in tests/test_multiply.py.\n\n### Reviewed Changes\n\nCopilot reviewed 2 out of 2 changed files in this pull request and generated 1 comment.\n\n| File                           | Description                                  |\n| ------------------------------ | -------------------------------------------- |\n| tests/test_multiply.py         | Adds tests for the multiply function using pytest parameterization. |\n| src/collections2/multiply.py   | Implements a basic multiply function.        |\n\n\n\n', 'submittedAt': '2025-06-28T01:45:15Z', 'includesCreatedEdit': False, 'reactionGroups': [], 'state': 'COMMENTED', 'commit': {'oid': '9f81d5464baaa509e38b7b1897ad7758ca6a6a9a'}}]})
```

though the exact results may change if we do multiple reviews on the `suggerere` repo, currenly July 13th, 2025 there is only 1 PR with copilot reviews.