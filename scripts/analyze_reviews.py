"""
Analysis of Assay platform reviews dataset.
Run: python scripts/analyze_reviews.py /tmp/assay_reviews.json
"""

import json
import re
import sys
from collections import Counter, defaultdict


def load_reviews(path):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Rubber-stamp scoring
# ---------------------------------------------------------------------------

RUBBER_STAMP_PHRASES = [
    r"\bcorrect\b",
    r"\bwell[- ]argued\b",
    r"\bgood point\b",
    r"\bwell said\b",
    r"\bwell[- ]written\b",
    r"\bnicely done\b",
    r"\bgreat answer\b",
    r"\bgreat response\b",
    r"\bsound reasoning\b",
    r"\bsolid answer\b",
    r"\bsolid response\b",
    r"\bthis is correct\b",
    r"\bthis is accurate\b",
    r"\bthis is good\b",
    r"\bthis answer is\b",
    r"\baccurate and\b",
    r"\bcomprehensive\b",
    r"\bthis is a (strong|good|solid|excellent)\b",
    r"\bexcellent (answer|response|point)\b",
    r"\bstrong answer\b",
    r"\bwell[- ]structured\b",
    r"\bwell[- ]reasoned\b",
    r"\bwell reasoned\b",
    r"\bwell presented\b",
    r"\bthoughtful\b",
    r"\binsightful\b",
    r"\bclearly (explains|articulates|presented)\b",
    r"\bgood job\b",
]

ADVERSARIAL_PHRASES = [
    r"\bhowever\b",
    r"\bbut\b",
    r"\bfails to\b",
    r"\bmisses\b",
    r"\bneglects\b",
    r"\bignores\b",
    r"\boverlooks\b",
    r"\bincorrect\b",
    r"\bwrong\b",
    r"\bflawed\b",
    r"\bmistake\b",
    r"\berror\b",
    r"\bcontradicts\b",
    r"\bdisagree\b",
    r"\bcounter\b",
    r"\bcritique\b",
    r"\bcritical\b",
    r"\bproblem\b",
    r"\bissue\b",
    r"\blimitation\b",
    r"\bweakness\b",
    r"\bshortcoming\b",
    r"\bfallacy\b",
    r"\boverstates\b",
    r"\bunderstates\b",
    r"\bfails\b",
    r"\binaccurate\b",
    r"\bmisleading\b",
    r"\bunsubstantiated\b",
    r"\bnot supported\b",
    r"\bunsupported\b",
    r"\bchallenge\b",
    r"\bquestion\b",
    r"\bdoubt\b",
    r"\bunclear\b",
    r"\bambiguous\b",
    r"\bvague\b",
    r"\bsimplistic\b",
    r"\boversimplif\b",
    r"\breductive\b",
]

POSITIVE_VERDICTS = {"correct", "well_argued", "strong"}
NEGATIVE_VERDICTS = {"incorrect", "needs_work", "weak", "flawed"}


def classify_review(review):
    body = (review.get("body") or "").strip()
    verdict = (review.get("verdict") or "").lower()
    length = len(body)

    body_lower = body.lower()

    # Empty/placeholder
    if length == 0:
        return "EMPTY"

    stamp_hits = sum(
        1 for p in RUBBER_STAMP_PHRASES if re.search(p, body_lower)
    )
    adversarial_hits = sum(
        1 for p in ADVERSARIAL_PHRASES if re.search(p, body_lower)
    )

    # Very short: almost certainly rubber stamp or empty
    if length < 80:
        if adversarial_hits >= 2:
            return "ADVERSARIAL"
        return "RUBBER-STAMP"

    # If heavily adversarial signals and not overridden by stamp count
    if adversarial_hits >= 3 and adversarial_hits > stamp_hits:
        return "ADVERSARIAL"

    # If lots of rubber stamp phrases and short-ish
    if stamp_hits >= 2 and length < 300 and adversarial_hits < 2:
        return "RUBBER-STAMP"

    # Long reviews with adversarial signals
    if adversarial_hits >= 2 and length >= 200:
        return "ADVERSARIAL"

    # Long reviews with generic praise
    if stamp_hits >= 3 and adversarial_hits < 2:
        return "RUBBER-STAMP"

    # Default: assume substantive if long enough with little signal
    if length >= 200:
        return "SUBSTANTIVE"

    if length >= 100:
        if stamp_hits >= 2 and adversarial_hits == 0:
            return "RUBBER-STAMP"
        return "SUBSTANTIVE"

    return "RUBBER-STAMP"


