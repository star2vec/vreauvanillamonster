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

**DECIDED: the ceiling leads.** The audit is narrower and more intimidating than it is
compelling — one CSV in one subfield reads as niche, however solid it is — while the ceiling
is an idea, and ideas travel. The audit then lands mid-piece as the *aha* that makes the
ceiling concrete. Title carries the ceiling; subtitle can carry the audit.

**This does not change the running order.** Acts I–IV stay exactly as below. What changes is
the opening frame, the title, and where the emphasis sits — which is cheap.

Three amendments, without which leading with the ceiling walks into the objection I raised
against it:

**(a) Open with the ceiling's *question*, not its thesis.** My earlier worry — that a
ceiling-first opening is too abstract for a non-specialist — only bites if we *assert* the
proposition ("binary label spaces cannot express potency"). Open instead with the puzzle it
answers, and we get breadth and concreteness at once. Something in the register of:

> Everyone knows chirality is the hard case for molecular machine learning. The standard
> story is that models cannot see it. That story is true — and it is not the problem.

Tension, no abstraction, and the reader is oriented in three sentences.

**(b) Headline the *structural* leg, never a count.** Leg 1 — the label space is `{0,1}^138`
with no intensity dimension — is a fact about a schema, not an estimate, so it cannot shrink
under scrutiny. Leg 2 (the literature pattern) supports it. I have now revised a ceiling
number downward twice; if the headline contained one, that fragility would be load-bearing.
**All counts belong to the audit.**

**(c) Move the scope pre-emption into the first three paragraphs.** Audit-first, the
"intensity was out of scope" objection lands on a late section. Ceiling-first, it lands on
the thesis, so it must be met immediately and in its strong form — see §16.

What we give up: the reader who leaves at 20% now takes away an argument rather than a
verified number, and a critic can attack the thesis before conceding anything. That is a
real cost and it is being accepted knowingly, in exchange for a piece people actually want
to read.

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

**[CORRECTED] My earlier rationale for this was wrong, and the ladder is really four rungs.**
I had written that SphereNet is SE(3)-invariant and "still failed" stereoisomer separation.
Reading Adams et al.'s full text, Figure 3's caption actually says SphereNet's *"separation
… persists through reflection, but the clusters overlap upon rotation of internal bonds."*
Separation **does** persist through reflection — so SE(3)-invariance genuinely buys
reflection sensitivity, and its failure there is conformational, not parity.

The defensible version, quotable verbatim: torsion angles *"provide access to the full
geometric information present in the conformer but do not guarantee expressivity when
learning chiral-dependent functions."* So the honest ladder:

| Rung | Status |
|---|---|
| 2D graph | no stereochemistry at all — blind to all 534 |
| E(3)-invariant (distances, angles) | **provably** blind to the 87 |
| SE(3)-invariant (adds torsions) | has *access* to parity; expressivity not guaranteed |
| parity handed over explicitly | what our variant 3 does |

Four rungs is more accurate *and* more interesting than three, because the third rung is a
real intermediate rather than a strawman. Direct quote for rung 2: *"E(3)-invariant 3D GNNs
that only consider pairwise atomic distances or bond angles … are inherently limited in
their ability to distinguish enantiomers."*

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
a *fixed* conformation. Two independently embedded enantiomers differ by **1.837 Å** in
their distance matrices, because ETKDG and MMFF settle into different torsional minima at
the flexible remote groups. So a 3D model *can* separate enantiomers in practice — by
conformer artefact, not by seeing parity. That is learning noise.

Our own number, asserted in `assets.py`. An agent had reported 1.11 Å; that did not
reproduce. See `CLAIMS.md`.

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

1. **The vocabulary** — inherited wholesale from Lee et al., and now verified at source. The
   Lee supplementary states the rule outright: *"Variations and misspellings of odor
   descriptors were merged, and any odor descriptor with **<=30 occurrences** in the dataset
   were discarded."* So the two descriptors that distinguish carvone died by two different
   mechanisms in one step: `spearmint` was **merged** into `mint` as a variant, and `caraway`
   was **deleted for being rare** — it has 10 molecules in GoodScents, well under the
   threshold. Not OpenPOM's choice; cite it upstream.
