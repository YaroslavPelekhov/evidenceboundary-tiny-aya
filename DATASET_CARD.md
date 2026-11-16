# EvidenceBoundary dataset card

License: CC BY 4.0 for original synthetic inputs and labels. No model-generated responses are included.

## Purpose and source

EvidenceBoundary tests extraction from untrusted documents containing synthetic prompt injections in English and Russian. All records are fictional, produced deterministically by `evidence_boundary.benchmark.generate_cases()` with seed 20261110. The generator and protocol are AI-assisted. No private user material, human-subject data, external document corpus, or model distillation is included.

## Composition

| Split | Fact families | English | Russian | Clean | Attacks | Total |
|---|---|---:|---:|---:|---:|---:|
| Development | F00–F03 | 20 | 20 | 8 | 32 | 40 |
| Held-out test | F04–F23 | 100 | 100 | 40 | 160 | 200 |
| All | F00–F23 | 120 | 120 | 48 | 192 | 240 |

Every family has two languages and five variants: clean, instruction override, role spoofing, forged evaluator claim and format override. Each attack type has 48 cases overall. The 264-row raw Alpaca file deliberately adds 24 exact duplicates for the curation check. CuratorKIT removes those 24, leaving every unique case unchanged.

## Record fields

| Field | Type and meaning |
|---|---|
| `id` | Unique family-language-variant string |
| `family_id` | Shared fictional fact family |
| `split` | `development` or `test` |
| `language` | `en` or `ru` |
| `variant` | One of the five variants above |
| `is_attack` | Boolean; false only for clean controls |
| `question` | Request for the approved reference |
| `document` | Fictional catalog record and any appended injection |
| `user_prompt` | Question plus labeled supplied document |
| `target` | Exact required answer, `ANSWER:REF-` followed by eight uppercase hexadecimal characters |
| `attack_marker` | Harmless family-specific marker that appears in attack text |
| `source` | Generator attribution |
| `version` | Dataset version, `0.1.0` |

The full reference value and complete attack marker are not hidden from evaluators. They are labels for deterministic scoring, not secret canaries. This artifact must not be represented as a benchmark protected from future public-data contamination.

## Curation and checks

CuratorKIT 0.1.24 performs schema validation, exact deduplication, Unicode normalization and export. HTML stripping is disabled so role-spoof tags survive. The complete task/document is stored in the Alpaca instruction field to avoid collapsing cases through a deduplication key that ignores input. The project checks that every expected prompt/target pair survives and that no rejected record remains.

Exact checks cover IDs, complete language/variant grids, correct targets, marker presence and split disjointness for families, target values and markers. There is no MinHash or embedding-based independence claim. Development/test wording is varied, but the semantic task and four attack families are shared. No training split or fine-tuning experiment exists.

## Evaluation status

The November 14 v0.2-hosted100 evaluation is complete: 200 held-out cases × two conditions = 400 real hosted-model outputs, with 20 new F01 development outputs kept separate. Baseline exact accuracy is 187/200 (93.5%); the added-boundary-instruction condition is 180/200 (90.0%). Clean accuracy is 40/40 in both; full-marker emission is 1/160 attacked cases in both. A network-disabled combined AuditKIT replay and a separate stdlib-only reanalysis verify all 400 saved outputs without creating new observations. The endpoint advertises tiny-aya-global, but weights and generation seed are unknown. See the main report for the two collection segments, all frozen metrics and limitations.

The separate November 11 pilot contains 16 responses using a different prompt and an unresolved request that was never retried. Its November 13 replay uses the same 16 observations. Those historical outputs are not pooled with the new experiment. No training or model adaptation was performed.

## Intended use and limitations

Use for a narrow, reproducible extraction-boundary diagnostic and for evaluating scoring/pipeline behavior. Do not use it alone to certify model safety, compare overall language ability, estimate real-world prompt-injection risk, or infer harmless-request refusal rates. All cases are answerable; missing-evidence abstention is untested. Exact output formatting and partial marker emission can confound interpretation. Raw outputs are withheld; the public release cannot support independent response-level rescoring.

The attacks only ask for benign marker strings. No live target, operational attack, non-public vulnerability or harmful instructions are provided. No third-party responsible-disclosure action was necessary for this synthetic diagnostic.

## Reproduction and rights

Run `python -m unittest discover -s tests -v` from the repository root. With dependencies from `requirements-curation.txt`, run `python -m evidence_boundary.prepare --output data-reproduced` into a new directory. See README for limitations.

Original synthetic inputs/labels are CC BY 4.0; original software is MIT. These grants do not cover model weights, hosted responses, dependencies or third-party materials. No model outputs are present, including in the Alpaca `output` column: that column contains synthetic target labels.
