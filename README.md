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
