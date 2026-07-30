# Page contents — working document

What the page says and in what order. **Not** how it looks; that goes in `design.md`.
Both of us edit this. My recommendations are marked **[REC]**; things I need your call on
are marked **[YOU]**.

---

## Structure: option D, funnel with the destination promised early

Concrete to abstract, with the abstraction earned. Four acts, in which the audit's hard
numbers are the spine and the representational claim is the destination.

Two commitments make this work, and they are the whole reason D beats the alternatives:

**1. Signpost the destination in the first 200 words.** The reader should know early that
this is heading toward a claim about *representation* — not just a bug report about one
CSV. Otherwise the closing act reads as an afterthought bolted onto a data-forensics piece,
and readers who leave early never learn where it was going.

**2. Stop numbering everything as "faults."** This is the single most important framing
decision in the document:

| | What it is | Kind |
|---|---|---|
| Losses 1–3 | Evidence existed in the sources and the pipeline destroyed it | **loss** |
| The blind spot | The reference model cannot see the distinction even if restored | **blindness** |
| The ceiling | Most of the phenomenon was never expressible in the format at all | **limit** |

Calling these "faults 1 through 5" flattens the best idea into a list item. They are three
different kinds of thing, and the page should say so.

Closing line, honest in both directions: *the evidence was destroyed three times over;
restoring it recovers the quality differences, and reveals that most of the phenomenon was
never expressible in the first place.*

---

# Act I — Handedness is real

### 1. Hook: what is actually in a cola
Flavour is mostly smell. Cola flavour is citrus, cinnamon, vanilla and spice oils, and
those oils are mixtures of specific aroma molecules — some of which come in two
mirror-image forms.

**[REC] Lead with linalool, because a cola formula plausibly contains *both* of its
enantiomers at once** — S-(+) from coriander (~88% S), R-(−) from lavender and neroli.

**[REC] The promissory opening.** Title and first paragraph carry the *audit* — concrete,
countable, verifiable. Then one sentence promises the ceiling without arguing it, roughly:
*"and the deeper problem isn't that the data was damaged — it's that the format was never
able to hold what chirality actually does. I'll come back to that."*

Then it is kept in §16, where the reader has already accepted the numbers.

Why this beats leading with either one alone:

- A reader who leaves at 20% takes away the audit, which is correct and shareable.
- A reader who finishes gets the ceiling as an earned payoff.
- The burden of proof sits on the audit, which is discharged mechanically by running one
  script, while the ceiling arrives only after the numbers have bought trust.
- A critic attacking the ceiling has, by that point, already conceded the audit.
- Rhetorically decisive: an argument the reader *arrives at* feels like their own
  conclusion; an argument asserted up front feels like a thesis to resist. The ceiling is
  exactly the kind of claim that benefits from being earned rather than declared.

The one real cost is that the title cannot also announce a representation-learning
contribution. **[REC] Recover that in the subtitle** — title carries the audit, subtitle
carries the ceiling.

Corrections to carry, both of which are errors I made earlier and had to fix:
- Citrus **peel** oil is **not** rich in linalool — 0.03–1.6% against 38–91% limonene.
- The defensible claim is sharper: in *Citrus sudachi* peel oil, **(S)-(+)-linalool has the
  highest odour-unit value of all 26 components**, the only one above 1.0, far above
  limonene. Trace abundance, largest single contribution to the smell.
- Citrus **flower and leaf** oils genuinely are linalool-rich: neroli 28–40% (R-dominant),
  orange blossom 15–32% (S), petitgrain >27% (S).
- The "7X formula" provenance (Merory 1960, the Pemberton notebook) is itself
  folklore-grade. Hedge it if we name specific oils. Coriander/cinnamon/citrus/vanilla as
  the cola profile is uncontroversial; the exact recipe is not.

### 2. Two molecules, one difference
(R)-carvone smells of spearmint; (S)-carvone of caraway. Same atoms, same bonds, same
connectivity. Only the handedness differs.

**Carvone is the lead exhibit throughout** — the only one meeting a purity-controlled
evidence bar, and the only one whose difference a reader can imagine.

