# Related work: assisted-scoring bias in sleep-scoring references

Date: 29 September 2026. Run by the
[literature review protocol](../plan/LITERATURE_REVIEW_PROTOCOL_2026-09-29.md)
at "related work for a paper" depth, from a
[search plan](SEARCH_PLAN.md) written before searching.
- [PAPERS.csv](PAPERS.csv): 39 structured cards (P01-P39).
- [SEARCH_LOG.json](SEARCH_LOG.json): every query with hit counts and kept
  records.
- [references.bib](references.bib): DOIs taken from PubMed records.

Earlier screening of this candidate is in the
[novelty round](../research_selection_2026-09-26_novelty/CANDIDATES.md);
our results are in
[PSG_ASSIST_BIAS_RESULTS_001](../research_selection_2026-09-26_novelty/PSG_ASSIST_BIAS_RESULTS_001_2026-09-29.md).

## Coverage

- **32 distinct searches:**
  - 14 PubMed concept queries, with logged hit counts (9 to 495);
  - 7 known-item lookups;
  - 7 citation chases: 6 through PubMed cited-in links and 1 through
    Semantic Scholar;
  - 4 web searches.
- **Screening:** 546 PubMed titles screened and 56 abstracts read.
- **Full texts for the decisive sources (P01, P02, P04, P05, P18, P21);**
  other cards state their evidence depth.
- **Limits:**
  - Semantic Scholar and OpenAlex rate-limit anonymous use, so citation
    chasing from the NLP anchors (Berzak 2016, Schroeder 2025) is
    incomplete;
  - PubMed cited-in links miss papers that are not indexed with references
    (ScoreCraft showed 0);
  - no Scopus, Web of Science or Google Scholar; English-language sources
    only;
  - one FDA 510(k) summary inspected.

## What is known

**1. Assisted scoring raises agreement in sleep scoring, reported as a
virtue since 2010.**
- Somnolyzer's AASM validation: experts corrected 3.7-4.8% of automatic
  epochs, and two assisted scorings agreed at kappa 0.99 against 0.76 for
  two manual scorings. The authors called this "reliability close to 1"
  (P03).
- Younes et al. (P04): agreement rose from 78.9% manual to 86.5% when the
  same technologists edited an automatic scoring.
- PSG-IPA's source study (P01): kappa rose in all four tasks.
- Alvarez-Estevez and Fernandez-Varela (P05) validated an arousal detector
  against clinical references. Some had been produced by reviewing that
  detector's own output: kappa 0.600 there, against 0.559 for purely manual
  references. They had hypothesised that pre-scoring helps scorers focus,
  judged the evidence "not conclusive", and concluded the algorithm
  "behaves as one expert more".
- All four read higher agreement as reduced variability or better quality.
- Assisted use is also the intended clinical workflow of cleared software,
  whose output is "subject to verification by a qualified clinician"
  (P18).

**2. Experts follow suggestions, including wrong ones.**
- In sleep staging, incorrect recommendations cut technologists' accuracy
  by 3.3-7.3 points (P02). That study avoided a contaminated reference by
  design but did not measure what contamination does.
- In radiology, incorrect AI suggestions degrade readers at every
  experience level (P28, P31, P32).
- Systematic reviews link automation bias to verification complexity
  (P29, P30).

**3. Pre-annotation effects in text annotation are mixed and depend on
ambiguity.**
- Editing parser output anchors annotators and overestimates parser
  performance (P20). Part-of-speech pre-annotation introduces biases
  (P21), and correcting pre-tagged text halved disagreement already in the
  Penn Treebank (cited in P21).
- LLM suggestions shift labels and inflate model results on subjective
  tasks (P26).
- For low-ambiguity clinical entity tasks, pre-annotation saved time
  without detectable bias (P22, P23, P24). Those checks compared with
  pre-annotations or F-measures, not with independent raters.
- Sleep scoring is highly ambiguous: only 32-46% of epochs reach unanimous
  expert agreement (P10), and second-by-second respiratory agreement is
  kappa 0.32 (P12).

