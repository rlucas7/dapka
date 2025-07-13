We can use the gh cli to get info about a gh user via:


```bash
# small illustrative example, location is a random string that a human enters or `null`
# the string might be a city, state/province/etc, country, or something else entirely
# note that the last two are organizations and not users
for username in rlucas7 wojzaremba yoshua karpathy lexfridman mitsuhiko rgommers scipy aws;
do
  gh api \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /users/$username
done;
```

To select specific output we can pipe this to `jq` such as
```bash
for username in karpathy PhilBeaudoin yoshua;
do
  gh api -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /users/$username | jq 'with_entries(select([.key] | inside(["login", "id", "location"])))';
done;
```
which gives:

```bash
{
  "login": "karpathy",
  "id": 241138,
  "location": "Stanford"
}
{
  "login": "PhilBeaudoin",
  "id": 229691,
  "location": "Montreal, Quebec, Canada"
}
{
  "login": "yoshua",
  "id": 178137,
  "location": null
}
```

As examples where the user location is currently a city, `null`, and `city, province, country` respectively.
```
note that Yoshua Bengio is a professor at U. of Montreal, e.g. he (likely) lives in Quebec, in or near Outrement.

# Search for pull requests

```bash
gh search prs  copilot
# increase from 30 results (default) filter to `github.com/microsoft/*` repos
gh search prs  copilot --limit 1000 --owner microsoft
```

