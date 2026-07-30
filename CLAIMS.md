# Claims ledger

Every claim the page will make, with how we know it and how to re-check it. The point is
to make it impossible to publish something unverified by accident.

**Tiers, strongest first:**

| Tier | Meaning |
|---|---|
| **A — reproducible** | Produced by our own code. Run the script, get the number. Falsifiable by a stranger. |
| **B — read directly** | I read the primary file or code myself in this session and can quote it. |
| **C — agent-sourced** | A subagent read it and reported. Plausible, but **I have not seen the source**. |
| **D — inaccessible** | The source could not be opened. Reported from an abstract, a secondary source, or a reference list. |
| **E — inference** | Not a fact claim. An argument built on A–D facts. Must be argued, not asserted. |

**The rule: nothing at tier C or D goes on the page as a bare assertion.** Either promote it
to B by reading the source, or attribute it visibly ("Reglitz et al. report…") so the reader
knows where the weight sits.

---

## The structural risk, stated plainly

**All of our numbers are tier A. Almost none of our literature is above tier C.**

That was survivable when the audit was the headline, because the audit is entirely tier A.
It is *not* obviously survivable now that the ceiling leads, because the ceiling's second leg
— the claim that the best-evidenced enantiomer differences are potency differences — is
built almost entirely from agent reports I have not personally checked.

Four claims carry that leg. If any is wrong, the headline weakens:

1. Wine lactone spans >10⁷ in detection threshold across stereoisomers
2. Linalool is 8–10× in potency with qualities reported "very similar"
3. Carvone's spearmint/caraway quality difference is real and purity-controlled
4. Limonene's orange/lemon quality difference is refuted

**[ACTION] These four must be promoted to tier B before the ceiling can headline the page.**
That means opening the primary sources myself, not re-asking an agent.

---

## Tier A — reproducible from our own code

Run `python audit/audit.py`, `python audit/assets.py`,
`OPENPOM_CLONE=… python audit/concentration_check.py`.

| Claim | Value | Source |
|---|---|---|
| Benchmark shape | 4,983 × 140 | `audit.py` |
| SMILES column name | `nonStereoSMILES` | `audit.py` |
| Stereo characters in the whole file | 0 `@`, 0 `/`, 0 `\` | `audit.py` |
| Label count, binary, set-identical to `required_desc` | 138 | `audit.py` |
| Rows fusing ≥2 distinct stereoisomers | 534 (10.7%) | `audit.py` |
| Stereoisomers absorbed | 1,258 | `audit.py` |
| Fusions with conflicting source labels | 508 | `audit.py` |
| Fusions containing a true enantiomer pair | 87 | `audit.py` |
| …with conflicting labels | 74 | `audit.py` |
| …with both members fully stereo-specified | 71 | `audit.py` |
| Diastereomer/E-Z-only fusions | 447 | `audit.py` |
| Union-rule reconstruction | 4,983 / 4,983, 0 mismatches | `audit.py` |
| Specification breakdown | 97 fully specified / 392 mixed / 45 partly | `audit.py` |
| Fusions erasing an `odorless` member | 7 | `audit.py` |
| Rows labelled `odorless` | 200 | `audit.py` |
| Self-contradictory shipped row | menthyl lactate: `mint;cooling;odorless` | `audit.py` |
| Carvone distance matrices identical | max abs difference **exactly 0.0** | `assets.py`, asserted |
| Signed volume, carvone pair | +2.481266 / −2.481266, sums to 0 | `assets.py`, asserted |
| Figures rendering stereo | 42 SVGs: 31 wedge/hash, 2 E/Z, 9 nothing to draw | `assets.py`, asserted |
| String-replace stereo strip vs RDKit | 0 disagreements across 7,902 molecules | `audit.py` |
| Radicals in the benchmark | 6, all pre-existing metal complexes | `audit.py` |
| Source stimuli with concentration recorded | 4,137 / 4,626, 14 distinct values, 0.01%–100% | verified inline |
| Source stimuli with solvent recorded | 1,850, 9 distinct | verified inline |
| Concentration/solvent surviving into the benchmark | none | verified inline |
| Leffingwell curation reproduction | **99.97%**, 3,509 / 3,510 exact | `concentration_check.py`, asserted |
| Dilution info lost to semicolon truncation | 23 / 3,510 | `concentration_check.py` |
| Neat and diluted descriptors merged | 8 / 3,510 | `concentration_check.py` |
| Independently embedded enantiomers, same seed, matching atom order | **1.837 Å** max abs difference | `assets.py`, asserted |

---

## Tier B — I read the source myself

| Claim | Where |
|---|---|
| `ATOM_FDIM = 134` from six properties: valence, degree, num_Hs, formal charge, atomic number, hybridization | `openpom/feat/graph_featurizer.py` L27–43, read L1–115 |
| `BOND_FDIM = 6` — bond type plus `IsInRing()`, no `GetStereo()`, no `GetBondDir()` | same file, L82–110 |
| `atom_features()` makes exactly six calls, none stereo | same file, L46–79 |
| `'mint': ['cornmint', 'peppermint', 'mint', 'minty', 'spearmint']` — so `spearmint` was **merged**, not deleted | `goodcents_dataset_curation.ipynb` cell 41 |
| `caraway` appears in no merger group and not in `required_desc` — **deleted** | cells 4, 41, 45 |
| `remove_stereo()` is a raw string replace before parsing | `merge_datasets.ipynb` cell 35 |
| The flatten sits under a markdown header titled `### Handle stereo isomers` | same notebook, cell 34 |
| Cell 42 drops `odorless` when collapsing duplicates | same notebook |
| `required_desc` is hardcoded and cited to the Lee et al. POM preprint | `goodcents_dataset_curation.ipynb` cell 4 |
| `correct_spell_errors_v1` truncates at the first `;` (`#choose odor and not flavor`) | `leffingwell_dataset_curation.ipynb` cell 29 |
| Leffingwell drops `cortex`, so it uses 137 descriptors | same notebook, cell 49 |
| Pipeline unions text descriptors with a pre-existing `Labels` column | same notebook, cell 40 |
| README mentions stereochemistry nowhere | `grep -inE 'stereo\|chiral\|isomer\|limitation' README.md` → empty |
| `curated_goodcents.csv` retains stereochemistry: 524 `@`, 671 `/` | verified inline |
| `curated_leffingwell.csv` retains stereochemistry: 115 `@`, 570 `/` | verified inline |
| Carvone in `curated_goodcents.csv`: three rows, enantiomers with **different** labels | verified inline |
| OpenPOM is MIT licensed | `LICENSE` |