**Visualisation: mirror pair viewer. Side by side, with linked rotation.**
Side by side is obvious since comparison *is* the content. The critical detail is that the
viewers must **rotate together**. Independent rotation shows two unrelated blobs and
teaches nothing; lockstep rotation plus a `reflect` toggle makes "mirror images, not
different molecules" land in the body rather than the head. Highest-value interaction
decision on the page.

Built: `out/assets.json → mirror_pair`, exact mirror construction, shared atom ordering.

### 3. Why you can smell the difference
Short. Receptors are themselves chiral, so a left hand and a right hand don't fit the same
glove. Do not overreach — the receptor story is where popular writing usually overclaims.

**[REC] Explicit stop point.** A casual reader should be able to leave here satisfied.

---

# Act II — Models provably cannot see it

### 4. What a model actually receives
Both carvone enantiomers produce a **byte-identical** input tensor to a 2D graph model.
Not approximately.

**[REC] Ground this in the field's real code, not a hypothetical.** OpenPOM's featurizer
builds a 134-dimensional atom vector from exactly six properties — valence, degree, num_Hs,
formal charge, atomic number, hybridization — and a 6-dimensional bond vector of bond type
plus `IsInRing()`. Nothing in either is stereochemistry. A repo-wide grep for
chirality-related calls returns zero hits in any `.py` source. **This is the blindness**,
and it is quotable from 236 lines of code.

### 5. So use 3D — and it still fails
A distance-based model is *also* blind, and this is a theorem: the distance matrix
determines the Gram matrix, which determines the point set up to an orthogonal transform,
and O(3) contains reflections.

**Visualisation: distance-matrix reveal, side by side, sharing the viewer above.**
Both matrices adjacent, with a difference strip reading zero everywhere. Rotate: unchanged.
Reflect: still unchanged. The theorem becomes tactile instead of asserted.

Verified: `max|dA − dB| = 0.0` exactly, asserted in `assets.py`.

Primary citation: **Dumitrescu et al., "E(3)-equivariant models cannot learn chirality,"
ICLR 2025**, arXiv:2402.15864 — a formal proof. Joshi et al., ICML 2023 (arXiv:2301.09308)
for the general expressivity frame.

### 6. The minimal fix
One number: the signed volume of the neighbour vectors at the stereocentre. `+2.481266` and
`−2.481266`. Rotation preserves it; reflection negates it. That is all "parity-odd" means.

**[REC] A single readout under both viewers, not a separate widget** — one extra row
appearing on something the reader already understands.

### 7. The invariance ladder
**[REC] Vertical, not side by side** — it is a hierarchy, and vertical reads as ascent.

| Rung | Blind to |
|---|---|
| 2D graph | all 534 fusions |
| distance-based / E(3)-invariant | the 87 enantiomer fusions |
| parity-aware | none |

**[REC] Do not label rung 3 "SE(3)."** SE(3)-invariance is necessary but not sufficient:
SphereNet is SE(3)-invariant and still failed Adams et al.'s stereoisomer separation test. A
GDL reader will check this.

**[REC] This is the strongest GDL showcase on the page**, because the counts are real. Many
people can explain E(3) versus SE(3); almost nobody grounds it in "here are 87 rows of the
field's actual benchmark where the distinction bites."

Worth a paragraph: ChiENN (Gaiński et al., ECML PKDD 2023) locates the root cause deeper
than missing features — messages are aggregated with a permutation-invariant function,
which is what destroys the information. Our approach sidesteps this by precomputing a
per-atom parity scalar. And Tetra-DMPNN (arXiv:2012.00094) is the cleanest empirical hook
in this literature: 98–100% R/S accuracy with an order-sensitive aggregator versus **exactly
50%, chance**, with a plain sum.

### 8. Where the theorem stops
The limit of our own argument, stated before anyone else states it. The theorem is exact for
a *fixed* conformation. Two independently generated conformers of two enantiomers differ by
over 1 Å in their distance matrices, because embedding lands in different torsional minima.
So a 3D model *can* separate enantiomers in practice — by conformer artefact, not by seeing
parity. That is learning noise.

**[REC] Keep this.** Short, costs nothing, and signals we understand the argument rather
than reciting it.

---

# Act III — The data did not keep it either

