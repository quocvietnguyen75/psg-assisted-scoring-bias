# Pre-submission novelty re-check, 3 November 2026

Run before submission to the *Journal of Sleep Research*, after the corresponding author asked what would raise the
paper's chance of acceptance. The literature review of 29 September 2026 ([REVIEW.md](REVIEW.md)) is the baseline;
this check asks only whether anything published since then, or missed then, tests the paper's central claim (that
references built by editing an algorithm's pre-scoring favour that algorithm) or undercuts its recommendations.

## Method

OpenAlex API, 3 November 2026, no API key; the full query log with every hit is
[novelty_recheck_2026-11-03_openalex.json](novelty_recheck_2026-11-03_openalex.json), written by
[novelty_recheck_2026-11-03.py](novelty_recheck_2026-11-03.py).

1. **Forward citations**, newest first, of: the study behind the dataset (Alvarez-Estevez and Rijsman 2022, PLOS ONE,
   17 citing works), the arousal-detector validation whose clinical reference was partly reviewed detector output
   (Alvarez-Estevez et al. 2019, Sleep Medicine, doi:10.1016/j.sleep.2019.01.025, 26), World of ScoreCraft (Holm et al. 2026, JSR; 0 in OpenAlex, indexing lag)
   and the PSG-IPA dataset DOI (0).
2. **Topic searches** restricted to works from 1 January 2026: assisted scoring and reference standard; semi-automatic
   scoring agreement; validation reference-standard bias; incorporation bias; anchoring and automation bias in sleep
   staging; pre-scoring edited by technologists; "PSG-IPA"; human-in-the-loop sleep scoring.
3. **Reporting guidelines**: a search for the AI extension of STARD, prompted by an editorial that described it as in
   development.

## Results

- **No work tests the central claim.** None of the citing works or search hits compares references built from
  assisted scorings with the assisting algorithm, or uses PSG-IPA's paired manual and assisted scorings for that
  purpose. The newest works citing the dataset's study are on reduced-montage scoring, a multi-centre PSG dataset,
  RIP technology and federated learning. The newest works citing the arousal-detector validation are on arousal
  detection methods, electrodermal responses to arousals, sigma power, drowsiness and auditory stimulation.
- **Three new papers read in abstract or full text, none overlapping:**
  - BaHammam and Almarshad 2026, *Nature and Science of Sleep*, doi:10.2147/NSS.S602114: an editorial proposing
    sleep-specific reporting items for AI scoring studies (training data, number of scorers, inter-scorer agreement,
    review rules and time for algorithm-assisted scoring). Full text read: the words "reference standard", "blind" and
    "pre-scoring" do not occur; it does not ask how the reference scorings were produced. It supports the paper's
    recommendation that these items are new, and is a candidate citation.
  - SLEEP Advances 2026, doi:10.1093/sleepadvances/zpag054: models trained on quality-controlled annotations; the
    reference came from four certified scorers working independently. No overlap.
  - Eurasian Journal of Pulmonology 2026, doi:10.14744/ejp.2026.67756: Somnolyzer against two independent scorers;
    concludes that automatic scoring "may serve as a reliable first-pass analysis tool", the workflow the paper
    studies. No overlap; supports the premise.
- **STARD-AI was published and was not cited.** Sounderajah et al., *Nature Medicine* 31:3283-3289, 15 September 2025,
  doi:10.1038/s41591-025-03953-8 (Bossuyt and Collins, first authors of the cited STARD 2015 and TRIPOD+AI, are among
  its authors). Full text read (open PDF): item 18 repeats STARD 2015 item 13b ("Whether clinical information and index
  test results were available to the assessors of the reference standard"); item 12 asks "Who undertook the
  annotations for the dataset ... and how (within the same clinical context or in a post hoc fashion)"; no item asks
  whether any software pre-scored or pre-annotated the reference. The paper's two "new items" (pre-scoring by any
  software; a reference built with one algorithm's help used to judge another) therefore stand. Cited in the
  Recommendations on 3 November 2026.

- **The FDA's 2025 draft guidance, full text searched** (raised by a fidelity check of the cover letter, which had
  said that the guidance does not ask about pre-scoring). The PDF at the entry's URL (doi-less; fda.gov media
  184856) contains no occurrence of "pre-scoring", "pre-annotation", "pre-labeling" or "semi-automatic". Its
  reference-standard section asks how the reference standard was established, what data were provided to the
  clinicians who determined it, their grading and blinding protocol, and whether annotators were blinded to each
  other; its clinical-validation section asks for "blinding of the device outputs from the clinical reference
  standard determination process". It therefore does not ask specifically whether reference scorers worked from
  automatic pre-scoring by any software, although "what data are provided to these clinicians" is broad enough to
  cover it if a sponsor reads it so. The cover letter now says "neither asks specifically".

## Conclusion

The novelty claim stands as worded. One citation was missing (STARD-AI) and was added. Repeat the forward-citation and
topic searches on the submission date.
