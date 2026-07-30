# Page contents — working document

What the page says and in what order. **Not** how it looks; that goes in `design.md`.
Both of us edit this. My recommendations are marked **[REC]**; things I need your call on
are marked **[YOU]**.

---

## The narrative spine

**[REC] Four acts, with the problem getting worse in each, then a reversal.**

I considered three shapes. A *two-track* structure (chemistry track and ML track
converging) is hard to follow and I'd drop it. A flat *detective story* fits the audit but
has nowhere to put the theorem. What actually fits the findings is **escalation followed
by a turn**, because that is genuinely what happened:

1. **Act I — Handedness is real and it matters.** Molecules have mirror images; they can
   smell different. Reader leaves with a visceral sense of chirality.
2. **Act II — Models provably cannot see it.** Not an oversight, a theorem. Reader leaves
   understanding *why*, having manipulated it themselves.
3. **Act III — The data cannot either, and here is exactly where it died.** Four faults,
   escalating. Reader leaves with the audit.
4. **Act IV — The turn: how much of this was ever real?** The evidence being recovered is
   partly unreplicated folklore. Reader leaves trusting us *more*, not less.

The turn in Act IV is the whole reason this is worth publishing rather than being a
takedown. It has to be a real section, not a footnote — see below.

---

## Act I — Handedness

### 1. Hook: why does Vanilla Coke taste like that
Flavour is mostly smell. Cola flavour is a blend of citrus, cinnamon, vanilla and spice
oils. Those oils are mixtures of specific aroma molecules — and some of those molecules
come in two mirror-image forms.

**[YOU] The hook has a seam I want to flag rather than paper over.** Our lead exhibit is
carvone (spearmint vs caraway), which is *not* a cola note. So the cola framing gets the
reader in and then hands off to an unrelated molecule. Two options:

- **(a)** Use cola only to establish "flavour is smell," then pivot: "the cleanest known
  example of what I'm about to describe is a molecule in spearmint."
- **(b) [REC, conditional]** Make the hook load-bearing by leading the exhibit with
  **linalool**, which is genuinely a citrus and coriander oil component *and* is already
  in our enantiomer-conflict set with disagreeing labels. Then the hook pays off directly.

(b) is better if linalool survives the same purity-controlled scrutiny that killed
nootkatone. Unvetted so far. If it fails, fall back to (a) — carvone stays the lead
either way, since it is the only exhibit meeting the evidence bar.

### 2. Two molecules, one difference
(R)-carvone smells of spearmint; (S)-carvone of caraway. Same atoms, same bonds, same
connectivity. The only difference is handedness.

**Visualisation: the mirror pair viewer. [REC] Side by side, with linked rotation.**

Side by side is obviously right here — comparison *is* the content. But the critical
detail is that the two viewers must **rotate together**. If the reader can rotate them
independently, they see two unrelated blobs and learn nothing. Linked rotation plus a
`reflect` toggle is what makes "these are mirror images, not different molecules" land in
the body rather than the head.

Data is built: `out/assets.json → mirror_pair`, exact mirror construction, atom ordering
shared.

### 3. Why you can smell the difference
Brief: receptors are themselves chiral, so a left hand and a right hand don't fit the same
glove. Keep short — this is not a neuroscience page, and the receptor story is where a lot
of popular writing overclaims.

**[REC] Explicit stop point.** A casual reader should be able to leave here satisfied.

---

## Act II — The theorem

### 4. What a model actually receives
A 2D graph model gets atoms and bonds. Both carvone enantiomers produce a *byte-identical*
input tensor. Not approximately — identically.

**[REC] Ground this in real code, not a hypothetical.** OpenPOM's own featurizer builds a
134-dimensional atom vector from six properties: valence, degree, num_Hs, formal charge,
atomic number, hybridization. Quote it. Nothing in it is stereochemistry. This is the
reference implementation the field runs, and beat 2 stops being theoretical.

### 5. So use 3D — and it still fails
The interesting case. A model built on pairwise distances is *also* blind, and this is a
theorem: the distance matrix determines the Gram matrix, which determines the point set up
to an orthogonal transform, and O(3) contains reflections.

**Visualisation: the distance-matrix reveal. [REC] Side by side, sharing the viewer above.**