### 9. The benchmark
`curated_GS_LF_merged_4983.csv`, 4,983 × 140. The SMILES column is named
`nonStereoSMILES`, and the file contains zero `@`, `/`, `\` characters. Stereochemistry was
never hidden — the column name says so plainly. It was just never costed.

### 10. Three losses
**[REC] Loss 2 leads the act, not loss 3.** The flatten is the *binding* loss, but the
label normalisation is the *surprising* one, and a reader who expects a modelling mistake
and gets a regex will remember it. Most quotable finding we have.

1. **The vocabulary** — inherited wholesale from Lee et al. No `caraway`, `spearmint`,
   `dill`. Not OpenPOM's choice; cite it upstream.
2. **The label normalisation** — `spearmint` merged into `mint` because the string contains
   "mint"; `caraway` deleted because it matches nothing in the 138. The chirality signal
   died to `str.match`.
3. **The flatten** — one notebook cell, under a header titled `### Handle stereo isomers`.
   Carvone's enantiomers still carried *different* labels after losses 1 and 2; this killed
   the survivor.

Forward-reference the ceiling here without stating it — it needs Act IV's distinction first.

### 11. The numbers
534 fusions (10.7%), 1,258 stereoisomers absorbed, 508 with conflicting labels, 87
enantiomer pairs, 74 conflicting, 71 fully specified.

**[REC] Pre-empt the objection inside the section, with a number.** A sceptic's first move
is "some of those were racemates anyway." Answer: only 97 of 534 have every member fully
stereo-specified, so the strictest reading is 97. The parity-critical count barely moves —
71 of 74. Volunteering this is what makes the rest credible.

### 12. The fusion explorer
All 534 rows, filterable by enantiomer-vs-diastereomer, conflicting-labels, and evidence
tier; each expanding to source isomers, original labels, and the merged row.

**[REC] Not side by side — a filterable list.** Its job is completeness, not comparison.
This is the object a sceptic uses to try to disbelieve the counts and fails.

### 13. The fix is one cell
Flattening the two source files reproduces the shipped benchmark exactly: 4,983 of 4,983
rows, zero unexplained. So the fix is not "recurate from scratch," it is **don't run one
cell** — the stereochemistry is already sitting in the same directory.

Cite **Sanchez-Lengeling et al. 2019** (arXiv:1910.10685) for the union rule itself, which
is prior-published. Our contribution is that the identity criterion the union operates on is
stereo-blind, so it fuses distinct molecules rather than reconciling duplicate records —
plus the magnitude.

---

# Act IV — But what were we restoring?

### 14. How much of this was ever real?
**[REC] A full section. This is where the piece earns trust.**

The audit is verifiable from files. Whether any given enantiomer pair *actually* smells
different is a separate question with much patchier evidence. Carvone is the only exhibit
meeting a purity-controlled standard. (R)/(S)-2-butanol have different labels in the
benchmark although Laska & Teubner 1999 showed humans **cannot** discriminate them. So some
of the 74 are annotation noise, not destroyed signal.

**Linalool returns here as the bookend, and it is the best teaching case we have**, because
it splits the two claims people conflate:

- **Potency: established.** 8–10× threshold difference, confirmed independently 1997 and
  2023. Reglitz et al. 2023 (*BrewingScience* 76, 92–97, DOI 10.23763/BrSc23-07reglitz)
  isolated (S) from the racemate by chiral HPLC to >99.9% ee and screened both by chiral
  GC-O confirming every impurity ≥100× below target — exactly the control Kvittingen's
  limonene critique demands. 17 assessors, ASTM E679 forced choice.
- **Quality: not established.** The famous lavender/woody versus sweet/petitgrain pair
  traces to Ohloff & Klein 1962, a stereochemistry paper predating chiral GC by 25 years.
  Steinhaus's group, holding the cleanest material anyone has had, reports the two
  qualities are "very similar."

**Two details about how evidence decays, both usable:**

The one purity-controlled panel test of linalool *quality* (Padrayuttawat et al. 1997) also
reports discriminating **limonene** enantiomers at p<0.001 — at 89%/94% purity, exactly the
regime Kvittingen proved generates false positives. Same table, same method, same purity,
and one of its two results is known to be wrong. Better than any assertion we could write.
Its linalool (S) sample was ~80% ee, so the ~10% (R) contamination — nine times more potent
— sat far above (R)'s own threshold at test concentration.

