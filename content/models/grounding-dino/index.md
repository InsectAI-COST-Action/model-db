+++
# ═══════════════════════════════════════════════════════════════════════════════
#  A model card for the Insect AI Model Zoo.
# ═══════════════════════════════════════════════════════════════════════════════
#
#  To add a model:
#
#      cp -r template content/models/your-model-id
#      #  edit content/models/your-model-id/index.md
#      ./scripts/serve.sh
#
#  Name the folder in kebab-case. A model with a name of its own uses it -
#  `flatbug`, `arthronat`. A model known only as "the one from that paper" uses
#  <firstauthor>-<year>-<descriptor>, e.g. `marin-2025-pollinator-yolov5`.
#
#  Everything between the +++ lines is checked when the site builds. Get one
#  wrong and the build stops and tells you which file and what to write, in
#  plain language. You do not have to run a separate command to find out.
#
#  Every field the site displays is in this file. Anything else you want to say
#  goes in the prose below the closing +++, where you can say it in a sentence
#  instead of in a field.

# ── Identity ──────────────────────────────────────────────────────────────────

title              = "Grounding DINO"
description        = "Open-vocabulary model that can predict objects in images based on a text prompt."
foundation         = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

category           = "detection" 
task               = ["Object Detection", "Classification", "Embedding"] 
architecture       = ["Swin Transformer"] 
output_format      = ["grounding-dino-hf-results"]
# base_model         = "DINO"                    # If this is a fine-tuned model, name the
                                              # base model it was fine-tuned from.
year               = 2023 
license            = "Apache-2.0" 
status             = "published" 

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-29 
vocabulary_scope   = "open" 
geographic_scope   = "Global" 
produces           = ["bbox", "label", "embedding"] 
image_input_size   = "any" 
input_modality     = ["text", "image"] 
developer          = "IDEA research" 
paper_url          = "https://arxiv.org/abs/2303.05499" 

# ── Weights ───────────────────────────────────────────────────────────────────
#
# Where to download the model. The FIRST block is the link the catalogue table
# shows. Add another only if the model genuinely ships several files, the way
# FlatBug ships a YOLOv8n/s/m/l ladder.
#
# Weights are never committed here. GitHub refuses files over 100 MB and the
# authors host them anyway.

[[assets]]
key      = "hf-repo" 
provider = "huggingface" 
url      = "https://huggingface.co/IDEA-Research/grounding-dino-base"
note       = "Swin-Base variant (56.7 AP on COCO fine-tuned). For smaller/faster deployment, use grounding-dino-tiny (Swin-Tiny, 48.4 AP zero-shot)."

[[assets]]
key      = "hf-repo-tiny" 
provider = "huggingface" 
url      = "https://huggingface.co/IDEA-Research/grounding-dino-tiny"
note       = "Swin-Tiny variant — recommended for edge deployment and quick prototyping. ~1GB download."



# ── The model's own card, if it has one elsewhere ─────────────────────────────
#
# If the authors already keep a card on Hugging Face, point at it rather than
# copying it here - a copy starts drifting the moment they edit theirs.
#
# hf_revision is a COMMIT HASH, not a branch. Find it under "revisions" on the
# model's Hugging Face page. A branch name can move, and the license and
# commercial-use terms recorded above are what that card said when this entry
# was curated; pinning is what keeps that claim checkable.
#
# The site then shows both links: the pinned revision as curated, and the
# author's current version.

hf_repo     = "IDEA-Research/grounding-dino-base"
hf_revision = ""
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** Zero-shot object detection for scenarios where target classes are unknown. Ideal for annotation assist tools, and open-set detection tasks where fixed-class detectors fail. Also supports expression comprehension (detecting objects via complex descriptions like "the damaged leaf near the stem"). 

## Architecture and training

Grounding DINO combines a DINO-style DETR detector with grounded pre-training that fuses vision and text modalities. The architecture uses:

- **Visual backbone**: Swin Transformer (Tiny or Base variants; later versions use ViT-L or EfficientViT-L1)
- **Text encoder**: BERT-based transformer
- **Fusion module**: Feature enhancer with cross-modality attention and language-guided query selection
- **Decoder**: Cross-modality decoder predicting bounding boxes and text alignment scores

