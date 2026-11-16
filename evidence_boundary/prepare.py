from __future__ import annotations
import argparse
from importlib.metadata import version
from pathlib import Path
from .benchmark import generate_cases, read_jsonl, sha, validate_cases, write_json, write_jsonl


def prepare(output: Path) -> dict:
    from curatorkit import Curator, CuratorConfig
    output.mkdir(parents=True, exist_ok=False)
    cases = generate_cases()
    raw = [{"instruction": c["user_prompt"], "input": "", "output": c["target"]} for c in cases]
    # Twenty-four deliberate exact duplicates test the real CuratorKIT dedup stage.
    raw += [dict(row) for row in raw[::10]]
    raw_path = output / "raw_alpaca.jsonl"
    write_jsonl(raw_path, raw)
    result = Curator(CuratorConfig(
        dataset=str(raw_path), format="alpaca", dedup="exact", clean=True,
        clean_transforms={"strip_html": False, "normalise_unicode": True,
                          "fix_encoding_artifacts": False, "collapse_whitespace": False,
                          "remove_control_chars": False},
        min_tokens=1, max_tokens=4096, export_formats=["alpaca"],
        output_dir=str(output / "curatorkit"), name="evidence_boundary_v0_1_0",
    )).run()
    # SFT dedup ignores input in this toolkit version: full document is deliberately
    # in instruction. Fail closed if any unique attack or clean control was dropped.
    expected = {(c["user_prompt"], c["target"]) for c in cases}
    actual = {(s.instruction, s.output) for s in result.passed}
    if len(result.passed) != len(cases) or actual != expected or result.rejected:
        raise RuntimeError("Curation changed/dropped unique evidence. Inspect CuratorKIT outputs; do not evaluate.")
    by_prompt = {(c["user_prompt"], c["target"]): c for c in cases}
    curated = [by_prompt[(s.instruction, s.output)] for s in result.passed]
    curated.sort(key=lambda c: c["id"])
    validate_cases(curated)
    write_jsonl(output / "cases.jsonl", curated)
    write_jsonl(output / "development.jsonl", [c for c in curated if c["split"] == "development"])
    write_jsonl(output / "test.jsonl", [c for c in curated if c["split"] == "test"])
    manifest = {
        "status": "DATASET_PREPARED_NO_MODEL_RESULTS", "synthetic_only": True,
        "raw_rows": len(raw), "unique_cases": len(curated), "exact_duplicates_removed": len(raw) - len(curated),
        "development_cases": 40, "test_cases": 200, "family_split": "F00-F03 development; F04-F23 test",
        "curatorkit_version": version("curatorkit"), "auditkit_version": version("auditkit"),
        "stage_counts": result.stage_counts,
        "raw_sha256": sha(raw_path.read_bytes()), "cases_sha256": sha((output / "cases.jsonl").read_bytes()),
        "curation_note": "HTML tags preserved; full document in instruction to prevent input-ignoring SFT dedup from collapsing attack variants.",
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(prepare(args.output))

if __name__ == "__main__":
    main()
