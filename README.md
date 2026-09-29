# Insect AI Model Database

A registry of models for insect detection, classification and trait quantification. Models must be vision-based, must have a scope spanning multiple insect genera, and must have open or at least lightly gated weights.

## Model metadata is stored as an .md file

A model is **one file**: `content/models/<id>/index.md`. Its front matter is the
registry record, the fields the website renders, and the prose beneath it is
the model card.

**The build is the validator.** Hugo checks every card against
[`data/schema.toml`](https://github.com/InsectAI-COST-Action/model-db/blob/main/data/schema.toml) as it renders, and stops with a message
naming the file, the field and what it wanted. There is no separate check
command to remember, and no way to publish a card that has not been checked.

## Quickstart

Install **Hugo extended**, the plain build cannot run the asset pipeline in
`layouts/partials/head.html`, so the site would ship without its stylesheet or
its script.

| Platform | Install |
| --- | --- |
| Linux | `./scripts/fetch-hugo.sh` once; downloads the Linux binary into `./bin` |
| macOS | `brew install hugo` |
| Windows | `winget install Hugo.Hugo.Extended` |

The fetch script downloads a Linux binary; do not run it from Windows Git Bash
or WSL when you need a native Windows executable. On macOS and Windows, use the
package-manager installation above and make sure `hugo version` includes
`+extended`.

Start the preview from the repository root:

```bash
./scripts/serve.sh          # Linux; http://localhost:1313/
```

The script uses `./bin/hugo` when present, otherwise it uses `hugo` from `PATH`.
On macOS and Windows, start the preview directly from the repository root:

```bash
hugo server --baseURL http://localhost:1313/
```

To build the static site without starting the preview, run this from the
repository root (use `./bin/hugo` instead of `hugo` if you installed with the
Linux fetch script):

```bash
hugo --gc --minify
```

## Adding a model

**Read [contributing](https://github.com/InsectAI-COST-Action/model-db/blob/main/content/contributing.md) on the running site, or in short:**

```bash
cp -r template content/models/my-model
# edit content/models/my-model/index.md, then set status = "published" when ready
./scripts/serve.sh
```

## Repository layout

```
content/models/<id>/index.md   the whole entry: front matter + model card
content/models/<id>/LICENSE    the upstream license, where it is separate
template/                      what you copy to start a new model
data/schema.toml               every field, and the values each accepts
data/categories.toml           category slugs → titles, descriptions, order
layouts/                       hand-written templates; no theme, no mounts
assets/css, assets/js          the site's only stylesheet and only script
scripts/                       fetch-hugo.sh, serve.sh
```

## Pointing at the model's own card

When a model already has a card on Hugging Face, this entry points at it instead
of copying it:

```toml
hf_repo     = "edgaremy/arthropod-detector"
hf_revision = "54edf7364582e9efda68c04edfd672cfe109fb4a"
```

The site shows **both** links, the pinned revision the entry was curated
against, and the authors' current version. `hf_revision` is a commit hash: the
build rejects a branch name, because the license and commercial-use terms in the
entry are claims about what that card said at the time, and a branch can move
while the entry stays put. Pinning is what keeps the claim checkable.

Refreshing it is a deliberate act: update the hash, and the change lands as a
reviewable diff in a pull request.

## Why the schema is small

**A field exists only if the website renders it.** The zoo used to carry
preprocessing, inference and postprocessing blocks, tensor layout,
normalisation scheme, NMS thresholds, tile sizes. Fourteen fields that a
contributor had to answer and that no page ever displayed, which asked a
biologist to know what NMS is in order to say nothing to anyone. They are gone;
whatever is genuinely useful about them belongs in the card's prose, where it
can be written as a sentence.

What is left is roughly twenty fields. Eight are required. Everything else has a
default, so a contributor who does not know the answer can delete the line.
