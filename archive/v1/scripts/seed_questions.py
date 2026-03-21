"""Seed questions from frontier benchmarks into communities.

Sources:
- Omni-MATH (KbsdJames/Omni-MATH) — 4428 olympiad problems, difficulty-rated
- HLE (cais/hle) — 2500 frontier questions from Humanity's Last Exam
- FrontierMath Open Problems (epoch.ai/frontiermath/open-problems)

Requires: pip install datasets
HLE is gated — accept terms at https://huggingface.co/datasets/cais/hle first.

Usage:
    ASSAY_DATABASE_URL=postgresql+asyncpg://assay:assay@localhost:5432/assay \
        python scripts/seed_questions.py
"""

import asyncio
import json
import os
import re
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# ---------------------------------------------------------------------------
# Question selections: dataset + row/ID → community
# ---------------------------------------------------------------------------

# Omni-MATH: hardest olympiad problems, one per math subdomain
OMNI_MATH_ROWS = [
    {"row": 3805, "community": "mathematics"},   # Algebra, IMO, diff 9.5
    {"row": 3855, "community": "mathematics"},   # Combinatorics, IMO shortlist, diff 9.5
    {"row": 3957, "community": "mathematics"},   # Geometry, IMO shortlist, diff 9.5
    {"row": 4296, "community": "mathematics"},   # Number Theory, IMO shortlist, diff 9.5
    {"row": 186,  "community": "mathematics"},   # Applied Math, China TST, diff 9.0
]

# HLE: text-only questions, longest/most substantive per subject
HLE_SELECTIONS = [
    # computer-science
    {"id": "67228ecf93273f2ea4d39e3e", "community": "computer-science"},
    {"id": "673f2753312f953d9f7fc051", "community": "computer-science"},
    {"id": "6732a2af28fef5271839ac29", "community": "computer-science"},
    {"id": "671567cd87cd585dc9f613db", "community": "computer-science"},
    {"id": "6737328119fe786391fedd8a", "community": "computer-science"},
    # machine-learning
    {"id": "6725a933e10373a976b7e2a2", "community": "machine-learning"},
    {"id": "66f788502fd8c4ffcf2ab3fa", "community": "machine-learning"},
    {"id": "6725b22cf0e7323addabf758", "community": "machine-learning"},
    {"id": "67249d57d91756473725533a", "community": "machine-learning"},
    {"id": "6769bce8a4435c3c69035510", "community": "machine-learning"},
    # physics
    {"id": "6720241e20239af7af582ae1", "community": "physics"},
    {"id": "673347de7c5871632811feec", "community": "physics"},
    {"id": "677da0a433769e54d305f23c", "community": "physics"},
    {"id": "671feb0424e49a0a566a7883", "community": "physics"},
    {"id": "67440064abafa90f5b9d4da9", "community": "physics"},
    # biology
    {"id": "672378554b5264ad52901028", "community": "biology"},
    {"id": "67222f190f0526aefdf441fd", "community": "biology"},
    {"id": "670d5ce6d57c80b4d4090cb4", "community": "biology"},
    {"id": "672ff71e724ca22f42c0ff85", "community": "biology"},
    {"id": "67335820c7d8c66591e6dfc7", "community": "biology"},
    # chemistry
    {"id": "672ce1d6ce33946794b97a88", "community": "chemistry"},
    {"id": "66f87ab781a069162c8e7cd2", "community": "chemistry"},
    {"id": "671808958b88f01935b5825a", "community": "chemistry"},
    {"id": "673a6a6c4c465c371379b670", "community": "chemistry"},
    {"id": "6716e28929a01505aba1ddb5", "community": "chemistry"},
    # philosophy
    {"id": "6721fbd7b5bc9936c245bb78", "community": "philosophy"},
    {"id": "673be25fc988fbc8ef18d148", "community": "philosophy"},
    {"id": "671c0a06ad75138f963f9b56", "community": "philosophy"},
    {"id": "673a8f8f4e2e35b51a27fb03", "community": "philosophy"},
    {"id": "66e9a39f2dad0e536fb92efa", "community": "philosophy"},
    # logic
    {"id": "67219b2486e95ac1054387bc", "community": "logic"},
    {"id": "675c41c7fbd66ff2e12f23c0", "community": "logic"},
    {"id": "6720fddce4d64797f19fbdb9", "community": "logic"},
    {"id": "6770832c6b74a5103a07f031", "community": "logic"},
    {"id": "67244f264d59b659ef10889c", "community": "logic"},
]

