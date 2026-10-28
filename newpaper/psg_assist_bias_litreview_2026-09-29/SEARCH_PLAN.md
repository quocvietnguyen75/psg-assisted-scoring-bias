# Search plan: assisted-scoring bias in sleep-scoring references

Written 29 September 2026, before any search in this review. It follows the
[literature review protocol](../plan/LITERATURE_REVIEW_PROTOCOL_2026-09-29.md),
at the "related work for a paper" depth.

## Claim to position

Editing an algorithm's pre-scoring anchors expert scorers toward it. A
reference built from such scorings inflates that algorithm's measured
accuracy relative to independent raters: human and algorithmic (PSG-IPA,
protocol 001).

## Anchor papers

Each gets a known-item check, a full-text or abstract read and citation
chasing.

| ID | Work | Why it anchors |
|---|---|---|
| A1 | Alvarez-Estevez and Rijsman, PLOS One 2022 (PSG-IPA source) | The dataset; agreement rose with assistance |
| A2 | Holm et al., J Sleep Res 2025 (World of ScoreCraft) | Scorers follow recommendations in sleep staging |
| A3 | Berzak et al., EMNLP 2016 | Anchoring in edited parser output inflates parser evaluation |
| A4 | Schroeder et al., arXiv 2025 | LLM-assisted labels inflate reported model performance |
| A5 | Automation bias in AI-assisted radiology reading (e.g., Dratsch et al., Radiology 2023; to be verified) | Clinical readers follow incorrect AI suggestions |
| A6 | Punjabi et al., Sleep 2015 (Somnolyzer computer-assisted scoring) | Edited automatic scoring in sleep validation |

## Concepts and synonyms

| Concept | Terms |
|---|---|
| C1 Pre-annotation and anchoring bias in annotation | pre-annotation, pre-labelling, machine-assisted or model-assisted annotation, correcting automatic output, anchoring |
| C2 Automation bias in clinical decision support | automation bias, overreliance, incorrect AI suggestions, AI-assisted reading |
| C3 Reference-standard bias in diagnostic accuracy | incorporation bias, imperfect reference standard, review bias, QUADAS-2 |
| C4 Semi-automatic sleep scoring and autoscoring validation | computer-assisted or semi-automatic scoring, manual editing, Somnolyzer, EnsoSleep, Michele, FDA 510(k) |
| C5 Multi-scorer references in sleep AI evaluation | inter-scorer variability, consensus scoring, hypnodensity, multi-scored datasets |
| C6 Model-assisted dataset construction and evaluation circularity | model-in-the-loop data engines, pseudo-label references, self-preference, circular evaluation |

## Query families and tools

1. PubMed E-utilities: one query set per concept, with hit counts and the
   top 20 by relevance; titles screened, and abstracts fetched for kept
   records.
2. Citation chasing:
   - PubMed "cited in" links for A1, A2 and A6;
   - Semantic Scholar or OpenAlex for A3 and A4 (rate-limited; retries
     logged).
3. Web search for C1, C3 and C6 in NLP, computer vision and ML venues (ACL
   Anthology, arXiv, CVF), plus known-item lookups for predecessors that
   surface.
4. FDA 510(k) summaries of AI sleep-scoring devices, for how reference
   labels were built (C4).

## Stopping rule

Stop when new queries return already-recorded records. Record coverage
limits.
