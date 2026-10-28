# Search plan: reference standards in validations of automatic sleep scoring

Date: 29 September 2026. This is workstream 5 of the PSG assisted-scoring
study. It follows the [literature review protocol](../../research-kit/LITERATURE_REVIEW.md)
at reverse-audit depth.

**Question.** How do regulatory and published validations of automatic
sleep scoring build their reference standards? In particular, do they
report whether reference scorers worked from automatic pre-scoring?

**Why.** The manuscript argues that references made by editing an
algorithm's output are biased toward it. Its Discussion needs to say how
often validations could be affected, or would not report it.

## Sources

1. **FDA 510(k) clearances.** This is a census, not a sample: every
   clearance under product code OLZ ("Automatic Event Detection Software
   For Polysomnograph With Electroencephalograph", 21 CFR 882.1400).
   - Listed through the openFDA device API.
   - Each public summary PDF is read (`accessdata.fda.gov/cdrh_docs`).
2. **Published validations.** The validation studies already carded in the
   [related-work review](../psg_assist_bias_litreview_2026-09-29/PAPERS.csv).
   These are not searched afresh. Stated as a limit.

## Coding (per clearance)

- Whether the summary text is available.
- Whether it reports clinical performance data.
- **Reference type:**
  - `independent_experts`: experts scoring for the study, described as
    independent;
  - `expert_consensus_details_limited`;
  - `routine_clinical_scoring`: scorings made in routine care;
  - `daily_practice_panel`;
  - `not_described`;
  - `algorithm_reference`;
  - `no_new_performance_data`.
- Number of scorers and the consensus rule.
- Blinding to the device's output: explicit, stated without an object,
  implied by design, or not stated.
- A short verbatim quote.

**Scope.** Clearances from 2012 on. Earlier summaries are either not
online or contain no scoring-performance data.

## Limits, known before starting

- Summaries are abbreviated, so "not stated" means not stated in the
  summary, not absent from the submission.
- Other product codes (for example, home sleep testing) are not covered.
