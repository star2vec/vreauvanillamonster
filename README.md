# What neural networks provably cannot smell

An interactive explainer, plus an audit of the standard benchmark the odor-ML field
trains on.

**Status: work in progress.** The audit is complete and reproducible. The experiment and
the page are being built.

## The claim

Enantiomers are mirror-image molecules — same atoms, same bonds, opposite handedness.
They can smell completely different: (R)-carvone is spearmint, (S)-carvone is caraway.

Most molecular ML models provably cannot see this. A 2D graph model receives a
byte-identical input tensor for both. A model built on pairwise distances is also blind,
and that is a theorem rather than an oversight: a distance matrix determines the Gram
matrix, which determines the point set only up to an orthogonal transform, and O(3)
contains reflections. Distinguishing enantiomers requires a parity-odd quantity.

`curated_GS_LF_merged_4983.csv`, the field's standard benchmark, destroyed the evidence
anyway. It is the stereo-flattened union of two files that sit beside it in the same
repository directory and that still carry stereochemistry.

## What the audit finds

| | |
|---|---|
| Benchmark rows reconstructed exactly from source | 4,983 / 4,983 |
| Rows that fuse two or more distinct stereoisomers | 534 (10.7%) |
| Stereoisomers absorbed into those rows | 1,258 |
| Fusions whose source records carried conflicting labels | 508 |
| Fusions of a true **enantiomer** pair | 87 |
| …of those, with conflicting labels | 74 |
| …with both members fully stereo-specified | **71** |
| Fusions that are diastereomer or E/Z only | 447 |

That split matters. A 2D graph model is blind to all 534. A distance-based 3D model
recovers the 447 — diastereomers have genuinely different distance geometries — and
remains provably blind to the 87. Only a parity-odd feature reaches the rows where the
labels actually disagree.

The obvious objection is that some fused records were never resolved in the source
anyway — a racemate, or an undifferentiated trade entry — so the merge cannot be blamed
for losing a distinction nobody recorded. That objection gets a number rather than a
paragraph. Of the 534 fusions, **97** have every member fully stereo-specified, 392 mix an
unspecified record with resolved isomers, and 45 are partly unspecified throughout. The
strictest reading of the headline is therefore 97, not 534. The parity-critical count
barely moves under the same scrutiny: 71 of the 74 have both members of the conflicting
enantiomer pair fully resolved.

## Reproduce it

```
pip install -r requirements.txt
python audit/audit.py
```

The script fetches its own data and writes `out/audit.json`. It asserts that every one of
the 4,983 rows is exactly the union of its source rows' labels, with `odorless` suppressed
only where two or more rows were collapsed. Zero unexplained rows.

## Honest scope

The audit is verifiable from the files. Whether any given enantiomer pair *actually*
smells different to humans is a separate question with a much patchier literature, and the
two are graded separately in `out/audit.json`. Carvone is the only exhibit here whose
perceptual difference meets a purity-controlled standard. At least one — (R)/(S)-2-butanol
— has labels that differ in the data even though humans demonstrably cannot tell the two
apart. Some of the 74 conflicts are annotation noise rather than destroyed signal, and the
page says so.

The label-union mechanism itself was documented by
[Sanchez-Lengeling et al. (2019)](https://arxiv.org/abs/1910.10685). What is new here is
that the identity criterion the union operates on is stereo-blind, so it fuses distinct
molecules rather than reconciling duplicate records — and the size of that effect.

## Sources

- Benchmark and curated source files: [BioMachineLearning/openpom](https://github.com/BioMachineLearning/openpom) (MIT)
- Raw descriptors with stereochemistry intact: [pyrfume/pyrfume-data](https://github.com/pyrfume/pyrfume-data)
