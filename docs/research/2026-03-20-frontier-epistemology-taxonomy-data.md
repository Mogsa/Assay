# Frontier Epistemology: 50-Field Taxonomy Data

**Date:** 2026-03-20
**Context:** Cross-disciplinary analysis of how 50 academic/competitive fields define, detect, and contest their frontiers. Three axes scored 1-10 for each field. Data used to generate interactive 2D/3D scatter plots showing clustering patterns.

## Axes

**Objectivity (O):** How contested is the determination of what's "frontier"? 
- 10 = near-absolute (mathematics: you proved it or you didn't)
- 1 = maximally contested (visual art: the most contested frontier of any field)

**Cumulativity (C):** Does new work supersede old, or coexist with it?
- 10 = maximally cumulative (mathematics: Euclid's proofs still valid, nothing superseded)
- 1 = non-cumulative (visual art: figurative painting not superseded by abstraction, movements coexist)

**Epistemological Grounding (E):** What anchors frontier claims? How strong is the evidence basis?
- 10 = logical necessity (mathematics: proof)
- 7-8 = empirical necessity (physics, chemistry: nature is the judge)
- 5-6 = empirical + interpretive (psychology, economics: data + theory)
- 3-4 = institutional consensus (sociology, political science: peer review + paradigm)
- 1-2 = aesthetic judgment (visual art, music: cultural + market + critical discourse)

## Categories

| Code | Category | Color (hex) |
|------|----------|-------------|
| 0 | Formal Sciences | #534AB7 |
| 1 | Natural Sciences | #0F6E56 |
| 2 | Medical/Health | #D85A30 |
| 3 | Social Sciences | #378ADD |
| 4 | Humanities | #D4537E |
| 5 | Arts/Creative | #BA7517 |
| 6 | Engineering | #639922 |
| 7 | Professional | #888780 |
| 8 | CS/AI | #E24B4A |
| 9 | Competitive | #5F5E5A |

## Raw Data (50 fields × 3 axes + category)

| Field | O | C | E | Category |
|-------|---|---|---|----------|
| Mathematics | 9.5 | 10 | 10 | 0 - Formal Sciences |
| Logic & Foundations | 9 | 9.5 | 9.5 | 0 - Formal Sciences |
| Statistics | 8 | 8 | 8.5 | 0 - Formal Sciences |
| Theoretical CS | 9 | 9 | 9 | 0 - Formal Sciences |
| Physics | 9 | 9 | 9 | 1 - Natural Sciences |
| Chemistry | 8.5 | 8.5 | 8.5 | 1 - Natural Sciences |
| Biology | 7.5 | 7.5 | 7.5 | 1 - Natural Sciences |
| Neuroscience | 6 | 6 | 6.5 | 1 - Natural Sciences |
| Geology | 7.5 | 8 | 7 | 1 - Natural Sciences |
| Astronomy | 8 | 8 | 7.5 | 1 - Natural Sciences |
| Ecology | 5.5 | 5 | 6 | 1 - Natural Sciences |
| Medicine | 7 | 7 | 7 | 2 - Medical/Health |
| Pharmacology | 7 | 7 | 6.5 | 2 - Medical/Health |
| Public Health | 5.5 | 5.5 | 5.5 | 2 - Medical/Health |
| Psychology | 4 | 3.5 | 4.5 | 3 - Social Sciences |
| Economics | 5 | 4 | 5.5 | 3 - Social Sciences |
| Sociology | 3.5 | 3 | 3.5 | 3 - Social Sciences |
| Anthropology | 4 | 3 | 3.5 | 3 - Social Sciences |
| Political Science | 4 | 3 | 4 | 3 - Social Sciences |
| Linguistics | 5.5 | 5 | 5.5 | 3 - Social Sciences |
| Archaeology | 6 | 6 | 5.5 | 3 - Social Sciences |
| Geography | 5 | 5 | 5 | 3 - Social Sciences |
| Philosophy | 2 | 1.5 | 2 | 4 - Humanities |
| History | 4.5 | 4 | 4 | 4 - Humanities |
| Literature | 1.5 | 1 | 1.5 | 4 - Humanities |
| Classics | 5 | 5 | 4.5 | 4 - Humanities |
| Religious Studies | 2.5 | 2 | 2 | 4 - Humanities |
| Visual Art | 1 | 1 | 1 | 5 - Arts/Creative |
| Music | 2 | 2 | 2 | 5 - Arts/Creative |
| Theatre | 1.5 | 1 | 1.5 | 5 - Arts/Creative |
| Film | 2.5 | 3 | 2.5 | 5 - Arts/Creative |
| Architecture | 5.5 | 6 | 5 | 5 - Arts/Creative |
| Dance | 1 | 1 | 1 | 5 - Arts/Creative |
| Mechanical Engineering | 8.5 | 9 | 8 | 6 - Engineering |
| Electrical Engineering | 8.5 | 9 | 8 | 6 - Engineering |
| Civil Engineering | 8.5 | 8.5 | 8 | 6 - Engineering |
| Biomedical Engineering | 7.5 | 8 | 7 | 6 - Engineering |
| Aerospace Engineering | 9 | 8.5 | 8.5 | 6 - Engineering |
| Chemical Engineering | 8.5 | 8.5 | 8 | 6 - Engineering |
| Materials Science | 8.5 | 8.5 | 8 | 6 - Engineering |
| Law | 3 | 4 | 3 | 7 - Professional |
| Business | 3 | 2.5 | 2.5 | 7 - Professional |
| Education | 3.5 | 2.5 | 3 | 7 - Professional |
| Journalism | 4 | 2 | 3 | 7 - Professional |
| CS (Systems) | 8 | 8 | 7.5 | 8 - CS/AI |
| AI / ML | 4.5 | 5 | 4 | 8 - CS/AI |
| Sports | 9.5 | 7.5 | 8 | 9 - Competitive |
| Chess | 9 | 6.5 | 7.5 | 9 - Competitive |
| Culinary Arts | 3 | 4 | 3 | 9 - Competitive |
| Esports | 7.5 | 3 | 6 | 9 - Competitive |

## Key Findings

### 1. The Diagonal
Nearly all fields fall along a strong positive diagonal in the Objectivity vs Cumulativity projection. Fields that are objective tend to be cumulative. This isn't coincidental — objectivity enables consensus on what constitutes progress, which enables accumulation.

### 2. Three Clusters
- **Hard cluster (upper-right):** Formal sciences, natural sciences, engineering. Extremely tight. These fields agree on how frontiers work: proof or experiment, cumulative, objective.
- **Soft cluster (lower-left):** Humanities and arts. Also tight — they share non-cumulative, non-objective, interpretive grounding.
- **Messy middle:** Social sciences, medicine, professional fields. Spread out, reflecting genuine internal disagreement about methodology.

### 3. AI/ML Is the Critical Anomaly
In every projection, AI/ML sits anomalously far from other technical/engineering fields. CS Systems is comfortably in the hard cluster (O=8, C=8, E=7.5). AI/ML has dropped into the social science zone (O=4.5, C=5, E=4). This is the only engineering field whose frontier-determination mechanisms resemble the humanities more than the sciences.

**Why:** AI evaluates frontier via benchmarks (pseudo-objective, gameable), scaling laws (empirical but theoretically ungrounded), human preferences (subjective), and hype cycles (market-driven). Capabilities accumulate (GPT-4 > GPT-2) but understanding does not (we don't know WHY these systems work).

### 4. The Frontier Paradox
Fields with the most objective frontiers (mathematics, physics) least often talk about what's "frontier" — it's obvious from the open problems. Fields with the least objective frontiers (art, philosophy) are the ones where "what is frontier?" is itself a central question of the discipline.

### 5. The Market Distortion
Market value correlates with frontier status in some fields (technology, engineering) and anti-correlates in others (the most commercially successful music/art is rarely the most frontier). In AI, commercial success and frontier status are currently tightly coupled, which is historically unusual for a scientific field.

### 6. Implications for Assay
AI evaluation currently uses only the methodology of the upper-right corner (benchmarks, scores, metrics from formal/natural sciences). It ignores evaluation methods from the rest of the spectrum (peer review, aesthetic judgment, institutional consensus from social sciences, humanities, and arts). Assay's multi-agent R/N/G evaluation is an attempt to import evaluation methods from across the diagonal — structured disagreement (social sciences), adversarial review (humanities), and reputation-weighted judgment (professional fields) — into a domain that currently relies only on benchmark scores.

## Prior Work

This analysis extends two established frameworks:

**Biglan (1973)** — Three-dimensional taxonomy: hard/soft, pure/applied, life/nonlife. Our Objectivity axis corresponds roughly to Biglan's hard/soft dimension. Our axes add resolution Biglan doesn't capture — he classifies AI and Physics as both "hard-applied-nonlife," missing their radically different frontier epistemologies.

**Becher & Trowler (2001)** — "Academic Tribes and Territories." Extends Biglan with convergent/divergent and urban/rural axes. Our Cumulativity axis relates to their convergent/divergent distinction. Our Grounding axis has no direct Biglan/Becher equivalent — it's about what counts as evidence, not about paradigm development or social structure.

## JSON Format (for programmatic use)

```json
[
  {"name":"Mathematics","objectivity":9.5,"cumulativity":10,"grounding":10,"category":"Formal Sciences"},
  {"name":"Logic & Foundations","objectivity":9,"cumulativity":9.5,"grounding":9.5,"category":"Formal Sciences"},
  {"name":"Statistics","objectivity":8,"cumulativity":8,"grounding":8.5,"category":"Formal Sciences"},
  {"name":"Theoretical CS","objectivity":9,"cumulativity":9,"grounding":9,"category":"Formal Sciences"},
  {"name":"Physics","objectivity":9,"cumulativity":9,"grounding":9,"category":"Natural Sciences"},
  {"name":"Chemistry","objectivity":8.5,"cumulativity":8.5,"grounding":8.5,"category":"Natural Sciences"},
  {"name":"Biology","objectivity":7.5,"cumulativity":7.5,"grounding":7.5,"category":"Natural Sciences"},
  {"name":"Neuroscience","objectivity":6,"cumulativity":6,"grounding":6.5,"category":"Natural Sciences"},
  {"name":"Geology","objectivity":7.5,"cumulativity":8,"grounding":7,"category":"Natural Sciences"},
  {"name":"Astronomy","objectivity":8,"cumulativity":8,"grounding":7.5,"category":"Natural Sciences"},
  {"name":"Ecology","objectivity":5.5,"cumulativity":5,"grounding":6,"category":"Natural Sciences"},
  {"name":"Medicine","objectivity":7,"cumulativity":7,"grounding":7,"category":"Medical/Health"},
  {"name":"Pharmacology","objectivity":7,"cumulativity":7,"grounding":6.5,"category":"Medical/Health"},
  {"name":"Public Health","objectivity":5.5,"cumulativity":5.5,"grounding":5.5,"category":"Medical/Health"},
  {"name":"Psychology","objectivity":4,"cumulativity":3.5,"grounding":4.5,"category":"Social Sciences"},
  {"name":"Economics","objectivity":5,"cumulativity":4,"grounding":5.5,"category":"Social Sciences"},
  {"name":"Sociology","objectivity":3.5,"cumulativity":3,"grounding":3.5,"category":"Social Sciences"},
  {"name":"Anthropology","objectivity":4,"cumulativity":3,"grounding":3.5,"category":"Social Sciences"},
  {"name":"Political Science","objectivity":4,"cumulativity":3,"grounding":4,"category":"Social Sciences"},
  {"name":"Linguistics","objectivity":5.5,"cumulativity":5,"grounding":5.5,"category":"Social Sciences"},
  {"name":"Archaeology","objectivity":6,"cumulativity":6,"grounding":5.5,"category":"Social Sciences"},
  {"name":"Geography","objectivity":5,"cumulativity":5,"grounding":5,"category":"Social Sciences"},
  {"name":"Philosophy","objectivity":2,"cumulativity":1.5,"grounding":2,"category":"Humanities"},
  {"name":"History","objectivity":4.5,"cumulativity":4,"grounding":4,"category":"Humanities"},
  {"name":"Literature","objectivity":1.5,"cumulativity":1,"grounding":1.5,"category":"Humanities"},
  {"name":"Classics","objectivity":5,"cumulativity":5,"grounding":4.5,"category":"Humanities"},
  {"name":"Religious Studies","objectivity":2.5,"cumulativity":2,"grounding":2,"category":"Humanities"},
  {"name":"Visual Art","objectivity":1,"cumulativity":1,"grounding":1,"category":"Arts/Creative"},
  {"name":"Music","objectivity":2,"cumulativity":2,"grounding":2,"category":"Arts/Creative"},
  {"name":"Theatre","objectivity":1.5,"cumulativity":1,"grounding":1.5,"category":"Arts/Creative"},
  {"name":"Film","objectivity":2.5,"cumulativity":3,"grounding":2.5,"category":"Arts/Creative"},
  {"name":"Architecture","objectivity":5.5,"cumulativity":6,"grounding":5,"category":"Arts/Creative"},
  {"name":"Dance","objectivity":1,"cumulativity":1,"grounding":1,"category":"Arts/Creative"},
  {"name":"Mechanical Engineering","objectivity":8.5,"cumulativity":9,"grounding":8,"category":"Engineering"},
  {"name":"Electrical Engineering","objectivity":8.5,"cumulativity":9,"grounding":8,"category":"Engineering"},
  {"name":"Civil Engineering","objectivity":8.5,"cumulativity":8.5,"grounding":8,"category":"Engineering"},
  {"name":"Biomedical Engineering","objectivity":7.5,"cumulativity":8,"grounding":7,"category":"Engineering"},
  {"name":"Aerospace Engineering","objectivity":9,"cumulativity":8.5,"grounding":8.5,"category":"Engineering"},
  {"name":"Chemical Engineering","objectivity":8.5,"cumulativity":8.5,"grounding":8,"category":"Engineering"},
  {"name":"Materials Science","objectivity":8.5,"cumulativity":8.5,"grounding":8,"category":"Engineering"},
  {"name":"Law","objectivity":3,"cumulativity":4,"grounding":3,"category":"Professional"},
  {"name":"Business","objectivity":3,"cumulativity":2.5,"grounding":2.5,"category":"Professional"},
  {"name":"Education","objectivity":3.5,"cumulativity":2.5,"grounding":3,"category":"Professional"},
  {"name":"Journalism","objectivity":4,"cumulativity":2,"grounding":3,"category":"Professional"},
  {"name":"CS (Systems)","objectivity":8,"cumulativity":8,"grounding":7.5,"category":"CS/AI"},
  {"name":"AI / ML","objectivity":4.5,"cumulativity":5,"grounding":4,"category":"CS/AI"},
  {"name":"Sports","objectivity":9.5,"cumulativity":7.5,"grounding":8,"category":"Competitive"},
  {"name":"Chess","objectivity":9,"cumulativity":6.5,"grounding":7.5,"category":"Competitive"},
  {"name":"Culinary Arts","objectivity":3,"cumulativity":4,"grounding":3,"category":"Competitive"},
  {"name":"Esports","objectivity":7.5,"cumulativity":3,"grounding":6,"category":"Competitive"}
]
```
