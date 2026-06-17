import json
import glob
import os

# -------- Heuristics -------- #

def has_multiple_options(text):
    signals = [
        "option a", "option b",
        "approach 1", "approach 2",
        "one approach", "another approach",
        "alternatively", "another option"
    ]
    count = sum(s in text for s in signals)
    return count >= 1

def has_tradeoffs(text):
    keywords = ["tradeoff", "trade-off", "vs", "versus", "however", "on the other hand", "would", "increase"]
    return any(k in text for k in keywords)

def has_decision(text):
    keywords = ["choose", "decision", "select", "reject", "chosen", "implementation"]
    return any(k in text for k in keywords)

def has_specificity(text):
    return bool(text and any(
        k in text for k in ["validation.py", "function", "helper", ".py", "def "]
    ))

def mentions_constraints(text):
    keywords = ["compatibility", "compat", "safety", "risk", "draft", "solid"]
    return any(k in text for k in keywords)

# -------- Scorer for YOUR Schema -------- #

def score_entry(entry):
    text_blob = json.dumps(entry).lower()

    scores = {}

    # Problem (not explicit, weak inference)
    scores["problem"] = 0.5 if any(k in text_blob for k in ["issue", "problem", "bug", "invalid", "error"]) else 0.0

    # Alternatives from rejected_options[]
    rejected = entry.get("rejected_options", [])
    scores["alternatives"] = 1.0 if len(rejected) >= 1 else 0.0

    # Tradeoffs from rejection reasons
    scores["tradeoffs"] = 1.0 if has_tradeoffs(text_blob) else 0.0

    # Decision from chosen_solution.implementation
    chosen = entry.get("chosen_solution", {})
    scores["decision"] = 1.0 if chosen.get("implementation") else 0.0

    # Justification from rationale
    rationale = chosen.get("rationale", "")
    scores["justification"] = 1.0 if len(rationale) > 20 else 0.5

    # Constraints from validation/compat mention
    scores["constraints"] = 1.0 if mentions_constraints(text_blob) else 0.0

    # Specificity
    scores["specificity"] = 1.0 if has_specificity(text_blob) else 0.5

    total = sum(scores.values())
    percent = (total / 7.0) * 100

    # Penalties
    if scores["tradeoffs"] == 0.0:
        percent = min(percent, 70)
    if scores["alternatives"] == 0.0:
        percent = min(percent, 60)
    if scores["specificity"] == 0.0:
        percent = min(percent, 50)

    return percent, scores

# -------- Runner -------- #

def run_benchmark(path="./critiques/decision-log-*.json"):
    files = glob.glob(path)

    print(f"Found {len(files)} files")

    results = []

    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
        except Exception as e:
            print(f"Failed to parse {f}: {e}")
            continue

        score, breakdown = score_entry(data)

        results.append({
            "file": f,
            "score": round(score, 2),
            "breakdown": breakdown
        })

    return results

# -------- Main Entry Point -------- #

if __name__ == "__main__":
    results = run_benchmark()

    if not results:
        print("No decision logs found.")
    else:
        avg = sum(r["score"] for r in results) / len(results)

        for r in results:
            print(f"{r['file']}: {r['score']}% -> {r['breakdown']}")

        print(f"\nAverage: {round(avg, 2)}%")