2. **The label normalisation** — OpenPOM then re-implements the merge downstream, and its
   dictionary is quotable: `'mint': ['cornmint', 'peppermint', 'mint', 'minty', 'spearmint']`.
   The chirality signal died to variant-merging plus a frequency threshold.
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

- **Potency: established, verified at source.** Reglitz et al. 2023 (*BrewingScience* **76**,
  92–96, DOI 10.23763/BrSc23-07reglitz — read in full): detection thresholds **0.82 vs 8.3
  µg/kg in water** and **6.5 vs 53 in beer**, so 10.1× and 8.2×. (S) isolated from the
  racemate by chiral HPLC to **>99.9% ee**, commercial (R) at 98.7%, both confirmed by chiral
  GC-MS, then both screened by **chiral GC-O with AEDA showing every impurity at an FD factor
  ≥100× below target** — exactly the control Kvittingen's critique demands. 17 trained
  assessors, ASTM E679.
- **Quality: not established.** The famous lavender/woody versus sweet/petitgrain pair
  traces to Ohloff & Klein 1962, a stereochemistry paper predating chiral GC by 25 years and
  which I have not been able to read.
  **[ATTRIBUTION FIX]** The *"odour qualities of (R)- and (S)-linalool are very similar"*
  line is real and is Reglitz et al.'s — but it sits in their **Introduction as accepted
  background**, not as their finding. They measured thresholds, not quality. Write it as
  "Steinhaus's group describe the qualities as very similar," never as a measured result.
- **Bonus, fully verified:** the widely quoted **80×** ratio is dead. It traces to Jagella
  1999, a TU Munich dissertation, and Reglitz note the air measurements *"were only performed
  by a single assessor."*

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
The correctness trap, and the best single number on the page: with **technical-grade**
limonene, **50%** of participants called (R)-(+) "orange"; with **analytical-grade**, **13%**.
48 and 49 participants. Kvittingen, Sjursnes & Schmid, *J. Chem. Educ.*,
DOI 10.1021/acs.jchemed.1c00363 — read in full, verified.

> **PHRASING WARNING — I had this wrong and it was actively misleading.** The variable is
> **chemical** purity, **not enantiomeric** purity. Both (R)-limonene samples were **>99.9%
> ee**; what differed was total limonene content, 92.1% versus 99.2%, so roughly 7.9%
> against 0.8% impurities. And those impurities were other orange-oil components — several
> technical-grade peaks match peaks in orange oil directly.
>
> **Never write "with >99.9% ee material only 13%."** True, but it implies an enantiomeric
> effect and there is none. Correct phrasing: *same enantiomer, same enantiomeric purity, ten
> times fewer trace impurities — and the orange association collapses from 50% to 13%.*
>
> This is a better fact than the one I thought we had. The percept was never coming from the
> limonene at all.

Their verbatim conclusions are quotable: *"(S)-(−)-Limonene does not convey lemon odor."* and
*"(R)-(+)-Limonene does not convey orange odor."* Also usable: they report Sell's observation
that the purer limonene is, the less odour it has.

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
| Wine lactone stereoisomers | **10⁸** in sensitivity, mice matching humans | potency | verified at source; purity by optical rotation only |
| Linalool | 10.1× in water, 8.2× in beer; qualities described as very similar | potency | verified at source, exemplary purity control |
| Androstenone C₁₉-steroids | odorous vs essentially odourless | potency | thin, unreplicated, abstract-only |
| Carvone | spearmint vs caraway | **quality** | convergent: 3 × 1971 + Laska + Sato 2015 |
| Limonene | orange vs lemon | quality | **refuted, verified at source** |
| Nootkatone | grapefruit vs terpenic | quality | confounded (impurity) |

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
4. ~~Descriptions merged across concentration.~~ **DROPPED — measured and negligible.**
   Re-run with the real curation logic (`audit/concentration_check.py`, which reproduces
   `curated_leffingwell.csv` to **99.97%**, 3,509 of 3,510 rows exact): dilution-only
   information lost to the semicolon truncation affects **23** records, and neat/diluted
   descriptors merged into one vector affects **8**. Out of 3,510. My crude estimate said
   ~37 and I had loosely described 221 records as affected; both were wrong.

   Worth recording *why* it is small, because it is a point in the curation's favour: the
   pipeline unions text-derived descriptors with a pre-existing `Labels` column that
   Sanchez-Lengeling et al. had already cleaned from the *full* description, so most of what
   the truncation drops is recovered from there.

   **[REC] Keep at most one example as colour, never a count.** *"Nearly odorless if pure;
   creamy, vanilla, sweet-tart taste in dilution"* losing `creamy`, `vanilla` and `sweet` is
   a nice illustration of the format having nowhere to put a concentration qualifier. It is
   not evidence of scale.