def verdict_body_alignment(review):
    """Return True if verdict and body seem misaligned."""
    body = (review.get("body") or "").lower()
    verdict = (review.get("verdict") or "").lower()

    # Positive verdict but body has strong negative signals
    if verdict in ("correct", "well_argued", "strong"):
        neg_count = sum(
            1
            for p in [
                r"\bincorrect\b",
                r"\bwrong\b",
                r"\bflawed\b",
                r"\berror\b",
                r"\binaccurate\b",
                r"\bfails\b",
                r"\bmistake\b",
                r"\bmisleading\b",
            ]
            if re.search(p, body)
        )
        if neg_count >= 2:
            return True, "positive verdict but body contains strong negative language"

    # Negative verdict but body reads like generic praise
    if verdict in ("incorrect", "needs_work", "weak", "flawed"):
        pos_count = sum(
            1
            for p in [
                r"\bwell[- ]argued\b",
                r"\bgood point\b",
                r"\bcorrect\b",
                r"\baccurate\b",
                r"\bsolid\b",
                r"\bstrong\b",
            ]
            if re.search(p, body)
        )
        stamp_count = sum(
            1 for p in RUBBER_STAMP_PHRASES if re.search(p, body)
        )
        if stamp_count >= 3 and pos_count >= 2:
            return True, "negative verdict but body reads as generic praise"

    # Neutral verdict but extreme body
    # (less reliably detectable without domain knowledge)

    return False, ""


# ---------------------------------------------------------------------------
# Scoring for "best" and "worst" reviews
# ---------------------------------------------------------------------------

def quality_score(review, classification):
    """Higher = better quality review."""
    body = review.get("body") or ""
    length = len(body)
    adversarial_hits = sum(
        1 for p in ADVERSARIAL_PHRASES if re.search(p, body.lower())
    )
    # Penalise rubber stamps, reward length and adversarial signals
    if classification == "ADVERSARIAL":
        return length * 0.5 + adversarial_hits * 30
    if classification == "SUBSTANTIVE":
        return length * 0.4 + adversarial_hits * 15
    return -length  # rubber stamps: shorter = worse


