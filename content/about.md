---
title: About
description: What this registry is, where the schema came from, and what are its known gaps.
---

This is a registry of insect detection, classification, and foundation models.

## Where the schema came from

The record format follows [Microsoft's SPARROW-Engine](https://github.com/microsoft/SPARROW-Engine),
which onboards a model by writing a descriptor beside it rather than hard-coding
its behaviour in the catalogue.

## Known gaps

- **Performance figures are unverified.** They come from source publications and
  have not been reproduced on a single source and under the same conditions.
- **Everything is `link_only`.** No weights are mirrored. Some links may break
  and the registry does not guarantee that the weights will remain available.

## Contributors

{{< contributors >}}