---

## Tier C — agent-sourced, NOT personally verified

**Do not assert these bare.** Attribute them.

| Claim | Reported source | Load-bearing for |
|---|---|---|
| Limonene: 50% vs 13% orange attribution by purity grade, >99.9% ee, 48+49 participants | Kvittingen, Sjursnes & Schmid 2021, *J. Chem. Educ.*, DOI 10.1021/acs.jchemed.1c00363 (agent read OA full text) | **§15, the single best number on the page** |
| Carvone replicated three times in 1971 | Russell & Hills *Science* 172:1043; Friedman & Miller *Science* 172:1044; Leitereg et al. *Nature* 230:455 | lead exhibit, ceiling leg 2 |
| Laska & Teubner 1999: 10 pairs, α-pinene/carvone/limonene discriminated; menthol, 2-butanol and 7 others not | *Chem. Senses* 24, 161. **Agent had abstract-level access only** | 2-butanol counter-exhibit, α-pinene exhibit, menthol demotion |
| Linalool 8–10× threshold, (S) isolated to >99.9% ee, chiral GC-O impurity screening, 17 assessors | Reglitz et al. 2023, *BrewingScience* 76, 92–97 | ceiling leg 2 |
| Wine lactone: 10⁸-fold sensitivity difference in mice matching humans | Sato et al. 2015, *Sci. Rep.* 5, 14073 (open access) | ceiling leg 2 |
| Nootkatone's (−) sample was total synthesis from (+)-sabinene, no quantified ee | Haring et al. 1972, *J. Agric. Food Chem.* | nootkatone demotion, §18 |
| Lee et al. 2023 contains zero occurrences of stereochemistry/chiral/enantiomer/isomer | PMC11898014, agent searched the text | novelty framing, §9/§10 |
| Issues are disabled on `BioMachineLearning/openpom` (`has_issues: false`) | GitHub API | novelty framing |
| Adams, Pattanaik & Coley is **ICLR 2022** and uses **torsion angles**, not signed volume | arXiv:2110.04383 | §5, §7 |
| SphereNet is SE(3)-invariant and still failed stereoisomer separation | same | §7 — the reason not to label rung 3 "SE(3)" |
| Dumitrescu et al., *E(3)-equivariant models cannot learn chirality*, ICLR 2025 | arXiv:2402.15864 | §5 primary citation |
| Tetra-DMPNN: 98–100% R/S accuracy vs exactly 50% with a plain sum aggregator | arXiv:2012.00094 | §7 |
| ChiENN locates the cause in permutation-invariant aggregation | ECML PKDD 2023, arXiv:2307.02198 | §7 |
| Union rule already published | Sanchez-Lengeling et al. 2019, arXiv:1910.10685 (agent read ar5iv mirror) | **§13 — mandatory citation** |
| Citrus peel oil is 0.03–1.6% linalool vs 38–91% limonene | Bourgou et al. 2012 | §1 |
| (S)-linalool has the highest odour-unit value of 26 components in *C. sudachi* peel | Padrayuttawat et al. 1997 (agent read scanned OCR) | §1 |
| Coriander ~88% S-linalool (76.4% ee) | Chanotiya & Yadav 2009 | §1 |
**Promoted out of this tier — and it did not survive intact.** The agent reported that
independently embedded carvone enantiomers differ by **1.11 Å**. Measured in our own code
under a fixed seed with atom ordering asserted to match: **1.837 Å**. The qualitative claim
("over 1 Å, from torsional minima rather than any failure of the theorem") holds and is now
tier A and asserted in `assets.py`. The specific figure was wrong.

