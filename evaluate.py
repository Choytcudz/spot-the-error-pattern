"""Held-out check of the Spot the Error Pattern loop. Synthetic images only."""

import json
from pathlib import Path

from spot_error import make_scene, run

EXPECTED = {
    "clean": "accept",
    "mild_blur": "accept",
    "heavy_blur": "hold_for_human",
    "dark": "accept",
    "glare": "hold_for_human",
}


def main() -> None:
    rows = []
    for kind in EXPECTED:
        for i in range(8):
            split = "calibrate" if i < 4 else "held_out"
            # The blur cutoff was chosen from seeds in the 10_000 series.
            # Held-out images use a different seed stream.
            seed = (10_000 + i * 17) if split == "calibrate" else (80_000 + i * 13)
            result = run(make_scene(seed + len(kind), kind))
            rows.append(
                {
                    "kind": kind,
                    "split": split,
                    "expected_final": EXPECTED[kind],
                    "final_action": result["final_action"],
                    "match": result["final_action"] == EXPECTED[kind],
                    "steps": len(result["trace"]),
                    "trace": result["trace"],
                }
            )
    held = [r for r in rows if r["split"] == "held_out"]
    correct = sum(r["match"] for r in held)
    summary = {
        "opencv": rows[0]["trace"][0]["measurement"] and __import__("cv2").__version__,
        "n_held_out": len(held),
        "n_correct": correct,
        "accuracy": correct / len(held),
        "by_kind": {
            kind: {
                "correct": sum(r["match"] for r in held if r["kind"] == kind),
                "n": sum(r["kind"] == kind for r in held),
            }
            for kind in EXPECTED
        },
        "failures": [
            {"kind": r["kind"], "final_action": r["final_action"], "trace": r["trace"]}
            for r in held
            if not r["match"]
        ],
    }
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    (out / "eval.json").write_text(json.dumps(summary, indent=2))
    print(
        f"held_out {correct}/{len(held)} accuracy={summary['accuracy']:.3f} "
        f"failures={len(summary['failures'])}"
    )
    for kind, item in summary["by_kind"].items():
        print(f"  {kind}: {item['correct']}/{item['n']}")


if __name__ == "__main__":
    main()