The widely quoted **80×** linalool ratio is dead: single assessor, unpublished 1999
dissertation, explicitly disproved by Reglitz et al.

### 15. The limonene trap
The correctness trap, and the best single number on the page: with technical-grade limonene,
**50%** of participants called (R)-(+) "orange"; with >99.9% ee material, **13%**. Same
molecule, same question, purity the only variable.
Kvittingen, Sjursnes & Schmid 2021, DOI 10.1021/acs.jchemed.1c00363.

**[REC] Two bars. That is the entire chart.** Resist elaborating it.

Plus the irony worth using: Friedman & Miller 1971 is simultaneously the origin of the
debunked limonene claim *and* one of three independent carvone replications. Same paper,
same year — one claim survived retesting, one didn't. Better than asserting "check your
sources."

### 16. The ceiling: the labels have no volume knob
**[REC] The closing argument, and the most original thing here.**

Every one of the 138 labels is a binary present/absent descriptor. I checked: **not one
carries any intensity sense** — no *weak*, *strong*, *faint*, *intense*. So the format can
express a potency difference only when it crosses the detection threshold entirely, through
the single `odorless` label.

And that interlocks with loss 3: **`odorless` is the only potency channel that exists, and
merge cell 42 deliberately deletes it when fusing rows.** The one place potency information
could have survived is precisely what the merge discards. Those 7 odorless-erasure groups
matter more than I first credited.

Then the pattern in the literature, once quality and potency are separated:

| Pair | Difference | Kind | Evidence |
|---|---|---|---|
| Wine lactone stereoisomers | >10⁷ in threshold | potency | strong |
| Linalool | 8–10× threshold, qualities "very similar" | potency | strong |
| Androstenone C₁₉-steroids | odorous vs essentially odourless | potency | thin, unreplicated |
| Carvone | spearmint vs caraway | **quality** | strong |
| Limonene | orange vs lemon | quality | **refuted** |
| Nootkatone | grapefruit vs terpenic | quality | confounded |

Carvone is the *outlier*, not the pattern. For every pair whose difference is purely
potency, the benchmark cannot express it — with stereochemistry restored **and** perfect
labels. A binary vector can say `odorless`; it cannot say "the same smell, nine times
stronger."

**Evidence weighting — be honest about which legs are load-bearing:**

1. **Structural (airtight).** 138 binary labels, zero intensity dimension, potency
   expressible only at the `odorless` boundary, which the merge deletes.
2. **The literature pattern (strong).** The table above.
3. **Concentration metadata discarded (solid, verified).** The source records concentration
   for 4,137 of 4,626 stimuli spanning four orders of magnitude — 100%, 10%, 1%, 0.1%,
   0.01% — plus solvent for 1,850. The benchmark keeps **none** of it. So descriptors
   elicited at 0.01% and at 100% are treated as commensurable.
4. **Descriptions merged across concentration (real but modest — do not inflate).** 226 raw
   Leffingwell records qualify a descriptor by concentration. In a *crude approximation* of
   the curation logic, ~37 produce label vectors drawing from both the neat and the diluted
   clause. Vivid examples: *"Strong, offensive fecal odor; diluted — floral, animal,
   overripe fruit"* becomes a row asserting `floral` and `fruity`. **Caveat: my
   approximation produced obvious false positives** (it matched `odor` → `odorless`), so
   **no number here is quotable until the real `merger_root_dict` from cell 35 is applied.**
   Treat as illustration, not as a count.

**[REC] Present legs 1–3 as the argument and leg 4 as illustration.** I earlier described
this as a second leg of equal weight to the stereochemistry finding; that was overstated
and I am correcting it. 37-ish is an order of magnitude below 534.

**The objection you will get, and the answer.** *"Intensity was out of scope — the paper
predicts descriptors, not thresholds, so of course the format excludes it."* That objection
is fair as stated and must be met head-on, not dodged. The answer: we are **not** saying
they should have predicted thresholds. We are saying that if the field is arguing about
whether chirality matters for odor ML — and it is — it needs to know that most
well-documented chirality effects live in the modality this benchmark excludes. **So
chirality-aware modelling on this benchmark has a low ceiling no matter how the SMILES are
fixed.** Precise, actionable, and requires nobody to have made a mistake.

