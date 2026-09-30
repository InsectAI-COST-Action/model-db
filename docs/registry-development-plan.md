# Development plan: a registry over existing model and format records

Status: implemented as a metadata-only adapter lookup. The subsequent simplicity
review supersedes the original rich binding proposal: schemas contain only
entry-point mappings, not copies of adapter arguments, requirements or validation.

## Goal and contribution workflow

Make model lookup and conversion planning a thin, read-only layer over the
existing database. Each fact has one authoritative home:

| Fact | Authoritative location |
| --- | --- |
| Model identity, assets, and output formats | `content/models/<model>/index.md` |
| Format identity and structure | `static/formats/detection/<format>.json` |
| Available conversions and their call contracts | The same format descriptor |
| Conversion algorithms | `src/iai_model_zoo/formats/adapters/` |

The adapter directory above is the current repository path; there is no
`formats/detection/adapters` Python directory.

The intended extension workflow is:

1. Add a model by writing its card and referencing formats in `output_format`.
   No Python or separate registry edits are needed.
2. Add a format by writing its descriptor. Discovery must not require updating a
   catalogue, Python mapping, or central list of accepted format names.
3. Add conversion support by implementing an adapter and declaring its entry
   points in that descriptor. Existing adapters may serve multiple descriptors.
   No model cards change merely because their format gains an adapter.

Documentation and examples should accompany new behavior, but must not become
additional machine-readable registries to keep synchronized.

## Design

### Discover and join existing records

Use model directory names and descriptor filename stems as identifiers. Read
TOML frontmatter and JSON using Python 3.11+ standard-library support. Discover
files deterministically and reject invalid references with file/field locations.

Join a model's `output_format` values to descriptors, then to the adapter
bindings declared in those descriptors. Do not infer adapter modules from names,
architectures, or model-specific rules.

Preserve the existing positional correspondence between `architecture` and
`output_format`. Repeated identical formats yield one conversion candidate,
retaining the associated architecture entries as provenance. Distinct formats
remain alternatives; an explicit source-format selection resolves ambiguity.
Do not guess an asset-to-architecture association from asset names. An asset
selection alone cannot disambiguate formats unless the card explicitly records
that association.

Missing `output_format`, the existing `other` placeholder, and a descriptor with
no adapter are distinguishable unresolved cases. An unknown format reference is
a validation error. Existing cards without optional backend metadata stay valid.

### Keep adapter declarations with the format

Preserve the schema language's four sections: `types`, `enums`, `structure`, and
`notes`. Reserve `notes.adapters` for a small, validated machine-readable
contract. Keep explanatory text elsewhere in `notes`; never interpret prose as
configuration. This avoids changing the meaning of `structure` or introducing
a fifth schema section.

`notes.adapters` maps `import_one`, `import_collection`, `export_one`, or
`export_collection` to explicit `module:function` strings. Keys identify direction
and image cardinality; no adapter module is inferred from a format name.

Adapter APIs and documentation own options, context, compatibility validation,
container contracts and preservation limits. Do not duplicate these in schemas
or introduce a separate requirements language. A ready path means its adapter
references exist; callers still configure and invoke those APIs.

### Compose through ISIR

The resolver constructs the common path:

`model.output_format -> source importer -> ISIR -> target exporter`

Targeting ISIR requires only the importer; using ISIR as the source requires
only the exporter. ISIR-to-ISIR is an explicit identity operation in the returned
plan, requiring no adapter import or per-model route declaration. No general
graph search or enumerated route table is needed.

Make collection handling visible in the plan. Single-image importers produce
one ISIR record; multi-image importers produce a collection of per-image records.
Per-image mapping and wrapping a single record for a collection exporter are
explicit generic operations. Never collapse several images into one record.
Preserve dataset metadata separately, particularly for COCO import/export.

### Query and resolve without execution

Retain a small interface along these lines:

```python
registry = Registry.open(snapshot_path)
candidates = registry.query(model="arthronat", target="coco")
plan = registry.resolve(
    model="arthronat",
    source="ultralytics-detect-results",
    target="isir",
)
```

Support filters over model fields and source/target formats. Select input
cardinality explicitly when both single-image and collection APIs are available.
Weight selection is unnecessary for conversion lookup and does not establish
what a particular checkpoint actually produced.

Return detached deterministic records containing model/format data, callable
references, collection operations, and metadata fingerprints. `ready` means a
path exists; `unsupported` means a binding is absent; `needs_context` identifies
unspecified ISIR input cardinality. Multiple eligible paths raise a selection
error. Prediction validity and API arguments are checked by the actual adapters.

Resolution imports no implementations and performs no downloads or inference.
Existing adapter APIs remain unchanged.

### Responsibility boundary: conversion, not model execution

The format module provides schemas and output adapters that callers apply to
already-produced model outputs to convert them through ISIR to a target format
such as COCO. The registry discovers and resolves those adapters without
executing them. Actual conversion calls execute adapter code, not model inference.

Consuming repositories own inference implementation: choosing an execution
pipeline, installing model runtimes, obtaining weights, loading models,
preprocessing inputs, and running predictions. They also supply any image,
category, model, or dataset context required by the adapters. Model-to-format
lookup does not establish or execute an inference recipe.

This is an architectural boundary, not merely a feature deferred to a later
increment. Do not add inference orchestration or runtime/default-workflow
configuration to the format module or registry. Remove the draft workflow/default
machinery rather than relocating it into frontmatter. Preserve useful evidence
in existing probe reports or model documentation before deleting unique material.

The separate `src/probe` tooling may execute models to verify documented outputs;
that evidence-gathering role is independent of the format module and must not
become a runtime dependency of conversion or resolution.

## Completed implementation

1. Documented the minimal mapping in `static/formats/README.md` and populated
   descriptors for existing Flatbug, COCO, AMI, BioMoth, Ultralytics and YOLO TXT
   adapters. Unimplemented formats remain discoverable without bindings.
2. Removed the `output_format.values` catalogue in `data/schema.toml`; Hugo
   validates identifiers against descriptor files, retaining `other` and the
   architecture alignment rule.
3. Replaced the draft registry tables with file discovery, joins through
   `output_format`, and generic ISIR composition. Removed `data/registry/`.
4. Replaced registry tests, examples and documentation. Schema validation checks
   adapter mapping syntax without importing referenced implementations.

## Acceptance checks

- Fixture-only additions of models and formats work without catalogue edits.
- Changing a model output format or redirecting a descriptor callable changes
  resolution without Python changes; a missing binding remains unsupported.
- Repeated formats deduplicate and distinct formats/cardinalities remain ambiguous.
- ISIR identity, single-to-collection wrapping and per-image export are explicit.
- COCO container construction and dataset metadata remain caller responsibilities
  documented by its adapter, not invented by the resolver.
- Invalid metadata and unknown format references fail with diagnostics.
- Resolution performs no implementation imports or network access, does not read
  outside the snapshot, and returns detached results with stable fingerprints.
- Existing schemas, adapter behavior and visible model tables remain valid.

Run:

```bash
uv run --locked --project src/probe python -m unittest discover -s scripts/tests -q
python3 scripts/check_formats.py
./bin/hugo --destination /tmp/model-db-registry-site
git diff --check
```

Completion means contributors add a model in its card, a format in its descriptor,
or conversion support in that descriptor plus its implementation, without another
catalogue or model-specific mapping to update.