**Training data:** O365 (Objects365), GoldG (Grounding Data), Cap4M (caption data), and for later versions: COCO, OpenImage, ODinW-35, RefCOCO. The model learns object-level representations without explicit class labels through contrastive image-text grounding.

## Inputs and outputs

**Inputs:**
- Image (RGB, any resolution; internally resized to 800×1333 pixels)
- Text prompt (lowercase, phrases must end with period—e.g., "a butterfly." "damaged wing.")

**Outputs:**
- Bounding boxes (xyxy format) with confidence scores
- Per-box text similarity scores
- Maximum ~900 object proposals (reduced to 300 in 1.6+)

**Preprocessing requirement:** No class list needed.

The documented [Hugging Face results profile](/formats/detection/grounding-dino-hf-results.json) describes `post_process_grounded_object_detection` in Transformers **4.40.2**, matching the author model-card example. It returns one dictionary per image with `scores` and `boxes` tensors plus decoded phrase `labels`. Passing `target_sizes` produces pixel corners; omitting it produces normalized corners. This profile is source-inspected only and deliberately version-specific: newer Transformers APIs can change keys and signatures.

## Performance

| Benchmark | Setting | Score |
|-----------|---------|-------|
| COCO minival | Zero-shot transfer (no COCO training data) | 52.5 AP |
| COCO minival | Fine-tuned | 63.0 AP / 57.2 AP (Tiny) |
| ODinW-35 | Zero-shot | 26.1 mean AP (new SOTA at release) |
| LVIS-minival | Zero-shot (Grounding DINO 1.5 Pro) | 55.7 AP |
| LVIS-val | Zero-shot (Grounding DINO 1.5 Pro) | 47.6 AP |
| COCO | Zero-shot (Grounding DINO 1.6 Pro) | 55.4 AP |

Sources: Liu et al. 2023 (ECCV 2024), Grounding DINO 1.5/1.5 API technical report (arXiv:2405.10300).

## Limitations

**Critical constraints for insect monitoring:**

- **Small objects**: Performance degrades on very small insects (<1% image area); post-processing size filtering recommended
- **Occlusion**: Limited robustness to heavily occluded specimens; partial visibility reduces detection confidence
- **Fine-grained distinctions**: Struggles with morphologically similar taxa (e.g., closely related species without distinctive markings)
- **Life stage variation**: Not evaluated on larval/pupal stages; training data is dominated by adult forms
- **Background complexity**: Dense vegetation or cluttered substrates increase false positives
- **Speed**: ~3 FPS on V100 GPU (base variant); Edge variants reach 14 FPS but with accuracy trade-offs
- **Hallucinations**: Earlier versions produced spurious detections; 1.5+ variants show reduced hallucination rates but still occur with ambiguous prompts

The model cannot perform segmentation (unlike Grounded SAM) and requires post-processing (e.g., with SAM) for instance masks.

## How to obtain the weights

**Hugging Face (recommended for prototyping):**
- Tiny variant: https://huggingface.co/IDEA-Research/grounding-dino-tiny
- Base variant: https://huggingface.co/IDEA-Research/grounding-dino-base

**Latest versions (1.5/1.6 Pro & Edge):**
- GitHub: https://github.com/IDEA-Research/Grounding-DINO-1.5-API
- Manual checkpoint download required; not accessible via `transformers` library

**License:** Apache-2.0 permits commercial use and modification. No gated access required.

**Usage note:** When loading via Hugging Face Transformers, ensure `transformers>=4.38.0` for `AutoModelForZeroShotObjectDetection` support. Text tokens must end with periods and be lowercased.

## Citation

``` bibtex
@misc{liu2023grounding,
      title={Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection}, 
      author={Shilong Liu and Zhaoyang Zeng and Tianhe Ren and Feng Li and Hao Zhang and Jie Yang and Chunyuan Li and Jianwei Yang and Hang Su and Jun Zhu and Lei Zhang},
      year={2023},
      eprint={2303.05499},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
``` 
