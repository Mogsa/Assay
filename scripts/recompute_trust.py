#!/usr/bin/env python3
"""Recompute agent trust scores from human calibration data.

For each agent, computes MAE against the human rater across co-rated items,
then sets trust_score = 1 / (1 + MAE_avg). Finally recomputes frontier scores
for all rated items using the updated trust weights.

Usage:
    ASSAY_DATABASE_URL=postgresql+asyncpg://assay:assay@localhost:5432/assay \
        python scripts/recompute_trust.py
"""

from __future__ import annotations

import math
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# DB setup — sync engine from ASSAY_DATABASE_URL (swap asyncpg → psycopg2)
# ---------------------------------------------------------------------------

ASYNC_URL = os.environ.get(
    "ASSAY_DATABASE_URL",
    "postgresql+asyncpg://assay:assay@localhost:5432/assay",
)
SYNC_URL = ASYNC_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(SYNC_URL)


# ---------------------------------------------------------------------------
# Frontier score formula (duplicated from routers/ratings.py to avoid
# importing async app code into a sync script)
# ---------------------------------------------------------------------------

def compute_frontier_score(r: float, n: float, g: float) -> float:
    """Signed Euclidean distance: dist_to_worst - dist_to_ideal."""
    dist_to_ideal = math.sqrt((5 - r) ** 2 + (5 - n) ** 2 + (5 - g) ** 2)
    dist_to_worst = math.sqrt((r - 1) ** 2 + (n - 1) ** 2 + (g - 1) ** 2)
    return float(dist_to_worst - dist_to_ideal)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

AXES = ("rigour", "novelty", "generativity")


def main() -> None:
    with Session(engine) as db:
        # 1. Find the human user
        human = db.execute(
            text("SELECT id, display_name FROM agents WHERE kind = 'human' LIMIT 1")
        ).fetchone()

        if human is None:
            print("No human user found (kind='human'). Nothing to calibrate against.")
            sys.exit(1)

        human_id = human[0]
        print(f"Human calibrator: {human[1]} ({human_id})\n")

        # 2. Get all human ratings keyed by (target_type, target_id)
        human_ratings_rows = db.execute(
            text("""
                SELECT target_type, target_id, rigour, novelty, generativity
                FROM ratings
                WHERE rater_id = :hid
            """),
            {"hid": human_id},
        ).fetchall()

        if not human_ratings_rows:
            print("Human has no ratings. Nothing to calibrate.")
            sys.exit(1)

        human_ratings: dict[tuple[str, str], tuple[int, int, int]] = {}
        for row in human_ratings_rows:
            key = (row[0], str(row[1]))
            human_ratings[key] = (row[2], row[3], row[4])

        print(f"Human ratings: {len(human_ratings)} items\n")

        # 3. Get all agent ratings for items the human also rated
        agents_info: dict[str, dict] = {}  # agent_id -> {name, errors_r, errors_n, errors_g}
        agent_ratings_rows = db.execute(
            text("""
                SELECT r.rater_id, a.display_name,
                       r.target_type, r.target_id,
                       r.rigour, r.novelty, r.generativity
                FROM ratings r
                JOIN agents a ON a.id = r.rater_id
                WHERE a.kind = 'agent'
            """),
        ).fetchall()

        for row in agent_ratings_rows:
            agent_id = str(row[0])
            agent_name = row[1]
            key = (row[2], str(row[3]))

            if key not in human_ratings:
                continue

            if agent_id not in agents_info:
                agents_info[agent_id] = {
                    "name": agent_name,
                    "errors_r": [],
                    "errors_n": [],
                    "errors_g": [],
                }

            hr, hn, hg = human_ratings[key]
            agents_info[agent_id]["errors_r"].append(abs(row[4] - hr))
            agents_info[agent_id]["errors_n"].append(abs(row[5] - hn))
            agents_info[agent_id]["errors_g"].append(abs(row[6] - hg))

        if not agents_info:
            print("No co-rated items between human and agents. Nothing to compute.")
            sys.exit(1)

        # 4. Compute MAE and trust, update DB
        print(f"{'Agent':<16} {'MAE(R)':>7} {'MAE(N)':>7} {'MAE(G)':>7} {'MAE_avg':>8} {'Trust':>6} {'N':>4}")
        print("-" * 62)

        for agent_id, info in sorted(agents_info.items(), key=lambda x: x[1]["name"]):
            n = len(info["errors_r"])
            mae_r = sum(info["errors_r"]) / n
            mae_n = sum(info["errors_n"]) / n
            mae_g = sum(info["errors_g"]) / n
            mae_avg = (mae_r + mae_n + mae_g) / 3
            trust = 1.0 / (1.0 + mae_avg)

            print(
                f"{info['name']:<16} {mae_r:>7.2f} {mae_n:>7.2f} {mae_g:>7.2f} "
                f"{mae_avg:>8.2f} {trust:>6.3f} {n:>4}"
            )

            db.execute(
                text("UPDATE agents SET trust_score = :ts WHERE id = :aid"),
                {"ts": trust, "aid": agent_id},
            )

        db.commit()
        print(f"\nUpdated trust_score for {len(agents_info)} agents.")

        # 5. Recompute frontier scores for all rated items
        print("\nRecomputing frontier scores...")

        # Get distinct (target_type, target_id) pairs from ratings
        targets = db.execute(
            text("SELECT DISTINCT target_type, target_id FROM ratings")
        ).fetchall()

        updated = 0
        for target_type, target_id in targets:
            # Trust-weighted mean
            row = db.execute(
                text("""
                    SELECT
                        SUM(r.rigour * a.trust_score) / NULLIF(SUM(a.trust_score), 0),
                        SUM(r.novelty * a.trust_score) / NULLIF(SUM(a.trust_score), 0),
                        SUM(r.generativity * a.trust_score) / NULLIF(SUM(a.trust_score), 0)
                    FROM ratings r
                    JOIN agents a ON a.id = r.rater_id
                    WHERE r.target_type = :tt AND r.target_id = :tid
                """),
                {"tt": target_type, "tid": target_id},
            ).fetchone()

            if row is None or row[0] is None:
                continue

            score = compute_frontier_score(float(row[0]), float(row[1]), float(row[2]))

            if target_type == "question":
                db.execute(
                    text("UPDATE questions SET frontier_score = :fs WHERE id = :tid"),
                    {"fs": score, "tid": target_id},
                )
            elif target_type == "answer":
                db.execute(
                    text("UPDATE answers SET frontier_score = :fs WHERE id = :tid"),
                    {"fs": score, "tid": target_id},
                )
            updated += 1

        db.commit()
        print(f"Recomputed frontier scores for {updated} items.")


if __name__ == "__main__":
    main()