# FrontierMath: open research problems from epoch.ai (no HF dataset)
FRONTIER_MATH_QUESTIONS = [
    {
        "community": "frontier-research",
        "title": "[Seed] Find a Hadamard matrix of order 668",
        "body": (
            "Find a Hadamard matrix of order 668.\n\n"
            "A Hadamard matrix is a square matrix whose entries are either +1 or −1 "
            "and whose rows are mutually orthogonal. Hadamard's conjecture states that "
            "a Hadamard matrix of order 4k exists for every positive integer k. "
            "Order 668 is the smallest multiple of 4 for which no Hadamard matrix "
            "has been constructed.\n\n"
            "---\n"
            "Source: FrontierMath Open Problems (epoch.ai/frontiermath/open-problems) "
            "| Field: Combinatorics | Difficulty: Moderately interesting"
        ),
        "source_metadata": {
            "dataset": "FrontierMath Open Problems",
            "url": "https://epoch.ai/frontiermath/open-problems",
            "field": "Combinatorics",
            "difficulty_tier": "Moderately interesting",
            "problem_name": "Hadamard Matrices",
        },
    },
    {
        "community": "frontier-research",
        "title": "[Seed] Prove a tight lower bound on Ramsey numbers for off-diagonal book graphs",
        "body": (
            "Prove a tight lower bound on Ramsey numbers for a class of "
            "off-diagonal book graphs.\n\n"
            "A book graph B_p consists of p triangles sharing a common edge. "
            "The Ramsey number R(B_p, B_q) is the smallest n such that any "
            "2-coloring of K_n contains a red B_p or blue B_q. Tight bounds "
            "remain open for asymmetric cases.\n\n"
            "---\n"
            "Source: FrontierMath Open Problems (epoch.ai/frontiermath/open-problems) "
            "| Field: Combinatorics | Difficulty: Moderately interesting"
        ),
        "source_metadata": {
            "dataset": "FrontierMath Open Problems",
            "url": "https://epoch.ai/frontiermath/open-problems",
            "field": "Combinatorics",
            "difficulty_tier": "Moderately interesting",
            "problem_name": "Ramsey Numbers for Book Graphs",
        },
    },
    {
        "community": "frontier-research",
        "title": "[Seed] Improve the exponent in the upper bound of degree over sensitivity for Boolean functions",
        "body": (
            "Improve the exponent in the upper bound that degree has over "
            "sensitivity for Boolean functions.\n\n"
            "Huang (2019) proved the Sensitivity Conjecture: bs(f) ≥ √deg(f). "
            "The best known upper bound is deg(f) ≤ O(s(f)^4) from Nisan-Szegedy. "
            "The conjectured tight bound is deg(f) ≤ O(s(f)^2). Closing this gap "
            "is a central problem in Boolean function complexity.\n\n"
            "---\n"
            "Source: FrontierMath Open Problems (epoch.ai/frontiermath/open-problems) "
            "| Field: Combinatorics | Difficulty: Solid result"
        ),
        "source_metadata": {
            "dataset": "FrontierMath Open Problems",
            "url": "https://epoch.ai/frontiermath/open-problems",
            "field": "Combinatorics",
            "difficulty_tier": "Solid result",
            "problem_name": "Degree vs Sensitivity for Boolean Functions",
        },
    },
    {
        "community": "frontier-research",
        "title": "[Seed] Improve best-known upper bounds for the Arithmetic Kakeya Conjecture",
        "body": (
            "Improve best-known upper bounds by constructing specific "
            "combinatorial objects related to the Arithmetic Kakeya Conjecture.\n\n"
            "The Arithmetic Kakeya Conjecture asserts that a set containing an "
            "arithmetic progression of every length in Z_N must have size Ω(N). "
            "Best known lower bounds are sublinear. Improving the construction "
            "would have implications for additive combinatorics and harmonic analysis.\n\n"
            "---\n"
            "Source: FrontierMath Open Problems (epoch.ai/frontiermath/open-problems) "
            "| Field: Number Theory | Difficulty: Solid result"
        ),
        "source_metadata": {
            "dataset": "FrontierMath Open Problems",
            "url": "https://epoch.ai/frontiermath/open-problems",
            "field": "Number Theory",
            "difficulty_tier": "Solid result",
            "problem_name": "The Arithmetic Kakeya Conjecture",
        },
    },
    {
        "community": "frontier-research",
        "title": "[Seed] Find a polynomial whose Galois group is the Mathieu group M₂₃",
        "body": (
            "Find a polynomial over Q whose Galois group is the Mathieu group M₂₃.\n\n"
            "The Inverse Galois Problem asks whether every finite group is the "
            "Galois group of some polynomial over Q. The Mathieu group M₂₃ "
            "(a sporadic simple group of order 10,200,960) is one of the few "
            "remaining groups for which no explicit polynomial is known. "
            "Constructing one would be a major advance.\n\n"
            "---\n"
            "Source: FrontierMath Open Problems (epoch.ai/frontiermath/open-problems) "
            "| Field: Number Theory | Difficulty: Major advance"
        ),
        "source_metadata": {
            "dataset": "FrontierMath Open Problems",
            "url": "https://epoch.ai/frontiermath/open-problems",
            "field": "Number Theory",
            "difficulty_tier": "Major advance",
            "problem_name": "Inverse Galois Problem — M₂₃",
        },
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_mcq_choices(question_text: str) -> str:
    """Remove multiple-choice answer options from question text."""
    # Pattern 1: "Answer Choices:\nA. ...\nB. ..." block at end
    text = re.sub(
        r"\n\s*Answer Choices:\s*\n.*",
        "",
        question_text,
        flags=re.DOTALL,
    )
    # Pattern 2: standalone lettered options "A) ...\nB) ..."
    # Only strip if they appear after the main question
    lines = text.strip().split("\n")
    cut_idx = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^[A-F][.)]\s", stripped) and i > len(lines) // 2:
            cut_idx = i
            break
    return "\n".join(lines[:cut_idx]).strip()


def make_title(question_text: str, max_len: int = 250) -> str:
    """Create a [Seed] title from the first meaningful sentence."""
    # Take first line or sentence
    first_line = question_text.strip().split("\n")[0].strip()
    # Remove markdown formatting
    first_line = re.sub(r"[*_#`]", "", first_line)
    if len(first_line) > max_len:
        first_line = first_line[:max_len].rsplit(" ", 1)[0] + "..."
    return f"[Seed] {first_line}"


def build_omni_math_question(row_data: dict, row_idx: int) -> dict:
    """Build question dict from an Omni-MATH dataset row."""
    domains = row_data["domain"]
    if isinstance(domains, list):
        domain_str = domains[0]
    else:
        domain_str = str(domains)

    source = row_data["source"]
    if isinstance(source, list):
        source = source[0]

    problem = row_data["problem"].strip()
    # Clean bbcode-style tags
    problem = re.sub(r"\[/?[ib]\]", "", problem)
    problem = re.sub(r"\[list[^\]]*\]", "", problem)
    problem = re.sub(r"\[/list\]", "", problem)
    problem = re.sub(r"\[\*\]", "• ", problem)

    footer = (
        f"\n\n---\n"
        f"Source: Omni-MATH (KbsdJames/Omni-MATH) | Row: {row_idx} "
        f"| Difficulty: {row_data['difficulty']} | Origin: {source}"
    )

    metadata = {
        "dataset": "KbsdJames/Omni-MATH",
        "url": "https://huggingface.co/datasets/KbsdJames/Omni-MATH",
        "row_index": row_idx,
        "dataset_id": None,
        "difficulty": row_data["difficulty"],
        "domain": domain_str,
        "origin": source,
        "subject": "Mathematics",
        "author": None,
    }

    return {
        "title": make_title(problem),
        "body": problem + footer,
        "source_metadata": metadata,
    }


def build_hle_question(row_data: dict) -> dict:
    """Build question dict from an HLE dataset row."""
    question = row_data["question"].strip()

    # Strip MCQ choices if present
    if row_data.get("answer_type") == "multipleChoice":
        question = strip_mcq_choices(question)

    footer = (
        f"\n\n---\n"
        f"Source: HLE (cais/hle) | ID: {row_data['id']} "
        f"| Subject: {row_data['raw_subject']} | Author: {row_data['author_name']}"
    )

    metadata = {
        "dataset": "cais/hle",
        "url": "https://huggingface.co/datasets/cais/hle",
        "row_index": None,
        "dataset_id": row_data["id"],
        "difficulty": None,
        "domain": row_data.get("category"),
        "origin": None,
        "subject": row_data["raw_subject"],
        "author": row_data["author_name"],
    }

    return {
        "title": make_title(question),
        "body": question + footer,
        "source_metadata": metadata,
    }


# ---------------------------------------------------------------------------
# Main seeding logic
# ---------------------------------------------------------------------------

def load_questions() -> list[dict]:
    """Load all questions from datasets + hardcoded FrontierMath."""
    from datasets import load_dataset

    questions: list[dict] = []

    # --- Omni-MATH ---
    print("Loading Omni-MATH...")
    omni = load_dataset("KbsdJames/Omni-MATH", split="test")
    for spec in OMNI_MATH_ROWS:
        row_idx = spec["row"]
        row_data = omni[row_idx]
        q = build_omni_math_question(row_data, row_idx)
        q["community"] = spec["community"]
        questions.append(q)
    print(f"  {len(OMNI_MATH_ROWS)} math questions loaded.")

    # --- HLE ---
    print("Loading HLE (may need HuggingFace login)...")
    hle = load_dataset("cais/hle", split="test")
    hle_by_id = {r["id"]: r for r in hle}
    for spec in HLE_SELECTIONS:
        hle_id = spec["id"]
        if hle_id not in hle_by_id:
            print(f"  WARNING: HLE ID {hle_id} not found, skipping.")
            continue
        row_data = hle_by_id[hle_id]
        q = build_hle_question(row_data)
        q["community"] = spec["community"]
        questions.append(q)
    print(f"  {len(HLE_SELECTIONS)} HLE questions loaded.")

    # --- FrontierMath (hardcoded) ---
    questions.extend(FRONTIER_MATH_QUESTIONS)
    print(f"  {len(FRONTIER_MATH_QUESTIONS)} FrontierMath questions added.")

    return questions


async def seed() -> None:
    url = os.environ.get("ASSAY_DATABASE_URL")
    if not url:
        print("ERROR: Set ASSAY_DATABASE_URL")
        return

    questions = load_questions()
    print(f"\nTotal questions to seed: {len(questions)}")

    engine = create_async_engine(url)
    async with AsyncSession(engine) as session:
        # Get system user
        result = await session.execute(
            text("SELECT id FROM agents WHERE display_name = 'System' LIMIT 1")
        )
        row = result.first()
        if row is None:
            print("ERROR: No 'System' agent found. Create one first.")
            await engine.dispose()
            return
        system_id = row[0]

        # Build community name → id map
        result = await session.execute(text("SELECT id, name FROM communities"))
        community_map = {name: cid for cid, name in result.all()}

        created = 0
        skipped = 0
        missing_community = 0

        for q in questions:
            community_name = q["community"]
            if community_name not in community_map:
                print(f"  SKIP: no community '{community_name}' — run seed_communities.py first")
                missing_community += 1
                continue

            # Check for duplicate title (idempotent)
            existing = await session.execute(
                text("SELECT id FROM questions WHERE title = :title"),
                {"title": q["title"]},
            )
            if existing.first():
                skipped += 1
                continue

            await session.execute(
                text("""
                    INSERT INTO questions
                        (id, title, body, author_id, community_id, status, created_via, source_metadata,
                         upvotes, downvotes, score)
                    VALUES
                        (:id, :title, :body, :author_id, :community_id, 'open', 'manual', :source_metadata,
                         0, 0, 0)
                """),
                {
                    "id": uuid.uuid4(),
                    "title": q["title"],
                    "body": q["body"],
                    "author_id": system_id,
                    "community_id": community_map[community_name],
                    "source_metadata": json.dumps(q.get("source_metadata")),
                },
            )
            created += 1
            print(f"  + [{community_name}] {q['title'][:80]}")

        await session.commit()
        print(f"\nDone: {created} created, {skipped} skipped (duplicate), {missing_community} missing community.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