**4. Reference-standard theory already names the risk.**
- Incorporation bias (P34, P35) and discrepant analysis (P33) show that a
  reference influenced by the test under evaluation inflates that test's
  accuracy.
- The concept is moving into prediction models (P37).
- Our mechanism is a behavioural variant: the reference is produced by
  experts editing the algorithm's output, rather than formally including
  it.

**5. Model-assisted labels are now common in medical AI datasets.**
- AI-collaborative CT labelling was judged high-quality by a blinded grader,
  while its authors noted that edited labels "may be prone to automation
  bias" (P38).
- AbdomenAtlas built 673,000 masks by radiologists revising AI output
  (P39).

## What is not known, and our contribution

No inspected source tests whether the higher agreement of assisted
references reflects convergence on the assisting algorithm rather than
better accuracy. That test needs paired manual and assisted scorings by the
same experts, the algorithm's raw pre-fill, and independent raters, and no
inspected source measures the resulting evaluation inflation.

Contribution sentence, in the strategy's template:

> Prior work establishes that editing automatic output raises inter-scorer
> agreement in sleep scoring (P01, P03, P04) and that annotators anchor on
> suggestions (P02, P20, P26). We test whether that agreement reflects the
> assisting algorithm, which matters because AI sleep scorers are validated
> against expert references, and some references are produced by editing
> automatic output (P05, P18). We use paired manual, assisted and pre-fill
> scorings by 12 experts (PSG-IPA), with independent human raters and an
> independent algorithm (YASA), to distinguish it from the explanation that
> assistance simply improved accuracy.

## Misreading audit

| Tempting reading | What the sources actually say |
|---|---|
| "Computer-assisted manual scoring" (P08, P09) means editing a pre-fill | No. There it means manual scoring in software; the automatic scores in P08 were not edited. |
| Somnolyzer's kappa 0.99 shows superb reliability (P03) | It shows two assisted scorings converging on the same algorithm output (experts changed about 4% of epochs). |
| FDA-cleared sleep scorers are validated against assisted references | Not for EnsoSleep (P18): three independent RPSGTs, 2-of-3 majority. Only one summary was checked; do not generalise either way. |
| Pre-annotation is known to be unbiased (P22-P24) | Only for low-ambiguity text tasks, and only by criteria without independent raters. |
| Alvarez-Estevez 2019 already showed our effect (P05) | It observed higher agreement against semi-automatic references on different recordings, and read it as possibly reduced variability. There was no paired design and no independent-rater control. |
| The HMC benchmark on PhysioNet uses assisted labels | Unresolved. Its page says manual scoring; P05 shows the same clinic used semi-automatic review for some recordings; the 2021 paper does not say. Ask the authors before claiming anything. |
| Incorporation bias is exactly our mechanism | The classical definition is formal inclusion of the index test (P34). Ours is behavioural; present it as an analogue. |
| Citation counts from PubMed show a paper's reach (ScoreCraft: 0) | PubMed cited-in links are incomplete. |
| DOIs recalled from memory are reliable | Three DOIs typed from memory were wrong (P09, P33, P35) and were replaced by PubMed values before release. |

## Suggested related-work structure for the manuscript

1. Automatic and assisted scoring in sleep medicine, and how agreement
   gains have been interpreted (P01, P03-P07, P16-P18).
2. Automation bias and anchoring: clinical reading (P02, P28-P32) and
   annotation (P20-P26).
3. Reference-standard bias theory (P33-P37) and multi-scorer references for
   sleep AI (P08-P15, P19).
4. Model-assisted dataset construction (P38, P39), and why the finding
   generalises beyond sleep.

## Open items

- Ask the PSG-IPA and HMC authors how HMC reference scorings were made, and
  which algorithm versions produced the PSG-IPA pre-fills.
- Complete citation chasing from P20 and P26 with Semantic Scholar or
  OpenAlex keys, and read P03 and P25 in full if access allows.
- Check two or three more FDA 510(k) summaries (e.g., the Somnolyzer and
  MICHELE clearances) for how references were built.
- The ScoreCraft data request (with the user) would add a replication with
  known recommendation errors.
