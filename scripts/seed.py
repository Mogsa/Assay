#!/usr/bin/env python3
"""Seed Assay with default communities.

Usage:
    ASSAY_KEY=<api-key> python scripts/seed.py [base_url]

Idempotent — safe to run multiple times (409 = already exists).
"""

import os
import sys

import httpx

COMMUNITIES = [
    ("programming", "Programming", "Software engineering, languages, tools, architecture"),
    ("math", "Mathematics", "Pure math, applied math, proofs, puzzles"),
    ("physics", "Physics", "Classical, quantum, astrophysics, thermodynamics"),
    ("chemistry", "Chemistry", "Organic, inorganic, biochemistry"),
    ("logic", "Logic", "Formal logic, set theory, computability"),
    ("philosophy", "Philosophy", "Epistemology, ethics, metaphysics, philosophy of mind"),
    ("debate", "Debate", "Structured arguments on any topic, devil's advocate welcome"),
    ("open-problems", "Open Problems", "Unsolved questions in any field, speculative answers encouraged"),
    ("meta", "Meta", "About Assay itself — feature requests, bug reports, discussion"),
    ("general", "General", "Anything that doesn't fit elsewhere"),
]


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    api_key = os.environ.get("ASSAY_KEY")
    if not api_key:
        print("ERROR: ASSAY_KEY environment variable is required")
        sys.exit(1)

    url = f"{base_url.rstrip('/')}/api/v1/communities"
    headers = {"Authorization": f"Bearer {api_key}"}

    created = 0
    skipped = 0
    errors = 0

    with httpx.Client(timeout=30) as client:
        for name, display_name, description in COMMUNITIES:
            payload = {
                "name": name,
                "display_name": display_name,
                "description": description,
            }
            resp = client.post(url, json=payload, headers=headers)

            if resp.status_code == 201:
                print(f"  CREATED  {name}")
                created += 1
            elif resp.status_code == 409:
                print(f"  EXISTS   {name}")
                skipped += 1
            else:
                print(f"  ERROR    {name} — {resp.status_code}: {resp.text}")
                errors += 1

    print(f"\nDone: {created} created, {skipped} already existed, {errors} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
