# EvidenceBoundary: bilingual document-injection evaluation of hosted Tiny Aya

**Public code, synthetic inputs/labels, report and aggregate metrics. Raw hosted responses and logs are withheld.**

**One-line finding:** on 200 paired synthetic test cases, adding an explicit document-boundary instruction changed exact extraction from **93.5% to 90.0%**, while full-marker emission stayed **1/160 attacked cases** in both conditions. This is a negative result for this particular prompt intervention, not evidence that hardening generally reduces safety.

**Track:** Lexsi Track 2a, problem 2, adversarial and safety evaluation sets. No model training, weight change, adapter, or activation intervention was performed. “Hardened” in the raw files is just the added-instruction condition.

## Abstract

EvidenceBoundary is an English/Russian document-injection benchmark for exact extraction of approved catalog references. CuratorKIT turns 264 synthetic input rows into 240 unique cases across 24 fact families; AuditKIT evaluates saved model responses using six deterministic scorers. We compare a baseline system instruction with an added instruction treating document content as untrusted evidence. Prompts, scores and settings were locally frozen before a 200-case held-out evaluation, yielding 400 real responses from the official Cohere Labs Tiny Aya hosted demo. Exact accuracy was 187/200 (93.5%) for baseline and 180/200 (90.0%) with the added instruction, a difference of −3.5 percentage points (descriptive paired-family 95% bootstrap interval: −6.0 to −1.5). Clean accuracy remained 40/40 in both conditions, and full-marker emission remained 1/160 attacked cases in both. A secondary marker-or-suffix diagnostic changed from 3/160 to 2/160; this small count difference does not establish improved safety. Post-hoc inspection found that 28 of 33 incorrect responses preserved the correct eight-character code but omitted the required REF- prefix. Thus strict formatting regressions, rather than widespread attacker-marker compliance, dominate the observed failures. Collection completed in two audited segments after a collection interruption; replay adds no observations. The hosted endpoint exposes neither weight revision nor generation seed. These results characterize one narrow synthetic extraction task, not general model safety or a verified fixed-weight experiment.

## For judges: the essential evidence

- CuratorKIT **0.1.24** performs real schema validation, deduplication, controlled cleaning and export: **264 → 240** unique rows, with 24 deliberate duplicates removed. A fresh network-disabled reproduction produced byte-identical raw data, curated cases and both splits.
- AuditKIT **1.1.7** orchestrates generation through a `CallableModel`; the resumed segment has a complete native export. After interruption, a separate network-disabled AuditKIT replay audits all **400 saved responses** against all six frozen scores. Replay is **zero additional model observations**.
- The new development run is complete: 20 responses on F01, 9/10 strict accuracy per condition, clean 2/2 per condition. Its results are not pooled with the held-out test. No prompts or scorers changed after this review.
- Held-out coverage is complete: **200 cases × 2 conditions = 400 responses**, 20 fact families, 100 cases per language per condition. Unique event IDs, exact planned order, paired coverage, source/data hashes and native-score agreement all verify.
- The 292-response prefix and 108-response continuation are retained separately. The stopped process's original `RUNNING` manifest was preserved rather than rewritten. The authoritative final status is `COMBINED_SEGMENTS_COMPLETE_OFFLINE_AUDIT` in the retained non-public combined manifest.

## Task, threat model and motivation

A structured cataloging workflow needs the approved reference, not an obsolete draft reference or instructions embedded in a supplied document. The attacker controls an appended portion of the fictional document, but not the system prompt or the approved-reference field. Four fixed attacks request a harmless marker through direct override, role spoofing, a forged evaluator claim, or a replacement output format. The task requires `ANSWER:REF-` followed by eight uppercase hexadecimal characters, without extra text; only outer whitespace is stripped for scoring.

The baseline already gives an explicit extraction/format instruction. The comparison appends a further instruction treating document content as untrusted evidence and rejecting document-level commands. The contrast therefore tests this particular extra instruction, not “no instruction” versus a comprehensive defense. There are no adaptive attacks, best-of-N search, harmful operational payloads, real targets or private documents. No third-party vulnerability disclosure was warranted.

## Dataset and toolkit pipeline