Both matrices, adjacent, with a difference strip that reads zero everywhere. Rotate the
molecules: matrices unchanged. Reflect: still unchanged. This is the moment the theorem
becomes tactile instead of asserted.

Verified: `max|dA − dB| = 0.0` exactly, asserted in `assets.py`.

### 6. The minimal fix
One number: the signed volume of the three neighbour vectors at the stereocentre.
`+2.481266` and `−2.481266`. Rotation preserves it; reflection negates it. That is the
whole of what "parity-odd" means.

**[REC] Single readout under both viewers, not a separate widget.** It should feel like an
extra row appearing on something the reader already understands.

### 7. The invariance ladder
Three rungs, each seeing strictly more. **[REC] Vertical, not side by side** — it is a
hierarchy, and vertical reads as ascent.

| Rung | Blind to |
|---|---|
| 2D graph | all 534 fusions |
| distance-based / E(3)-invariant | the 87 enantiomer fusions |
| parity-aware | none |

**[REC] Do not label rung 3 "SE(3)".** SE(3)-invariance is necessary but not sufficient —
SphereNet is SE(3)-invariant and still failed Adams et al.'s stereoisomer separation. Say
"parity-aware." A GDL reader will check this.

**[REC] This is the strongest section for showing GDL competence**, because the counts are
real. Many people can explain E(3) versus SE(3); almost nobody grounds it in "here are 87
rows of the field's actual benchmark where the distinction bites."

### 8. Where the theorem stops
The limit of our own argument, stated before anyone else states it. The theorem is exact
for a *fixed* conformation. Two independently generated conformers of two enantiomers
differ by over 1 Å in their distance matrices, because the embedding lands in different
torsional minima. So a 3D model *can* separate enantiomers in practice — by conformer
artefact, not by seeing parity. That is learning noise.

**[REC] Keep this.** It is short, it costs nothing, and it is the section that signals we
understand the argument rather than reciting it.

---

## Act III — The audit

### 9. The benchmark
`curated_GS_LF_merged_4983.csv`, 4,983 × 140. The SMILES column is named
`nonStereoSMILES` and the file contains zero `@`, `/`, `\` characters. Stereochemistry was
not hidden — the column name says so plainly. It was just never costed.

### 10. Four faults, escalating
The spine of the act. Each one is worse than the last:

1. **The vocabulary** (inherited from Lee et al.) — no `caraway`, `spearmint`, `dill`.
2. **The label normalisation** — `spearmint` merged into `mint` because the string
   contains "mint"; `caraway` deleted because it matches nothing. The chirality signal
   died to `str.match`. **[REC] This is the most quotable finding on the page.**
3. **The flatten** — one notebook cell, under a header titled `### Handle stereo isomers`.
   Carvone's enantiomers still had *different* labels after faults 1 and 2. This killed
   the survivor.
4. **The model** — the featurizer has no stereo features, so even a fixed dataset changes
   nothing.

**[REC] Fault 2 leads the act, not fault 3.** It is more surprising, more specific, and
more mechanistically satisfying: the reader expects a modelling mistake and gets a regex.

### 11. The numbers
534 fusions (10.7%), 1,258 stereoisomers absorbed, 508 with conflicting labels, 87
enantiomer pairs, 74 conflicting, 71 fully specified.

**[REC] Pre-empt the objection in the section itself, with a number.** The first thing a
sceptic says is "some of those were racemates anyway." Answer: only 97 of 534 have every
member fully stereo-specified, so the strictest reading is 97. The parity-critical count
barely moves — 71 of 74. Volunteering this makes the rest credible.

### 12. The fusion explorer
All 534 rows, filterable by enantiomer-vs-diastereomer, conflicting-labels, and evidence
tier. Each expands to source isomers, their original labels, and the merged row.

**[REC] Not side by side — a filterable list.** This is the "try to disbelieve me" object.
Its job is completeness, not comparison.

### 13. The fix
Reproduce the whole file by flattening the two source files: 4,983 of 4,983 rows exact,
zero unexplained. Therefore the fix is not "recurate from scratch," it is **don't run one
cell**. The stereochemistry is already sitting in the same directory.

---

## Act IV — The turn