**[REC] The ceiling rests on legs 1–3 only.** This is the second time I have had to revise
a ceiling number downward, which is exactly why the headline claim must be the *structural*
one — see below.

**The objection you will get, and the answer — which Lee et al. hand us themselves.**
*"Intensity was out of scope — the paper predicts descriptors, not thresholds, so of course
the format excludes it."*

The answer is now much stronger than an argument, because their own Discussion says:

> *"the concentration of an odor influences odor character, but is not explicitly included in
> the map."*

**By their own account concentration affects odour *character*, not merely intensity.** So it
is a known, acknowledged, unaddressed limitation rather than something outside the task. We
are not saying they should have predicted thresholds, and we are not claiming to have noticed
something they missed — they flagged it. Our contribution is that nobody costed it, and
nobody connected it to chirality. **Chirality-aware modelling on this benchmark therefore has
a low ceiling no matter how the SMILES are fixed.**

**[REC] Quote them doing it.** A critique that opens by citing the authors' own caveat is far
harder to dismiss than one that appears to have caught them out.

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

**Frequency-truncation hypothesis — and this one came back from the dead, which is the most
interesting entry here.** I proposed that the vocabulary cut preferentially deleted rare,
parity-carrying labels; tested it; found survivors with frequency 1 and casualties with
frequency 187; and declared it false. It was not false. The Lee supplementary states a
**≤30-occurrence discard rule**, and my test had counted raw GoodScents molecule frequencies
rather than the merged counts in Lee et al.'s combined set — so I was measuring the wrong
quantity and drew the wrong conclusion with apparent evidence. `caraway`, at 10 molecules,
was cut for being rare exactly as I first guessed. The stronger version — that discriminating
descriptors are *systematically* rare — remains untested and unclaimed.

Radical-corruption hypothesis (false: valence stays satisfied).
SphereNet rationale for the ladder (wrong: its separation persists through reflection; the
failure is conformational). Nootkatone as exhibit #2 (demoted: its 1972
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

- ~~Is §16 the headline, or the closing act?~~ **Resolved: the ceiling leads.** See §1 for
  the three amendments that make it work — open with the question not the thesis, headline
  the structural leg not a count, and move the scope pre-emption to the top.

  Two definitions worth keeping straight, since the whole call turned on them. **The audit
  is a measurement**: 534 fusions, 74 conflicting enantiomer pairs, every row reconstructed
  from source, falsifiable by running one command. **The ceiling is an interpretation**: the
  138-label format has no intensity dimension, and the best-evidenced enantiomer differences
  are potency differences, so most of the phenomenon was never expressible. Checkable
  premises, inferred conclusion. They carry different burdens of proof, which is why the
  ceiling must lead with its structural claim and leave every number to the audit.
- ~~Re-run leg 4 of §16 with the real merger dict.~~ **Done: 23 + 8 of 3,510, so the leg is
  dropped.** `audit/concentration_check.py` reproduces the Leffingwell curation to 99.97%,
  which is worth keeping on its own terms — it confirms we understand that pipeline end to
  end.
- **[YOU]** Is §18 ("what died") page-visible or repo-only? I lean visible — strongest
  signal this wasn't a weekend's work — but it is your name on the self-criticism.
- ~~Lee et al. supplementary PDF ungrepped.~~ **CLEARED.** Retrieved via bioRxiv v4 (PMC only
  served an interstitial), 20 pages, extraction validated before trusting the negative. Zero
  occurrences of stereochemistry, stereoisomer, stereo, enantiomer, chiral, isomer, racemic or
  diastereomer. `SMILES` appears once, in a GC-O contaminant column heading. **The page may
  state that the flagship paper is silent on stereochemistry across main text and
  supplementary both.**
- Re-run leg 4 of §16 with the real `merger_root_dict` before quoting any number.
- Experiment results unknown, so §17 is a question with no answer.