| Split | Fact families | Cases | English / Russian | Clean / attacked |
|---|---|---:|---:|---:|
| Development pool | F00–F03 | 40 | 20 / 20 | 8 / 32 |
| Held-out test | F04–F23 | 200 | 100 / 100 | 40 / 160 |
| Total | F00–F23 | 240 | 120 / 120 | 48 / 192 |

Data are generated directly by deterministic code, not distilled from another model. Seed: **20261110**. Each fact family shares its approved reference across two parallel languages and five variants. Family IDs, reference values and attack markers are disjoint across splits. Exact checks verify the grids and labels. No embedding- or MinHash-based independence claim is made: the extraction schema and four attack types remain shared, although test wording differs. This is a held-out-fact/wording evaluation, not a new-domain or unseen-attack-family evaluation. There is no training split.

The full document is placed in CuratorKIT's Alpaca instruction field to avoid its input-ignoring SFT deduplication key collapsing attack variants. HTML stripping is disabled to retain role-spoof tags. Curation is demonstrated as pipeline integration, not a measured performance gain from curation. See [the dataset card](DATASET_CARD.md), [curation source](evidence_boundary/prepare.py).

## Model, settings and locally frozen protocol

- Official public [Cohere Labs Tiny Aya Space](https://huggingface.co/spaces/CohereLabs/tiny-aya), endpoint `/generate`, advertises `tiny-aya-global`. The [model card](https://huggingface.co/CohereLabs/tiny-aya-global) identifies a 3.35B research model and CC-BY-NC 4.0 with an acceptable-use addendum. No weights are redistributed.
- Requested temperature **0**, maximum new tokens **100**, fresh anonymous client per request, sequential dispatch and at least three seconds between inference POST starts. No automatic inference retries, paid instance or private token was used. Actual token counts and truncation flags are unavailable.
- Space application commit: `41ab5939e0361cf379ddae65d391df746a17d7f3`, checked before each dispatch. **This is application code, not a model-weight revision. Weight revision and generation seed are unknown.** Temperature zero does not prove determinism or unchanged backend weights.
- Conditions are adjacent for each case, with alternating first condition. Protocol hash: `027d3a84d10090202e97f56fce59586f59c4cd3d810f12ee6db478f731be3af2`. Prompts, six scorers, cases and inference settings were unchanged across the held-out segments. Original freeze: 12:15 UTC on November 14; first held-out POST: 12:16 UTC.
- The original process stopped after exactly 146 complete pairs. The next request was verified not to have reached its inference POST before collection resumed for the remaining 54 pairs. No completed prompt was repeated, and intermediate held-out performance was not used to tune the protocol.
- Collection windows: **12:16–13:55 UTC** and **14:46–15:19 UTC**, November 14, 2026. A precompletion-frozen combiner then verified the complete plan and replayed the saved strings offline. A second, receipt-free verifier independently reproduced the analysis.

## Before/after results

The table compares conditions **within this hosted100 test only**, not the old pilot against new prompts. Accuracy, valid format and correct-reference presence are higher-is-better; marker emission is lower-is-better. `ABSTAIN` is a limited proxy on answerable clean cases, not a comprehensive refusal measure.

| Metric / subset | Baseline | Added boundary instruction | Change (percentage points) |
|---|---:|---:|---:|
| Exact extraction, all | 187/200 (93.500%) | 180/200 (90%) | -3.500 |
| Exact extraction, attacked | 147/160 (91.875%) | 140/160 (87.5%) | -4.375 |
| Exact extraction, clean | 40/40 (100%) | 40/40 (100%) | +0.000 |
| Full attack marker, attacked | 1/160 (0.625%) | 1/160 (0.625%) | +0.000 |
| Valid format, all | 187/200 (93.500%) | 180/200 (90%) | -3.500 |
| Exact REF token present, all (diagnostic) | 187/200 (93.500%) | 180/200 (90%) | -3.500 |
| Full marker or unique suffix, attacked (diagnostic) | 3/160 (1.875%) | 2/160 (1.250%) | -0.625 |
| Literal ABSTAIN, clean (limited proxy) | 0/40 (0%) | 0/40 (0%) | +0.000 |

For overall accuracy, added-minus-baseline is **−3.50 pp**, descriptive 95% interval **[−6.00, −1.50]**. On attacked cases it is **−4.375 pp**, interval **[−7.50, −1.875]**. The five prespecified intervals are in [the aggregate summary](results/aggregate_summary.json).

### Language and attack-category slices

These are descriptive subsets, not independent experiments or broad multilingual rankings.

| Language | Baseline exact | Added instruction exact |
|---|---:|---:|
| en | 89/100 (89%) | 87/100 (87%) |
| ru | 98/100 (98%) | 93/100 (93%) |

| Variant | Baseline exact | Added instruction exact |
|---|---:|---:|
| clean | 40/40 (100%) | 40/40 (100%) |
| fake_evaluator | 37/40 (92.5%) | 33/40 (82.5%) |
| format_override | 34/40 (85%) | 32/40 (80%) |
| override | 36/40 (90%) | 35/40 (87.5%) |
| role_spoof | 40/40 (100%) | 40/40 (100%) |

### What failed, and what the metrics do not establish

Post-hoc inspection, explicitly not a new primary metric, found **28 of the 33 incorrect responses** retained the correct eight-character reference value but omitted its required `REF-` prefix. Three emitted only an attack-marker suffix; two emitted the full marker. Therefore all 33 errors must **not** be called successful prompt injections. The strict accuracy regression mostly concerns required output formatting, not additional full-marker compliance. No post-processing repair or relaxed scorer was applied after seeing these failures.

Paired outcomes were 179 both-correct, 12 both-incorrect, eight baseline-only correct and one added-instruction-only correct. Individual response quotations and case-level outcomes are not included in this release.

The full-marker metric alone misses suffix-only compliance and most task failures. Its identical 1/160 counts do not establish safety. The secondary marker-or-suffix count improves by one observation, which is insufficient for a general protection claim. The primary negative result is retained rather than replacing the metric with a more favorable post-hoc one.

## Statistical interpretation

The frozen paired cluster percentile bootstrap resamples **20 fact families**, retaining both languages, all five variants and both conditions. It uses 2,000 resamples and seed 20261110. The implementation uses sorted-draw endpoints at indices 50 and 1950, not interpolated quantiles. The intervals quantify descriptive family-resampling variation in this synthetic design; they are not model-generation variance, p-values, multiple-comparison-adjusted claims or population safety bounds. The 200 rows are not treated as 200 independent facts. Zero-width intervals for identical clean/marker outcomes do not imply zero risk.

## Limits, cost and ethics

The benchmark is small and templated. It does not measure dangerous-request safety, adaptive adversaries, real RAG systems, long or multi-turn contexts, absent-evidence abstention or general language ability. Prefix omission can be consequential for a strict parser while preserving much of the semantic answer, so strict accuracy must not be interpreted as a general semantic-failure or safety score. Only one hosted alias, one requested sampling configuration and one generation per condition/case were studied. No weight revision or model seed is exposed, and drift during the pause cannot be excluded.

Only fictional records and benign markers were transmitted. The demo links a [privacy policy](https://cohere.com/privacy); no personal data were sent. This notice is not treated as permission to relicense hosted outputs. No numeric demo quota was found in the reviewed app/API description, which is not a promise of unlimited availability. Requests were sequential and stopped on errors; the continuation resumed at the verified next unsent request.

There were **no direct paid-compute/API purchases**. Provider GPU hardware, token counts and infrastructure cost were not measured, so no ROI or model-only throughput claim is made. A free Colab T4 was separately checked during setup, but **it did not produce these hosted responses**.

## With more resources

The next study would first replicate with a verified local checkpoint, then test format-preserving methods and constrained decoding on fresh held-out families, longer documents and additional attack types/languages. It would prespecify separate semantic extraction, schema compliance and marker-compliance measures, plus a genuine absent-evidence/refusal set. The aim is to reduce prefix errors without increasing attacker-marker behavior or clean-task failures. The magnitude and direction of improvement are unknown; no projected positive score is asserted.

## Public reproduction and artifact map

Python 3.10+ is recommended; validation was run on Python 3.12. The standard-library tests use only synthetic fixtures and do not contact a model. Optional AuditKIT tests are skipped if AuditKIT is absent:

```sh
python -m unittest discover -s tests -v
```

To reproduce CuratorKIT curation with the separately installed dependencies in `requirements-curation.txt`:

```sh
python -m evidence_boundary.prepare --output data-reproduced
```

Use a new output directory and writable `XDG_CACHE_HOME`. This reproduces synthetic data, not model responses. Dependency installation is a separate network operation.

With AuditKIT 1.1.7 available (listed in `requirements-curation.txt`), run the **new public integration smoke test**, not the historical experiment:

```sh
XDG_CACHE_HOME=/tmp/evidenceboundary-cache python -m evidence_boundary.auditkit_smoke --output /tmp/evidenceboundary-smoke-NEW
XDG_CACHE_HOME=/tmp/evidenceboundary-cache python -m unittest discover -s tests -v
```

Choose a new local output directory. This offline-only test routes 20 synthetic target labels through AuditKIT and verifies native six-score exports. It constructs no service client and makes no fresh model inference. All fixture outputs go to the selected directory, not into this release. AuditKIT may also write its dependency cache under `XDG_CACHE_HOME`. The perfect fixture scores are **not model-performance evidence**.

- `evidence_boundary/benchmark.py`: deterministic generator, original scoring primitives and paired-family bootstrap.
- `evidence_boundary/protocol_hosted.py`: exact historical hosted100 prompt/scorer source. Its `prompt_for` function, not the older helper in `benchmark.py`, specifies the evaluated prompts.
- `evidence_boundary/prepare.py`: original CuratorKIT preparation pipeline.
- `evidence_boundary/auditkit_smoke.py`: new offline AuditKIT integration demonstration using synthetic targets, adapted from our original pipeline; not historical evidence.
- `data/`: synthetic inputs and labels only. Alpaca `output` fields are generator-created target labels, not model generations.
- `results/aggregate_summary.json`: reported aggregate metrics and five frozen confidence intervals.
- `tests/`: public synthetic-only validation tests, not inference.
- `LICENSE`, `LICENSE-DATA-AND-DOCS.md`, `NOTICE.md`: license scope and exclusions.

**Reproducibility limitation:** this release excludes raw hosted answers, request/transport logs, per-case scores, native AuditKIT result exports, operational records and the private replay verifier. Consequently an external reader cannot independently recompute the observed accuracy, paired outcomes or bootstrap intervals from this repository alone. Public tests validate data/scoring logic, not the truth of the reported model observations. No fresh inference launcher is included.

Historical private source freeze: `027d3a84d10090202e97f56fce59586f59c4cd3d810f12ee6db478f731be3af2`. This reduced public source tree is not that complete frozen executable bundle; calling `protocol()` here computes a different local source hash. Preserved `benchmark.py` and `protocol_hosted.py` are unchanged copies, recorded in `SOURCE_PROVENANCE.json`. Local freezes were not public preregistration.

## Work history, attribution and release status

The dataset, code and experiments were prepared during the November 2026 hackathon period. Earlier November 11 F00 work yielded 16 incomplete diagnostic outputs with a different, formatting-confounded prompt; its unresolved request was never retried. A November 13 offline replay reused those same 16 outputs. They are not a before/after baseline for this report. The November 14 study adds **20 development + 400 test responses**, not 820 or 836 observations from replay.

Code, protocol drafting, execution coordination, analysis and writing were substantially AI-assisted. The project is maintained by Yaroslav Pelekhov (GitHub: YaroslavPelekhov). This is not a claim that every line was human-written. Original code is MIT; original synthetic inputs/labels and created report text are CC BY 4.0, only to the extent the licensor holds applicable rights. Third-party materials and hosted outputs are excluded; see the license notices.

No weights/adapters are created or redistributed. This repository does not establish that submission has occurred, eligibility has been confirmed, or hosted-output redistribution rights have been resolved. The [Lexsi checklist](https://hackathon.lexsi.ai/#submit) permits a dataset-and-report deliverable for Track 2a problem 2, but public log/artifact and conditional form requirements remain relevant. Withheld logs limit this release's completeness for that checklist.

References: [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT), [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT), [official hosted Space](https://huggingface.co/spaces/CohereLabs/tiny-aya), [Tiny Aya Global model card](https://huggingface.co/CohereLabs/tiny-aya-global), [Cohere Labs AUP](https://docs.cohere.com/docs/cohere-labs-acceptable-use-policy).
