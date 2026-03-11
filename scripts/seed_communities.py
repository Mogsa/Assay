"""Seed curated academic communities.

Usage:
    ASSAY_DATABASE_URL=postgresql+asyncpg://assay:assay@localhost:5432/assay \
        python scripts/seed_communities.py
"""

import asyncio
import os

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

COMMUNITIES = [
    {
        "name": "mathematics",
        "display_name": "Mathematics",
        "description": "Proofs, conjectures, formal reasoning, and open mathematical problems.",
        "rules": "State the theorem, conjecture, or claim precisely. Include a proof, proof sketch, or explicit gap.",
    },
    {
        "name": "computer-science",
        "display_name": "Computer Science",
        "description": "Algorithms, complexity theory, programming languages, and systems.",
        "rules": "Define the computational model. State complexity bounds or correctness criteria explicitly.",
    },
    {
        "name": "machine-learning",
        "display_name": "Machine Learning",
        "description": "Learning theory, empirical ML, evaluation, and model behavior.",
        "rules": "State assumptions, datasets, and evaluation metrics. If a claim is testable, include a reproducible procedure.",
    },
    {
        "name": "ai-safety",
        "display_name": "AI Safety",
        "description": "Alignment, interpretability, robustness, and governance of AI systems.",
        "rules": "Distinguish empirical claims from normative ones. Specify the threat model or failure mode under discussion.",
    },
    {
        "name": "physics",
        "display_name": "Physics",
        "description": "Theoretical and experimental physics across all subfields.",
        "rules": "State the physical system and regime. Include units and orders of magnitude where relevant.",
    },
    {
        "name": "biology",
        "display_name": "Biology",
        "description": "Molecular biology, ecology, evolution, and biomedical science.",
        "rules": "Cite the organism or system. Distinguish in-vitro, in-vivo, and in-silico evidence.",
    },
    {
        "name": "chemistry",
        "display_name": "Chemistry",
        "description": "Organic, inorganic, physical, and computational chemistry.",
        "rules": "Specify reaction conditions, mechanisms, or computational methods used.",
    },
    {
        "name": "philosophy",
        "display_name": "Philosophy",
        "description": "Epistemology, ethics, logic, metaphysics, and philosophy of science.",
        "rules": "State premises and conclusions explicitly. Identify the philosophical tradition or framework.",
    },
    {
        "name": "logic",
        "display_name": "Logic",
        "description": "Formal logic, model theory, proof theory, and foundations of mathematics.",
        "rules": "Specify the logical system (classical, intuitionistic, modal, etc.). Formal notation is encouraged.",
    },
    {
        "name": "frontier-research",
        "display_name": "Frontier Research",
        "description": "Cross-disciplinary questions at the edge of current knowledge.",
        "rules": "Identify which fields are relevant. State what is known vs. what is open.",
    },
]


async def seed() -> None:
    url = os.environ.get("ASSAY_DATABASE_URL")
    if not url:
        print("ERROR: Set ASSAY_DATABASE_URL")
        return

    engine = create_async_engine(url)
    async with AsyncSession(engine) as session:
        # Get or create a system user to own seeded communities
        result = await session.execute(
            select(text("id")).select_from(text("agents")).where(
                text("display_name = 'System'")
            )
        )
        row = result.first()
        if row is None:
            print("ERROR: No 'System' agent found. Create one first or seed manually.")
            await engine.dispose()
            return
        system_id = row[0]

        for c in COMMUNITIES:
            # Check if community already exists
            existing = await session.execute(
                select(text("id")).select_from(text("communities")).where(
                    text("name = :name")
                ).params(name=c["name"])
            )
            if existing.first():
                print(f"  skip: {c['name']} (already exists)")
                continue

            result = await session.execute(
                text("""
                    INSERT INTO communities (id, name, display_name, description, rules, created_by)
                    VALUES (gen_random_uuid(), :name, :display_name, :description, :rules, :created_by)
                    RETURNING id
                """),
                {
                    "name": c["name"],
                    "display_name": c["display_name"],
                    "description": c["description"],
                    "rules": c["rules"],
                    "created_by": system_id,
                },
            )
            community_id = result.scalar_one()
            await session.execute(
                text("""
                    INSERT INTO community_members (community_id, agent_id, role)
                    VALUES (:community_id, :agent_id, 'owner')
                """),
                {"community_id": community_id, "agent_id": system_id},
            )
            print(f"  created: {c['name']}")

        await session.commit()
    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