def stamp_score(review):
    """Higher = worse (more rubber-stampy)."""
    body = review.get("body") or ""
    length = len(body)
    stamp_hits = sum(
        1 for p in RUBBER_STAMP_PHRASES if re.search(p, body.lower())
    )
    adversarial_hits = sum(
        1 for p in ADVERSARIAL_PHRASES if re.search(p, body.lower())
    )
    return stamp_hits * 10 - adversarial_hits * 5 - length * 0.01


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/assay_reviews.json"
    reviews = load_reviews(path)
    print(f"Loaded {len(reviews)} reviews\n")

    # Classify every review
    for r in reviews:
        r["_class"] = classify_review(r)

    # -----------------------------------------------------------------------
    # 1. Verdict distribution
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("1. VERDICT DISTRIBUTION")
    print("=" * 70)

    all_verdicts = [r.get("verdict") or "None" for r in reviews]
    verdict_counts = Counter(all_verdicts)
    print("\nOverall:")
    for v, c in verdict_counts.most_common():
        pct = 100 * c / len(reviews)
        print(f"  {v:25s} {c:4d}  ({pct:.1f}%)")

    # Per agent
    agent_verdicts = defaultdict(list)
    for r in reviews:
        agent = r.get("author") or "unknown"
        v = r.get("verdict") or "None"
        agent_verdicts[agent].append(v)

    print("\nPer-agent verdict breakdown:")
    for agent in sorted(agent_verdicts):
        counts = Counter(agent_verdicts[agent])
        total = sum(counts.values())
        breakdown = "  ".join(f"{v}:{counts[v]}" for v in sorted(counts))
        print(f"  {agent:35s}  n={total:3d}  {breakdown}")

    # -----------------------------------------------------------------------
    # 2. Classification distribution
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("2. RUBBER-STAMP DETECTION — OVERALL")
    print("=" * 70)

    class_counts = Counter(r["_class"] for r in reviews)
    for cls, cnt in class_counts.most_common():
        pct = 100 * cnt / len(reviews)
        print(f"  {cls:15s} {cnt:4d}  ({pct:.1f}%)")

    # -----------------------------------------------------------------------
    # 3. Per-agent review quality
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("3. PER-AGENT REVIEW QUALITY")
    print("=" * 70)

    agent_reviews = defaultdict(list)
    for r in reviews:
        agent = r.get("author") or "unknown"
        agent_reviews[agent].append(r)

    agent_stats = []
    for agent, rs in agent_reviews.items():
        cls_counts = Counter(r["_class"] for r in rs)
        total = len(rs)
        mean_len = sum(len(r.get("body") or "") for r in rs) / total
        pct_sub = 100 * cls_counts.get("SUBSTANTIVE", 0) / total
        pct_stamp = 100 * cls_counts.get("RUBBER-STAMP", 0) / total
        pct_adv = 100 * cls_counts.get("ADVERSARIAL", 0) / total
        pct_empty = 100 * cls_counts.get("EMPTY", 0) / total
        agent_stats.append(
            (agent, total, mean_len, pct_sub, pct_stamp, pct_adv, pct_empty)
        )

    # Sort by adversarial+substantive %
    agent_stats.sort(key=lambda x: x[3] + x[5], reverse=True)

    header = f"  {'Agent':35s} {'n':>4} {'AvgLen':>7} {'Subst%':>7} {'Stamp%':>7} {'Advers%':>8} {'Empty%':>7}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for agent, total, mean_len, pct_sub, pct_stamp, pct_adv, pct_empty in agent_stats:
        print(
            f"  {agent:35s} {total:4d} {mean_len:7.0f} {pct_sub:7.1f} {pct_stamp:7.1f} {pct_adv:8.1f} {pct_empty:7.1f}"
        )

    # Most critical reviewer
    best = max(agent_stats, key=lambda x: x[5])
    print(f"\n  Most adversarial reviewer: {best[0]} ({best[5]:.1f}% adversarial)")
    best2 = max(agent_stats, key=lambda x: x[3])
    print(f"  Most substantive reviewer: {best2[0]} ({best2[3]:.1f}% substantive)")
    worst = max(agent_stats, key=lambda x: x[4])
    print(f"  Most rubber-stampy: {worst[0]} ({worst[4]:.1f}% rubber-stamp)")

    # -----------------------------------------------------------------------
    # 4. Verdict-reasoning alignment
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("4. VERDICT-REASONING MISALIGNMENT")
    print("=" * 70)

    misaligned = []
    for r in reviews:
        flag, reason = verdict_body_alignment(r)
        if flag:
            misaligned.append((r, reason))

    print(f"\nFound {len(misaligned)} potentially misaligned reviews:\n")
    for r, reason in misaligned[:15]:
        body = (r.get("body") or "")[:200].replace("\n", " ")
        print(f"  [{reason}]")
        print(f"  Author: {r.get('author')}  Verdict: {r.get('verdict')}")
        print(f"  Q: {r.get('question_title', '')[:80]}")
        print(f"  Body: \"{body}...\"")
        print()

    # -----------------------------------------------------------------------
    # 5. Empty / test reviews
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("5. EMPTY / TEST / PLACEHOLDER REVIEWS")
    print("=" * 70)

    TEST_PATTERNS = [
        r"^test",
        r"^placeholder",
        r"^todo",
        r"^n/a",
        r"^\s*$",
        r"^\.+$",
        r"^x+$",
        r"lorem ipsum",
    ]

    empty_or_test = []
    for r in reviews:
        body = (r.get("body") or "").strip()
        if not body:
            empty_or_test.append((r, "EMPTY"))
            continue
        for p in TEST_PATTERNS:
            if re.search(p, body.lower()):
                empty_or_test.append((r, f"PATTERN:{p}"))
                break

    if empty_or_test:
        print(f"\nFound {len(empty_or_test)} empty/test reviews:")
        for r, reason in empty_or_test:
            print(
                f"  [{reason}] Author: {r.get('author')}  Verdict: {r.get('verdict')}"
            )
            print(f"  Body: \"{(r.get('body') or '')[:100]}\"")
    else:
        print("\nNone found — all reviews have content.")

    # -----------------------------------------------------------------------
    # 6. Best 5 reviews (most thorough, specific, critical)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("6. BEST 5 REVIEWS (most substantive/adversarial)")
    print("=" * 70)

    def best_key(r):
        body = r.get("body") or ""
        adv_hits = sum(1 for p in ADVERSARIAL_PHRASES if re.search(p, body.lower()))
        return len(body) * 0.4 + adv_hits * 40

    ranked = sorted(reviews, key=best_key, reverse=True)[:5]
    for i, r in enumerate(ranked, 1):
        body = r.get("body") or ""
        print(f"\n--- Best #{i} ---")
        print(f"Author: {r.get('author')}  |  Verdict: {r.get('verdict')}  |  Class: {r['_class']}")
        print(f"Question: {r.get('question_title', '')[:80]}")
        if r.get("answer_author"):
            print(f"Answer author: {r.get('answer_author')}")
        print(f"Length: {len(body)} chars")
        print(f"Review:\n\"{body[:1500]}\"")
        if len(body) > 1500:
            print(f"  ... [{len(body) - 1500} more chars]")

    # -----------------------------------------------------------------------
    # 7. Worst 10 reviews (most generic rubber stamps)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("7. WORST 10 REVIEWS (most generic rubber stamps)")
    print("=" * 70)

    def worst_key(r):
        return stamp_score(r)

    ranked_worst = sorted(reviews, key=worst_key, reverse=True)[:10]
    for i, r in enumerate(ranked_worst, 1):
        body = (r.get("body") or "").replace("\n", " ")
        print(f"\n--- Worst #{i} ---")
        print(f"Author: {r.get('author')}  |  Verdict: {r.get('verdict')}  |  Class: {r['_class']}")
        print(f"Question: {r.get('question_title', '')[:80]}")
        print(f"Length: {len(r.get('body') or '')} chars")
        print(f"Review: \"{body[:400]}\"")

    # -----------------------------------------------------------------------
    # 8. Review patterns
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("8. REVIEW PATTERNS")
    print("=" * 70)

    # Do agents tend to agree?
    # Group reviews by target_id and see verdict spread
    target_reviews = defaultdict(list)
    for r in reviews:
        tid = r.get("target_id")
        if tid:
            target_reviews[tid].append(r)

    contested = []
    for tid, rs in target_reviews.items():
        if len(rs) < 2:
            continue
        verdicts = [r.get("verdict") for r in rs]
        positive = sum(1 for v in verdicts if v in ("correct", "well_argued", "strong"))
        negative = sum(1 for v in verdicts if v in ("incorrect", "needs_work", "weak", "flawed"))
        if positive >= 1 and negative >= 1:
            contested.append((tid, rs, verdicts))

    print(f"\nTargets with split verdicts (some +ve, some -ve): {len(contested)}")
    if contested:
        print("Examples:")
        for tid, rs, verdicts in contested[:5]:
            q = rs[0].get("question_title", "?")[:60]
            print(f"  target_id={tid}  Q: {q}")
            for r in rs:
                print(f"    {r.get('author'):35s} -> {r.get('verdict')}")

    # Does any agent always give positive verdicts?
    print("\nAgents with 100% positive verdicts (positive defined as correct/well_argued/strong):")
    for agent, rs in sorted(agent_reviews.items()):
        verdicts = [r.get("verdict") for r in rs]
        pos = sum(1 for v in verdicts if v in ("correct", "well_argued", "strong"))
        if len(verdicts) >= 3 and pos == len(verdicts):
            print(f"  {agent}: {pos}/{len(verdicts)} positive")

    print("\nAgents with 100% negative verdicts:")
    for agent, rs in sorted(agent_reviews.items()):
        verdicts = [r.get("verdict") for r in rs]
        neg = sum(1 for v in verdicts if v in ("incorrect", "needs_work", "weak", "flawed"))
        if len(verdicts) >= 3 and neg == len(verdicts):
            print(f"  {agent}: {neg}/{len(verdicts)} negative")

    # Positive rate per agent
    print("\nPositive verdict rate per agent (sorted desc):")
    agent_pos = []
    for agent, rs in agent_reviews.items():
        verdicts = [r.get("verdict") for r in rs]
        total = len(verdicts)
        pos = sum(1 for v in verdicts if v in ("correct", "well_argued", "strong"))
        neg = sum(1 for v in verdicts if v in ("incorrect", "needs_work", "weak", "flawed"))
        agent_pos.append((agent, total, pos, neg, 100 * pos / total if total else 0))
    agent_pos.sort(key=lambda x: x[4], reverse=True)
    for agent, total, pos, neg, pct in agent_pos:
        bar_pos = "#" * pos
        bar_neg = "." * neg
        neutral = total - pos - neg
        bar_neu = "-" * neutral
        print(f"  {agent:35s} {pct:5.1f}% pos | {pos} pos {neg} neg {neutral} neutral  |{bar_pos}{bar_neg}{bar_neu}|")

    # Cross-agent agreement on same answer
    print(f"\nTotal targets reviewed: {len(target_reviews)}")
    multi_reviewed = {tid: rs for tid, rs in target_reviews.items() if len(rs) >= 2}
    print(f"Targets reviewed by 2+ agents: {len(multi_reviewed)}")

    agree = 0
    disagree = 0
    for tid, rs in multi_reviewed.items():
        verdicts = [r.get("verdict") for r in rs if r.get("verdict")]
        if len(verdicts) < 2:
            continue
        # All same verdict family?
        pos_count = sum(1 for v in verdicts if v in ("correct", "well_argued", "strong"))
        neg_count = sum(1 for v in verdicts if v in ("incorrect", "needs_work", "weak", "flawed"))
        if pos_count == len(verdicts) or neg_count == len(verdicts):
            agree += 1
        elif pos_count > 0 and neg_count > 0:
            disagree += 1

    if agree + disagree > 0:
        pct_agree = 100 * agree / (agree + disagree)
        print(f"Agreement rate on multi-reviewed targets: {pct_agree:.1f}% ({agree} agree, {disagree} disagree)")

    # Any agent who reviews the same agents' answers repeatedly?
    print("\nReviewer -> answer author pairing frequency (top 15):")
    pair_counts = Counter()
    for r in reviews:
        reviewer = r.get("author")
        answer_author = r.get("answer_author")
        if reviewer and answer_author and reviewer != answer_author:
            pair_counts[(reviewer, answer_author)] += 1
    for (reviewer, answer_author), cnt in pair_counts.most_common(15):
        print(f"  {reviewer:35s} reviews {answer_author:35s}  x{cnt}")

    print("\nDone.")


if __name__ == "__main__":
    main()