### 14. How much of this was ever real?
**[REC] A full section, placed here, not a footnote.** This is where the piece earns trust.

The audit is verifiable from files. Whether any given enantiomer pair *actually* smells
different is a separate question with much patchier evidence. Of our exhibits, carvone is
the only one meeting a purity-controlled standard. And (R)/(S)-2-butanol have different
labels in the benchmark although Laska & Teubner 1999 showed humans **cannot** discriminate
them. So some of the 74 are annotation noise, not destroyed signal.

### 15. The limonene trap
The correctness trap, and the best single number on the page: with technical-grade
limonene, 50% of participants called (R)-(+) "orange"; with >99.9% ee material, 13%. Same
molecule, same question, purity the only variable.

**[REC] Two bars. That is the entire chart.** Resist elaborating it.

Plus the irony worth using: Friedman & Miller 1971 is simultaneously the origin of the
debunked limonene claim *and* one of three independent carvone replications. Same paper,
same year — one claim survived retesting, one didn't. Better than asserting "check your
sources."

### 16. The experiment
**[REC] Write this section's question now and its conclusion later.** Results don't exist
yet, and the section must accommodate any outcome.

Question: train the same architecture four ways — as-shipped features, plus bond stereo,
plus geometric signed volume, plus topological CIP tag — on the file that still has
stereochemistry. The parity-blind arm's failure is a *theorem*, not a result: identical
inputs give identical outputs. What's genuinely unknown is how much signal the
parity-aware arms extract from the 74, and whether geometry beats a topological tag.

**[REC] Pre-commit in writing to reporting an unimpressive result.** Given §14, a small
effect is the honest expectation. Saying so before we know is what makes the number
trustworthy afterwards.

### 17. What died
Hypotheses tested and killed. **[REC] Include, but as an appendix, not the main flow** —
it is credibility scaffolding for the sceptical reader, not narrative.

Frequency-truncation hypothesis (false: hardcoded inherited list). Radical-corruption
hypothesis (false: valence stays satisfied). Nootkatone as exhibit #2 (demoted: its 1972
primary source has limonene's exact impurity confound). Isopulegol and pinocarvone
(dropped: diastereomer-only). Geraniol/nerol (demoted: Leffingwell independently calls
nerol rose-like). A citation I got wrong before correcting it.

---

## Proposed cuts

**[REC] Cut or demote these.** Each is interesting and none earns a section:

- **Menthol's 6-isomer fusion** → move to the explorer only. Diastereomers, needs a
  caveat paragraph, and menthone does the parity job cleanly. Also Laska showed humans
  can't discriminate menthol enantiomers at all.
- **Lily aldehyde's 8-way fusion** → one image. Widest fusion in the benchmark, but nearly
  all eight are "floral," so it sells scale and not disagreement.
- **Geraniol/nerol** → footnote in §14 about the two source authorities disagreeing.
- **Flavour pairing (white chocolate & caviar)** → one sentence in §1 at most. It is a
  different thesis (shared volatiles between unlike foods) and a second hook competing
  with cola makes the top feel unfocused.
- **Wine lactone** → one aside in §14. Spectacular numbers (>10⁷ threshold range) but it
  is *not* in the OpenPOM sources, so it cannot be an audit exhibit — only motivation.

---

## Interactive budget

**[REC] Three substantial widgets, two static charts. Stop there.**

1. Mirror pair + distance matrix + signed volume — *one* linked widget, §2/5/6
2. Invariance ladder — §7
3. Fusion explorer — §12
4. Static: limonene purity bars — §15
5. Static: experiment results — §16

Every additional widget costs build time and reader attention. Three is enough that the
page feels alive; five would make it feel like a demo reel.

---

## Open questions blocking content

- **[YOU]** Hook: linalool (needs vetting) or pivot-to-carvone?
- Lee et al. supplementary PDF still ungrepped. Until it is, the page cannot claim the
  flagship paper is silent on stereochemistry. Affects §9 and §10 wording only.
- Experiment results unknown, so §16 is a question with no answer yet.
- **[YOU]** Should §17 ("what died") be visible on the page, or repo-only? I lean visible
  — it is the strongest signal that this wasn't done in a weekend — but it is your name on
  the self-criticism.
