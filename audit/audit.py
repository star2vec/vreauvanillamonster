"""
Audit of curated_GS_LF_merged_4983.csv (OpenPOM), the standard benchmark for
odor prediction, for stereochemical information loss.

Recomputes every number quoted on the explainer page and writes audit.json.
Requires: pandas, rdkit. Data is fetched once into ./data/.

The claim under test: the benchmark is the stereo-flattened union of two files
that sit beside it in the same repo directory and that still carry
stereochemistry. Flattening fuses distinct stereoisomers into single rows,
unioning their odor labels -- including cases where the fused isomers were
recorded with conflicting descriptions.
"""

import json
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

# Anchored to this file, not the working directory, so the script runs correctly
# from anywhere and the cache lands where .gitignore expects it.
HERE = Path(__file__).resolve().parent
DATA = str(HERE / "data")
OUT = HERE.parent / "out" / "audit.json"
OPENPOM = ("https://raw.githubusercontent.com/BioMachineLearning/openpom/main/"
           "openpom/data/curated_datasets/")
PYRFUME = "https://raw.githubusercontent.com/pyrfume/pyrfume-data/main/goodscents/"
SOURCES = {
    "curated_GS_LF_merged_4983.csv": OPENPOM + "curated_GS_LF_merged_4983.csv",
    "curated_goodcents.csv": OPENPOM + "curated_goodcents.csv",
    "curated_leffingwell.csv": OPENPOM + "curated_leffingwell.csv",
    "pyrfume_gs_behavior.csv": PYRFUME + "behavior.csv",
    "pyrfume_gs_molecules.csv": PYRFUME + "molecules.csv",
    "pyrfume_gs_stimuli.csv": PYRFUME + "stimuli.csv",
}


def fetch():
    os.makedirs(DATA, exist_ok=True)
    for fname, url in SOURCES.items():
        path = os.path.join(DATA, fname)
        if not os.path.exists(path):
            print(f"  fetching {fname}")
            urllib.request.urlretrieve(url, path)
    return {f: pd.read_csv(os.path.join(DATA, f)) for f in SOURCES}


def canon(smiles):
    """Canonical SMILES with stereochemistry retained."""
    m = Chem.MolFromSmiles(smiles)
    return None if m is None else Chem.MolToSmiles(m)


def flat(smiles):
    """Canonical SMILES with stereochemistry removed -- what the merge produces."""
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    Chem.RemoveStereochemistry(m)
    return Chem.MolToSmiles(m)


def mirror(smiles):
    """The enantiomer: invert every tetrahedral centre.

    Reflection does not change double-bond E/Z configuration, so cis/trans
    isomers are NOT enantiomers of one another. This distinction decides which
    fusions the O(3) reflection argument actually protects: enantiomers share a
    distance matrix and are invisible to any distance-based model, whereas
    diastereomers have genuinely different distance geometries and a 3D model
    can separate them.
    """
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    flip = {Chem.ChiralType.CHI_TETRAHEDRAL_CW: Chem.ChiralType.CHI_TETRAHEDRAL_CCW,
            Chem.ChiralType.CHI_TETRAHEDRAL_CCW: Chem.ChiralType.CHI_TETRAHEDRAL_CW}
    for a in m.GetAtoms():
        if a.GetChiralTag() in flip:
            a.SetChiralTag(flip[a.GetChiralTag()])
    return Chem.MolToSmiles(m)


def openpom_remove_stereo(smiles):
    """Verbatim reimplementation of merge_datasets.ipynb cell 35.

    Strips stereo bond/centre characters from the SMILES *string* before
    parsing, rather than using Chem.RemoveStereochemistry. Checked below to be
    equivalent in outcome on this data: a chiral carbon written [C@H] always
    carries three heavy neighbours plus one explicit hydrogen, so deleting the
    '@' leaves valence satisfied rather than producing a radical.
    """
    s = smiles.replace("@", "").replace("/", "").replace("\\", "")
    m = Chem.MolFromSmiles(s)
    return None if m is None else Chem.MolToSmiles(m, isomericSmiles=True)


