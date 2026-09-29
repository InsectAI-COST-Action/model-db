---
title: Adding a model
description: How to add a model to the zoo, starting from the template, and what to write in the card.
---

Adding a model takes three steps. You need a terminal, but you do not need to
install anything, and there is nothing to run afterwards that tells you whether
you got it right: **the site build is the check.** If something is wrong, it
stops and says which field and what to write instead.

## 1. Copy the template folder

```bash
cp -r template content/models/my-model
```

Name the folder in kebab-case (lowercase with hyphens). 
A model with a name of its own uses it, for example
`flatbug`, `arthronat`. A model known only as "the one from that paper" uses
`<firstauthor>-<year>-<descriptor>`, such as `marin-2025-pollinator-yolov5`.

## 2. Edit `content/models/my-model/index.md`

That one file is the whole entry to be compiled. The fields at the top are 
what the catalogue table, the filters and the sidebar are built from. The 
prose below them is the model card proper.

Every field has a comment beside it explaining what it wants. Some additional
guidelines:

- **`status` starts as `draft`.** Only `published` appears on the site, so a
  half-finished entry is invisible until it is set to `published`.
- **`category` must already exist** in `data/categories.toml`. If your model
  needs a category the zoo does not have, add it there first, then build.
- **`task` lists operations only.** A model may do several (e.g., both 
  detection and segmentation)so write `task = ["Object Detection", "Instance Segmentation"]`.
- **`produces` must agree with `task`.** Declaring a `mask` output without a
  segmentation task is wrong.

Weights are never committed here. Point `url` at Zenodo, ERDA, Hugging Face or any other 
downloadable location.

## 3. Look at it

```bash
./scripts/serve.sh          # → http://localhost:1313/
```

If the build stops, read the message: it names the file, the field, and what it
wanted. Fix it and save, then Hugo rebuilds on its own.

## If the model already has a card on Hugging Face

Point at it rather than copying it. A copy starts drifting the moment the
authors edit theirs.

```toml
hf_repo     = "edgaremy/arthropod-detector"
hf_revision = "54edf7364582e9efda68c04edfd672cfe109fb4a"
```

`hf_revision` is a **commit hash, not a branch**, it could be found under "revisions" on
the model's Hugging Face page. The build refuses a branch name or a missing
hash. That is deliberate: the license and commercial-use terms you record above
are what that card said when you curated this entry, and a branch can move
underneath that claim while the entry stays put.

The site then shows both links: the revision as curated, and the authors'
current version, so a reader who wants the latest can still get it.

You still write a local card. Keep it short if the upstream one is good, but
say what a *reader of this zoo* needs, particularly limitations and license.

## Writing the card

The headings in the template are a convention, not a rule. Nothing checks for
them. They exist so two entries can be read side by side.

## Where to get help

The build error is the help. It names the file, the field and the fix. If it
does not make sense, the field list with explanations is in
[`data/schema.toml`](https://github.com/InsectAI-COST-Action/model-db/blob/main/data/schema.toml).
Open it, find the field that is raising the error, and read what it says.