Note this bounds the experiment before we run it, which is a point in its favour.

### 17. The experiment
**[REC] Write the question now, the conclusion later.** Results do not exist yet and the
section must accommodate any outcome.

Question: train the same architecture four ways — as-shipped features, plus bond stereo,
plus geometric signed volume, plus topological CIP tag — on the file that still has
stereochemistry. The parity-blind arm's failure is a *theorem*, not a result: identical
inputs give identical outputs. What is genuinely unknown is how much signal the parity-aware
arms extract from the 74, and whether geometry beats a topological tag.

**[REC] Pre-commit in writing to reporting an unimpressive result.** Given §14 and §16, a
small effect is the honest expectation. Saying so before we know is what makes the number
trustworthy afterwards.

**[REC] The experiment is an appendix to §16, not the climax.** End the *argument* at the
ceiling.

### 18. What died
Hypotheses tested and killed. **[REC] Include, but as an appendix** — credibility
scaffolding for the sceptical reader, not narrative.

Frequency-truncation hypothesis (false: hardcoded inherited list). Radical-corruption
hypothesis (false: valence stays satisfied). Nootkatone as exhibit #2 (demoted: its 1972
primary source has limonene's exact impurity confound, never replicated in 54 years).
Isopulegol and pinocarvone (dropped: diastereomer-only). Geraniol/nerol (demoted:
Leffingwell independently calls nerol rose-like). Linalool's descriptor pair (demoted to
potency-only). A citation I got wrong before correcting it. And in this document: an
overstated concentration count, corrected in §16.

---

## Proposed cuts

**[REC]** Each is interesting; none earns a section.

- **Menthol's 6-isomer fusion** → explorer only. Diastereomers, needs a caveat paragraph,
  menthone does the parity job cleanly, and Laska showed humans cannot discriminate menthol
  enantiomers at all.
- **Lily aldehyde's 8-way fusion** → one image. Widest fusion in the benchmark, but nearly
  all eight are "floral," so it sells scale and not disagreement.
- **Geraniol/nerol** → footnote in §14 on the two source authorities disagreeing.
- **Flavour pairing (white chocolate & caviar)** → one sentence at most. Different thesis,
  and a second hook competing with cola makes the top feel unfocused.
- **Wine lactone** → one row in §16's table plus an aside. Spectacular numbers but it is
  *not* in the OpenPOM sources, so it cannot be an audit exhibit — only motivation.

---

## Interactive budget

**[REC] Three substantial widgets, two static charts. Stop there.**

1. Mirror pair + distance matrix + signed volume — *one* linked widget, §2/5/6
2. Invariance ladder — §7
3. Fusion explorer — §12
4. Static: limonene purity bars — §15
5. Static: experiment results — §17

Five widgets would read as a demo reel. Three makes the page feel alive.

---

## Open questions

- ~~Is §16 the headline, or the closing act?~~ **Resolved via the promissory opening
  (§1):** audit in the title, ceiling in the subtitle, promised in the first paragraph and
  paid off in §16. Not a compromise — see the reasoning in §1.

  Two definitions worth keeping straight, since the whole call turned on them. **The audit
  is a measurement**: 534 fusions, 74 conflicting enantiomer pairs, every row reconstructed
  from source, falsifiable by running one command. **The ceiling is an interpretation**: the
  138-label format has no intensity dimension, and the best-evidenced enantiomer differences
  are potency differences, so most of the phenomenon was never expressible. Its premises are
  checkable but its conclusion is an inference. Measurements and interpretations carry
  different burdens of proof, which is why the measurement goes first.
- **[YOU]** Is §18 ("what died") page-visible or repo-only? I lean visible — strongest
  signal this wasn't a weekend's work — but it is your name on the self-criticism.
- Lee et al. supplementary PDF still ungrepped. Until it is, the page cannot claim the
  flagship paper is silent on stereochemistry. Affects §9 and §10 wording only.
- Re-run leg 4 of §16 with the real `merger_root_dict` before quoting any number.
- Experiment results unknown, so §17 is a question with no answer.