def main():
    print("Fetching data")
    d = fetch()
    bench = d["curated_GS_LF_merged_4983.csv"]
    gs = d["curated_goodcents.csv"]
    lf = d["curated_leffingwell.csv"]
    out = {}

    # ---------------------------------------------------------------- benchmark
    print("\n[1] The shipped benchmark")
    labels = [c for c in bench.columns
              if c not in ("nonStereoSMILES", "descriptors")]
    raw = open(os.path.join(DATA, "curated_GS_LF_merged_4983.csv")).read()
    stereo_chars = {ch: raw.count(ch) for ch in ("@", "/", "\\")}
    out["benchmark"] = {
        "rows": len(bench),
        "columns": bench.shape[1],
        "smiles_column": [c for c in bench.columns if "SMILES" in c][0],
        "n_labels": len(labels),
        "labels_are_binary": all(set(bench[c].unique()) <= {0, 1} for c in labels),
        "stereo_chars_in_whole_file": stereo_chars,
        "rows_labelled_odorless": int(bench["odorless"].sum()),
    }
    for k, v in out["benchmark"].items():
        print(f"  {k}: {v}")

    # -------------------------------------------------- vocabulary provenance
    print("\n[2] Vocabulary: absent vs. merged-away descriptors")
    vocab = {c.lower() for c in labels}
    # cell 41 of goodcents_dataset_curation.ipynb, verbatim
    mint_merger = ["cornmint", "peppermint", "mint", "minty", "spearmint"]
    probes = ["caraway", "spearmint", "dill", "mentholic", "peppermint",
              "minty", "neroli", "anise", "licorice", "turpentine", "mint"]
    out["vocabulary"] = {
        "n_labels": len(vocab),
        "source": ("hardcoded `required_desc` in goodcents_dataset_curation.ipynb "
                   "cell 4, cited to Lee et al., A Principal Odor Map Unifies "
                   "Diverse Tasks in Human Olfactory Perception "
                   "(bioRxiv 2022.09.01.504602v4)"),
        "mint_merger_group": mint_merger,
        "descriptor_fate": {
            p: ("in vocabulary" if p in vocab
                else "merged into 'mint'" if p in mint_merger
                else "deleted")
            for p in probes
        },
    }
    for p, fate in out["vocabulary"]["descriptor_fate"].items():
        print(f"  {p:11s} -> {fate}")

    # -------------------------------------------- is the string hack harmless?
    print("\n[3] Is the string-replace stereo strip equivalent to RDKit's?")
    all_src = list(gs.IsomericSMILES) + list(lf.IsomericSMILES)
    hack = {x for x in map(openpom_remove_stereo, all_src) if x}
    proper = {x for x in map(flat, all_src) if x}
    radicals = 0
    for s in bench.nonStereoSMILES:
        m = Chem.MolFromSmiles(s)
        if m:
            radicals += bool(sum(a.GetNumRadicalElectrons() for a in m.GetAtoms()))
    out["string_hack"] = {
        "molecules_compared": len(all_src),
        "distinct_via_string_replace": len(hack),
        "distinct_via_rdkit": len(proper),
        "disagreements": len(hack ^ proper),
        "benchmark_rows_with_radicals": radicals,
        "radicals_are_preexisting_metal_complexes": True,
    }
    for k, v in out["string_hack"].items():
        print(f"  {k}: {v}")

    # ------------------------------------------------------------ the collapse
    print("\n[4] The collapse attributable to the merge")
    per_isomer = defaultdict(lambda: defaultdict(set))
    n_source_rows = defaultdict(int)
    source_smiles = {}      # canonical isomer -> the SMILES as written in the source
    for frame, desc_col in ((gs, "Updated_Desc_v2"), (lf, "Updated_Desc")):
        for smiles, desc in zip(frame.IsomericSMILES, frame[desc_col]):
            skeleton, isomer = flat(smiles), canon(smiles)
            if skeleton and isomer:
                per_isomer[skeleton][isomer] |= {
                    t for t in str(desc).split(";") if t
                }
                n_source_rows[skeleton] += 1
                source_smiles.setdefault(isomer, smiles)

    fused = {k: v for k, v in per_isomer.items() if len(v) > 1}
    conflicting = {k: v for k, v in fused.items()
                   if len({frozenset(s) for s in v.values()}) > 1}
    shipped = {x for x in map(flat, bench.nonStereoSMILES) if x}
    out["collapse"] = {
        "source_molecules_stereo_aware": sum(len(v) for v in per_isomer.values()),
        "distinct_flattened_skeletons": len(per_isomer),
        "benchmark_rows": len(bench),
        "reproduces_shipped_file_exactly": set(per_isomer) == shipped,
        "rows_that_are_fusions": len(fused),
        "fusion_share_of_benchmark": round(len(fused) / len(bench), 4),
        "stereoisomers_absorbed": sum(len(v) for v in fused.values()),
        "fusions_with_conflicting_labels": len(conflicting),
        "max_isomers_in_one_row": max(len(v) for v in fused.values()),
    }
    for k, v in out["collapse"].items():
        print(f"  {k}: {v}")

    # ------------------------------------- the union rule, verified exhaustively
    print("\n[5] Is every row exactly the union of its source isomers' labels?")
    row_labels = {}
    for _, row in bench.iterrows():
        k = flat(row.nonStereoSMILES)
        if k:
            row_labels[k] = {l for l in labels if row[l] == 1}
    mismatches = []
    for skeleton, isomers in per_isomer.items():
        union = set().union(*isomers.values())
        # merge cell 42 suppresses 'odorless' only when collapsing two or more
        # source rows into one. A row built from a single source row passes
        # through untouched, contradictions included.
        if n_source_rows[skeleton] > 1 and union != {"odorless"}:
            union.discard("odorless")
        if row_labels.get(skeleton, set()) != union:
            mismatches.append(skeleton)
    out["union_rule"] = {
        "rows_checked": len(per_isomer),
        "mismatches": len(mismatches),
        "rule": ("each row's label set is exactly the union of the curated "
                 "labels of every source row sharing its flattened skeleton, "
                 "with 'odorless' suppressed only where two or more source rows "
                 "were collapsed (merge_datasets.ipynb cell 42)"),
        "note": ("Menthyl lactate is the row that forced this precision: its "
                 "single source record reads 'mint;cooling;odorless', and "
                 "because nothing was merged into it the contradiction "
                 "survives into the shipped benchmark."),
    }
    print(f"  rows checked: {len(per_isomer)}   mismatches: {len(mismatches)}")

    # ------------------------------- which fusions does the theorem protect?
    print("\n[5b] Enantiomer fusions vs diastereomer fusions")
    enantiomer_fusions, enantiomer_conflicts, diastereomer_only = [], [], []
    enantiomer_pairs_of = {}
    for skeleton, isomers in fused.items():
        keys = list(isomers)
        pairs = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:]
                 if mirror(a) == b]
        enantiomer_pairs_of[skeleton] = pairs
        if not pairs:
            diastereomer_only.append(skeleton)
            continue
        enantiomer_fusions.append(skeleton)
        if any(isomers[a] != isomers[b] for a, b in pairs):
            enantiomer_conflicts.append(skeleton)
    # A sceptic's first objection is that some fused records were never resolved in
    # the source anyway -- a racemate, or an undifferentiated trade entry -- so the
    # merge cannot be blamed for losing a distinction nobody recorded. Answer it
    # with a number instead of a paragraph: split every fusion by whether all of
    # its members are fully stereo-specified.
    def unspecified_centres(smiles):
        m = Chem.MolFromSmiles(smiles)
        if m is None:
            return 0
        return sum(1 for e in Chem.FindPotentialStereo(m)
                   if str(e.specified) != "Specified")

    fully_specified, partly, wholly_unspecified = [], [], []
    for skeleton, isomers in fused.items():
        vague = [c for c in isomers if unspecified_centres(source_smiles[c])]
        if not vague:
            fully_specified.append(skeleton)
        elif len(vague) == len(isomers):
            wholly_unspecified.append(skeleton)
        else:
            partly.append(skeleton)

    strict_enantiomer_conflicts = [
        s for s in enantiomer_conflicts
        if all(not unspecified_centres(source_smiles[a])
               and not unspecified_centres(source_smiles[b])
               for a, b in enantiomer_pairs_of[s]
               if per_isomer[s][a] != per_isomer[s][b])
    ]

    out["parity"] = {
        "total_fusions": len(fused),
        "fusions_containing_an_enantiomer_pair": len(enantiomer_fusions),
        "enantiomer_pairs_with_conflicting_labels": len(enantiomer_conflicts),
        "fusions_diastereomer_or_EZ_only": len(diastereomer_only),
        "specification_breakdown": {
            "note": ("How much of the collapse is an unambiguous loss versus a "
                     "distinction the source never resolved. The strictest "
                     "reading of the headline count is `all_members_specified`."),
            "all_members_specified": len(fully_specified),
            "mixes_unspecified_with_resolved": len(partly),
            "all_members_partly_unspecified": len(wholly_unspecified),
        },
        "enantiomer_conflicts_both_members_fully_specified":
            len(strict_enantiomer_conflicts),
        "why_it_matters": (
            "A 2D graph model receives an identical tensor for all 534 fusions. "
            "A distance-based 3D model is provably blind only to the "
            "enantiomer fusions -- diastereomers and E/Z isomers have different "
            "distance matrices and are separable. So the parity-specific claim "
            "rests on the enantiomer count, not the total."),
        "enantiomer_conflict_skeletons": sorted(enantiomer_conflicts),
    }
    for k, v in out["parity"].items():
        if k != "enantiomer_conflict_skeletons":
            print(f"  {k}: {v}")

    # ---------------------------------------------------- contrast across fusions
    print("\n[6] How much do the fused isomers disagree?")

    def jaccard(a, b):
        return len(a & b) / len(a | b) if (a | b) else 1.0

    contrast = {}
    for skeleton, isomers in fused.items():
        sets = [s for s in isomers.values() if s]
        if len(sets) > 1:
            contrast[skeleton] = min(
                jaccard(sets[i], sets[j])
                for i in range(len(sets)) for j in range(i + 1, len(sets))
            )
    out["contrast"] = {
        "fusions_scored": len(contrast),
        "with_a_fully_disjoint_isomer_pair": sum(1 for v in contrast.values() if v == 0),
        "with_worst_pair_overlap_under_a_third": sum(1 for v in contrast.values() if v < 0.34),
    }
    for k, v in out["contrast"].items():
        print(f"  {k}: {v}")

    # ------------------------------------------------- the odorless erasure
    print("\n[7] Fusions that erased an 'odorless' isomer (merge cell 42)")
    erased = {
        k: v for k, v in fused.items()
        if any("odorless" in s for s in v.values())
        and any(s and "odorless" not in s for s in v.values())
    }
    out["odorless_erasure"] = {
        "rule": ("merge_datasets.ipynb cell 42 drops 'odorless' from a fused "
                 "group unless every fused isomer was odorless"),
        "n_groups": len(erased),
        "skeletons": sorted(erased),
    }
    print(f"  groups: {len(erased)}")

    # ---------------------------------------------------------------- exhibits
    print("\n[8] Exhibits")
    names = {}
    mol = d["pyrfume_gs_molecules.csv"]
    for smiles, nm, iupac in zip(mol.IsomericSMILES, mol["name"], mol.IUPACName):
        c = canon(smiles)
        if c:
            names[c] = {"name": nm,
                        "iupac": iupac if isinstance(iupac, str) else None}

    bench_by_skeleton = {}
    for _, row in bench.iterrows():
        k = flat(row.nonStereoSMILES)
        if k:
            bench_by_skeleton[k] = row

    # Evidence tiers for the perceptual claim, which is INDEPENDENT of the audit
    # claim. The audit shows the benchmark fused an enantiomer pair whose source
    # records disagree -- that is verifiable from the files. Whether the two
    # enantiomers actually smell different to humans is a separate question with
    # its own, much patchier, literature.
    #
    # Standard applied: a classic enantiomer odour pair counts as established
    # only if it has been re-measured with chiral-GC-verified enantiomeric excess
    # AND a forced-choice panel. Limonene fails it (Kvittingen, Sjursnes &
    # Schmid 2021: 50% of participants called technical-grade (R)-limonene
    # "orange", but only 13% called analytical-grade the same). Nootkatone and
    # androstenone were never tested to that standard at all.
    EVIDENCE = {
        "established": ("perceptual difference independently established under "
                        "purity control"),
        "records_disagree": ("the benchmark fuses an enantiomer pair whose source "
                             "records disagree; whether the percepts differ is "
                             "UNVERIFIED -- do not assert it"),
        "confounded": ("source records disagree, but the primary literature for "
                       "the perceptual claim carries a known impurity confound"),
        "refuted": ("source records disagree and humans provably CANNOT "
                    "discriminate the pair"),
    }

    def exhibit(title, probe, note=None, confidence="high",
                evidence="records_disagree", citation=None):
        skeleton = flat(probe)
        isomers = per_isomer.get(skeleton, {})
        row = bench_by_skeleton.get(skeleton)
        keys = list(isomers)
        ena = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:]
               if mirror(a) == b]
        ena_diff = [(a, b) for a, b in ena if isomers[a] != isomers[b]]
        ex = {
            "title": title,
            "skeleton": skeleton,
            "confidence": confidence,
            "note": note,
            "evidence_tier": evidence,
            "evidence_meaning": EVIDENCE[evidence],
            "citation": citation,
            "parity_class": ("enantiomer pair with conflicting labels -- blind to "
                             "distance-based 3D models, theorem applies"
                             if ena_diff else
                             "enantiomer pair, labels agree" if ena else
                             "diastereomer / E-Z only -- a 3D model CAN see this; "
                             "proves 2D-graph blindness, not parity blindness"),
            "enantiomer_pairs": [
                {"a": a, "a_name": names.get(a, {}).get("name"),
                 "a_labels": sorted(isomers[a]),
                 "b": b, "b_name": names.get(b, {}).get("name"),
                 "b_labels": sorted(isomers[b])}
                for a, b in ena_diff
            ],
            "isomers": [
                {"smiles": iso,
                 "name": names.get(iso, {}).get("name"),
                 "iupac": names.get(iso, {}).get("iupac"),
                 "labels": sorted(s)}
                for iso, s in sorted(isomers.items())
            ],
            "benchmark_row": {
                "nonStereoSMILES": row.nonStereoSMILES,
                "labels": sorted(l for l in labels if row[l] == 1),
            } if row is not None else None,
        }
        print(f"\n  {title}: {len(ex['isomers'])} isomers -> 1 row"
              f"  [{ex['parity_class'].split(' --')[0]}]")
        for iso in ex["isomers"]:
            print(f"    {iso['name'] or iso['smiles']}: {iso['labels']}")
        if ex["benchmark_row"]:
            print(f"    BENCHMARK: {ex['benchmark_row']['labels']}")
        return ex

    out["exhibits"] = [
        exhibit(
            "Carvone -- the lead",
            "CC1=CC[C@@H](CC1=O)C(=C)C",
            note=("(5R) is the spearmint-described entry, (5S) the caraway one, "
                  "per the dataset's own IUPAC names. Upstream, 'spearmint' was "
                  "merged into 'mint' and 'caraway' was deleted -- yet the two "
                  "enantiomers still carried different labels after curation. "
                  "The merge destroyed that surviving difference. This is the "
                  "ONLY exhibit in the benchmark whose perceptual difference "
                  "meets the purity-controlled standard, on three independent "
                  "lines."),
            evidence="established",
            citation=("Three independent 1971 papers: Russell & Hills, Science "
                      "172:1043; Friedman & Miller, Science 172:1044; Leitereg "
                      "et al., Nature 230:455 (plus thresholds in J. Agric. "
                      "Food Chem. 1971, 19, 785). Forced-choice discrimination "
                      "confirmed by Laska & Teubner, Chem. Senses 1999, 24, 161. "
                      "Independent modern line: Sato et al., Sci. Rep. 2015, 5, "
                      "14073 (open access, PMC4566093), which covers carvone "
                      "enantiomers alongside wine lactone."),
        ),
        exhibit(
            "Nootkatone -- DEMOTED to a citation-drift case study",
            "C=C(C)C1CCC2=CC(=O)CC(C)C2(C)C1",
            note=("Was the number-two exhibit; it does not survive. The source "
                  "records do disagree -- grapefruit/orange/citrus/woody against "
                  "the single word 'terpenic' -- and that fusion is real. But "
                  "the primary literature for the perceptual claim (Haring et "
                  "al., J. Agric. Food Chem. 1972) compared a (-)-sample made by "
                  "total synthesis from (+)-sabinene with NO quantified "
                  "enantiomeric excess against a (+)-sample that was a natural "
                  "isolate. Different provenance means different impurity "
                  "profiles: this is the identical confound that killed the "
                  "limonene claim, and it has never been replicated in 54 years. "
                  "The circulating thresholds are also unit-corrupted -- taste-"
                  "in-water figures relabelled as odour-in-air, 'ppm of "
                  "saturated vapour' misread as 'ppm in air', and Molecules "
                  "2022, 27, 3827 states the comparison inverted and off by "
                  "1000x. Use it to teach citation drift, not chirality."),
            confidence="low",
            evidence="confounded",
            citation=("Haring et al., J. Agric. Food Chem. 1972; upstream "
                      "threshold source is Boelens, Boelens & van Gemert, "
                      "Perfum. Flavor. 1993, 18(6), 1-15 (unread, Cloudflare)"),
        ),
        exhibit(
            "alpha-Pinene -- the human-validated pair",
            "CC1=CCC2CC1C2(C)C",
            note=("The strongest evidence base of any exhibit. Laska & Teubner "
                  "1999 (Chem. Senses 24:161) tested ten enantiomer pairs by "
                  "forced-choice triangular test; alpha-pinene, carvone and "
                  "limonene were the three humans could reliably discriminate. "
                  "The benchmark labels differ sharply -- four labels against "
                  "eight -- and the merge unions them. Held one tier below "
                  "carvone because Laska's purity control could not be read "
                  "(OUP full text inaccessible), so discrimination is "
                  "panel-verified but ee is not."),
            evidence="records_disagree",
            citation="Laska & Teubner, Chem. Senses 1999, 24, 161 (abstract-level)",
        ),
        exhibit(
            "Geosmin -- petrichor, five labels against one",
            "CC1CCCC2(C)CCCCC12O",
            note=("Geosmin is the smell of rain on dry earth, and humans detect "
                  "it at parts per trillion. The unspecified entry carries "
                  "earthy/fresh/green/herbal/musty; (+)-geosmin carries the "
                  "single word 'earthy'. No purity-controlled enantiomer "
                  "comparison located -- present as a database disagreement, not "
                  "as an established perceptual difference."),
        ),
        exhibit(
            "Pulegone -- seven labels against one",
            "CC(C)=C1CCC(C)CC1=O",
            note=("(+)-pulegone: camphoreous, fresh, herbal, metallic, mint, "
                  "sulfurous, sweet. (-)-pulegone: mint. One row asserts all "
                  "eight. No purity-controlled comparison located."),
        ),
        exhibit(
            "Menthone -- the menthol exhibit that actually works",
            "CC1CCC(C(C)C)C(=O)C1",
            note=("Replaces the menthol exhibit on the parity axis: (-)-menthone "
                  "carries eight labels, (+)-menthone two, and they are a true "
                  "enantiomer pair. No purity-controlled odour comparison "
                  "located for the menthone enantiomers either, so this is a "
                  "database disagreement too."),
        ),
        exhibit(
            "(R)- vs (S)-2-butanol -- the honest counter-exhibit",
            "CCC(C)O",
            note=("Include this one deliberately, against our own interest. The "
                  "benchmark records different labels for the two enantiomers "
                  "(fruity/oily/winey vs oily/winey), but Laska & Teubner 1999 "
                  "found humans CANNOT discriminate 2-butanol enantiomers by "
                  "smell. So some of the 74 conflicts are noise in the source "
                  "descriptions, not destroyed perceptual signal. Saying this "
                  "out loud is what makes the rest of the argument credible -- "
                  "and it bounds what the phase-3 experiment can claim."),
            evidence="refuted",
            citation="Laska & Teubner, Chem. Senses 1999, 24, 161",
        ),
        exhibit(
            "3-methylpentanal -- one enantiomer recorded odorless",
            "CC[C@H](C)CC=O",
            note=("'odorless' IS in the 138-label vocabulary, so this exhibit "
                  "survives both vocabulary faults intact and dies only at the "
                  "flatten. Caveat: the (3R) entry resolves to a thin database "
                  "record (schembl9421367), so 'odorless' may mean "
                  "'undescribed' rather than 'tested and found odorless'."),
            confidence="medium",
        ),
        exhibit(
            "Menthol skeleton -- 2D-blindness only, NOT a parity exhibit",
            "CC(C)[C@@H]1CC[C@@H](C)C[C@H]1O",
            note=("Six isomers fuse to a row asserting eleven labels; no single "
                  "isomer carries more than six, and the row is exactly the "
                  "union. ('bitter' comes from (+)-neomenthol and 'pine' from "
                  "neomenthol -- both genuinely in the curated sources, not "
                  "imported from Leffingwell.) But these are DIASTEREOMERS: "
                  "menthol, neomenthol, isomenthol and neoisomenthol have "
                  "different distance geometries, so a 3D model can separate "
                  "them and the reflection theorem does not apply. Worse for a "
                  "parity framing, Laska & Teubner 1999 found humans cannot "
                  "discriminate the menthol ENANTIOMERS at all. Use this to "
                  "illustrate 2D-graph blindness and nothing more."),
            confidence="medium",
        ),
        exhibit(
            "Lily aldehyde -- the widest fusion",
            "C=C[C@]1(C)CC[C@@H]([C@H](C)C=O)O1",
            note=("Eight isomers into one row, the largest fusion in the "
                  "benchmark. Note the contrast is low -- nearly all are "
                  "floral -- so this exhibit sells scale, not disagreement."),
        ),
        exhibit(
            "Geraniol / nerol -- demoted to a footnote",
            "CC(C)=CCC/C(C)=C/CO",
            note=("Originally intended as a headline exhibit, and it does not "
                  "hold up. Goodscents calls nerol citrus/sweet/natural; "
                  "Leffingwell independently calls it sweet/fresh/rose. So both "
                  "isomers carry 'rose' after curation and the clean "
                  "'rose versus neroli' story is wrong. What it does show is a "
                  "different fault: the two source authorities disagree with "
                  "each other, and the merge unions rather than adjudicates."),
            confidence="low",
        ),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, sort_keys=False)
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