This is the ledger earning its keep on the first pass. Every remaining tier-C number is a
number of exactly this kind.

---

## Tier D — could not be accessed. Handle with care or drop.

| Claim | Problem |
|---|---|
| Linalool's lavender/woody vs sweet/petitgrain pair traces to Ohloff & Klein 1962 | **Paywalled, never read.** We assert this *fails*, so the risk is asymmetric — but "it is a stereochemistry paper with no panel" is unverified |
| Steinhaus's group reports linalool qualities "very similar" | Quote provenance not confirmed by me |
| Wine lactone per-isomer threshold table | Guth 1996 paywalled; values may originate partly in a 2006 thesis |
| Bentley 2006 review | **No abstract exists** (PubMed 16967929 says so). Nothing quotable |
| Androstenone: "unnatural" enantiomers essentially odourless | Ohloff 1983 abstract only; never names which enantiomers were made; unreplicated 43 years |
| "Only ~5% of enantiomer pairs smell alike" | Source 403'd. **DO NOT CITE** |
| 7X cola formula composition | Provenance is folklore-grade (Merory 1960 / Pemberton notebook). Hedge or drop |
| Lee et al. supplementary PDF | **Download blocked. This is the open novelty gate** — until grepped, the page cannot claim the flagship paper is silent |

---

## Tier E — inferences. Argue, never assert.

| Inference | Rests on |
|---|---|
| **The ceiling**: most of the phenomenon was never expressible in the format | A (138 binary labels, no intensity dimension) + C (the potency-vs-quality literature pattern) |
| The chirality signal "died to `str.match`" | B. A characterisation of verified code — defensible, but it is rhetoric |
| Three losses attributable to distinct parties | B. Attribution is interpretation |
| The fix is "don't run one cell" | A (exact reconstruction). Strong, but "fix" implies a goal the authors may not share |
| Chirality-aware modelling on this benchmark has a low ceiling | The whole chain. **This is the thesis.** |

---

## What still needs implementing

**Verification, before any prose is written:**
- [ ] Promote the four ceiling-critical literature claims to tier B by reading primary sources myself
- [ ] Grep the Lee et al. supplementary PDF — the open novelty gate
- [ ] Move the 1.11 Å independent-embedding measurement into `assets.py` as an assertion

**Build:**
- [ ] `design.md` — how the sections look, now that contents are settled
- [ ] `site/build.py` — inline JSON, SVG, CSS, JS into one `dist/index.html`, no external requests
- [ ] Widget 1: mirror pair + distance matrix + signed volume, side by side, **linked rotation**
- [ ] Widget 2: invariance ladder, vertical
- [ ] Widget 3: fusion explorer, all 534 rows, filterable
- [ ] Static chart: limonene purity, two bars
- [ ] Prose for all four acts

**Experiment (M1, not this laptop):**
- [ ] Port OpenPOM's 134-d atom / 6-d bond featurization to plain RDKit
- [ ] Small message-passing net in pure PyTorch, no DGL, no DeepChem
- [ ] Four variants: as-shipped, +bond stereo, +signed volume, +CIP tag
- [ ] Unit test: the parity-blind arm must emit *identical* outputs for both members of every
      enantiomer pair. If it ever differs, the featurization is leaking and the run is void
- [ ] Static chart: results
- [ ] Pre-commit in writing to reporting an unimpressive result

**Open decision:**
- [ ] Is §18 ("what died") page-visible or repo-only?
