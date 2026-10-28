# How FDA-cleared sleep-scoring software built its validation references

Date: 29 September 2026. Counts corrected on 11 October 2026, after two
authors checked the coding against every summary
([FDA_CODING_RECONCILIATION.md](FDA_CODING_RECONCILIATION.md)). This is
workstream 5 of the PSG assisted-scoring study.
- Plan: [SEARCH_PLAN.md](SEARCH_PLAN.md).
- Log: [SEARCH_LOG.json](SEARCH_LOG.json).
- Coded table with quotes: [DEVICES.csv](DEVICES.csv).
- The authors' check: [FDA_CODING_CHECK_COMPLETED.xlsx](FDA_CODING_CHECK_COMPLETED.xlsx).

## Coverage

This is a census of every 510(k) clearance under product code OLZ, the
code for automatic event-detection software for polysomnography with EEG:
- 37 clearances, from 1986 to June 2026, listed through the openFDA API;
- 25 from 2012 on, all with retrievable summaries;
- 22 of those report clinical performance data. The other three are an
  identical re-clearance, an abbreviated 510(k), and a clearance that only
  adds a change control plan (Dreem 3S, K242094).

The public summaries were read, not the full submissions, so "not stated"
means not stated in the summary. Pre-2012 clearances are out of scope: their
summaries are not online or report no scoring performance.

## Findings (the 22 clearances with performance data)

| Reference used | Clearances |
|---|---|
| Experts scoring for the study, described as independent (2-4 scorers, majority rule) | 10 |
| An expert consensus or majority, independence not described | 4 |
| Scorings made in routine clinical care | 4 |
| A panel scoring "as done in their daily practice" | 1 |
| Reference not described | 2 |
| Another cleared algorithm's unedited output | 1 |

**No summary reported whether its reference scorers had worked from
automatic pre-scoring by any software.** This includes the five that used
routine clinical scorings or daily-practice panels. In laboratories whose
software pre-scores automatically, routine scoring may be assisted, but these
summaries do not say. SOMNUM (K253390) states only that its scorers had no
access to SOMNUM's own output.

**Blinding to the device's output:**
- explicit in 1 summary (SOMNUM, K253390): the scorers worked "without access
  to SOMNUM automatic scoring output";
- implied by design in 5: the device was run separately from, or after, the
  expert scoring (four Embla and Natus summaries, whose experts marked raw
  recordings, and Nox, which ran the device after exporting the routine
  scoring);
- mentioned without saying what was blinded in 2 (EnsoSleep);
- not applicable in 1 (an algorithm reference);
- not stated in 13.

**Algorithm as comparator.** One recent clearance (Hypnos, K250851)
compared the device with another cleared algorithm's unedited output
(EnsoSleep), rather than with human scorers.

## Published validations (not searched afresh; see the related-work review)

- One large validation used references partly produced by reviewing the
  validated algorithm's own output (Alvarez-Estevez and Fernandez-Varela
  2019, P05).
- Somnolyzer's validation reported assisted agreement as reliability
  (Anderer 2010, P03).
- Multi-scorer benchmark datasets (Dreem open datasets, the AASM
  inter-scorer reliability set) were scored manually.
- Whether the widely used clinical benchmark from the PSG-IPA centre (HMC)
  used assisted scoring is unresolved, as recorded in the related-work
  review.

## What this means for the manuscript

- **What we cannot claim.** Regulatory validations do not generally use
  assisted references. Most clearances with a described reference used
  independent experts.
- **What we can claim.**
  - Provenance is under-reported: in about a third of clearances (7 of
    22), the reference was routine clinical scoring, a daily-practice
    panel, or not described at all.
  - No summary says whether the scorers worked from automatic pre-scoring
    by any software.
  - Only one summary states that they could not see the device's own
    output.

  Our results give that unreported detail a measurable consequence, and a
  simple item for reporting guidance.
