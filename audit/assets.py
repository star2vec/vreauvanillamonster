"""
Build the visual assets the explainer page needs, offline, from RDKit.

Reads the exhibit list out of out/audit.json so the figures cannot drift away from
the numbers, and writes out/assets.json plus out/figures/*.svg.

Three things get produced:

1. 2D depictions of every exhibit isomer, with wedge/hash stereo bonds and CIP
   annotations, as standalone SVG.
2. A 3D coordinate pair for carvone built so that the two molecules are EXACT
   mirror images sharing atom ordering -- the payload for the theorem widget.
3. The distance matrices of that pair, which are identical, and the signed volume
   at the stereocentre, which is not.

The point of (2) and (3) together: the distance matrix is what a distance-based
model sees, and it cannot tell the two apart. The signed volume is the cheapest
quantity that can.
"""

import json
import re
from pathlib import Path

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, rdCIPLabeler, rdDepictor, rdDistGeom
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Geometry import Point3D

RDLogger.DisableLog("rdApp.*")

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out"
FIGURES = OUT / "figures"

# The lead exhibit, whose enantiomers drive the 3D widget. (5R) is the entry the
# source described as spearmint; (5S) is the caraway one.
CARVONE_R = "CC1=CC[C@H](CC1=O)C(=C)C"
CARVONE_S = "CC1=CC[C@@H](CC1=O)C(=C)C"


def slug(text):
    keep = [c if c.isalnum() else "-" for c in text.lower()]
    return "".join(keep).strip("-").replace("---", "-").replace("--", "-")


def depict(smiles, width=340, height=290):
    """One molecule, one SVG, stereo bonds drawn and CIP labels annotated.

    Returns (svg, wedged_bonds, cip_labels_drawn) so the caller can verify that
    stereochemistry actually made it into the picture. A chirality explainer whose
    figures silently lose their wedges would be worse than useless.

    noFreetype=True emits real <text> nodes rather than rendering glyphs to
    <path>. Smaller, reachable by screen readers, and it makes the CIP annotation
    checkable. The only glyphs here are atom symbols and "(R)"/"(S)", so there is
    no exotic-font risk in exchange.
    """
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None, 0, []
    # rdCIPLabeler is the accurate CIP implementation. The legacy
    # Chem.AssignStereochemistry codes are only reliable for simple cases.
    rdCIPLabeler.AssignCIPLabels(m)
    rdDepictor.SetPreferCoordGen(True)
    rdDepictor.Compute2DCoords(m)
    d = rdMolDraw2D.MolDraw2DSVG(width, height, -1, -1, True)
    opts = d.drawOptions()
    opts.addStereoAnnotation = True      # singular; the plural name does not exist
    opts.clearBackground = False         # let the page's own theme show through
    rdMolDraw2D.PrepareAndDrawMolecule(d, m)
    d.FinishDrawing()
    svg = d.GetDrawingText()

    # Ground truth for "is stereo drawn". The two kinds are drawn by completely
    # different mechanisms and must be checked separately: tetrahedral centres get
    # BEGINWEDGE/BEGINDASH bond directions, whereas double-bond E/Z is conveyed
    # purely by the geometry of the layout and never produces a wedge.
    prepared = rdMolDraw2D.PrepareMolForDrawing(Chem.MolFromSmiles(smiles))
    wedged = sum(1 for b in prepared.GetBonds()
                 if str(b.GetBondDir()) in ("BEGINWEDGE", "BEGINDASH"))
    ez = sum(1 for b in prepared.GetBonds()
             if str(b.GetStereo()) in ("STEREOE", "STEREOZ",
                                       "STEREOCIS", "STEREOTRANS"))
    cip = re.findall(r"\(([RSrsEZ])\)",
                     "".join(re.findall(r"<text[^>]*>(.*?)</text>", svg)))
    return svg, wedged, ez, cip


def stereocentres(mol):
    """Assigned tetrahedral centres, with the neighbour ordering RDKit used.

    `controllingAtoms` gives a deterministic neighbour order, which matters
    because the sign of a triple product flips under any odd permutation of its
    inputs. Never take whatever order the data structure happens to hold.
    """
    out = []
    for info in Chem.FindPotentialStereo(mol):
        if str(info.type) != "Atom_Tetrahedral":
            continue
        out.append({
            "atom": int(info.centeredOn),
            "specified": str(info.specified) == "Specified",
            "descriptor": str(info.descriptor),
            "controlling_atoms": [int(a) for a in info.controllingAtoms],
        })
    return out


def signed_volume(mol, centre, neighbours, conf_id=-1):
    """The parity-odd quantity: sign of the triple product about a stereocentre.

    A rotation leaves this unchanged; a reflection negates it. That asymmetry is
    the entire reason a parity-aware model can do what a distance-based one
    provably cannot.
    """
    pos = mol.GetConformer(conf_id).GetPositions()
    v = [pos[i] - pos[centre] for i in neighbours[:3]]
    return float(np.dot(np.cross(v[0], v[1]), v[2]))


def mirror_pair(smiles, seed=0xF00D):
    """A molecule and its exact mirror image, sharing atom ordering.

    Embed once, copy, negate one axis. Do NOT re-optimise the reflection: MMFF
    would relax it into a different torsional minimum and the distance matrices
    would stop matching.

    This construction matters more than it looks. Two INDEPENDENTLY embedded
    enantiomers differ by over 1 angstrom in their distance matrices, because
    ETKDG and MMFF settle into different torsional minima at flexible remote
    groups. That is a conformer artefact, not a counterexample to the theorem --
    but a widget built that way would appear to refute the very claim it exists
    to demonstrate.
    """
    a = Chem.AddHs(Chem.MolFromSmiles(smiles))
    ps = rdDistGeom.ETKDGv3()
    ps.randomSeed = seed
    if rdDistGeom.EmbedMolecule(a, ps) != 0:
        raise RuntimeError(f"could not embed {smiles}")
    AllChem.MMFFOptimizeMolecule(a, maxIters=2000)

    b = Chem.Mol(a)
    conf = b.GetConformer()
    pos = conf.GetPositions().copy()
    pos[:, 0] *= -1.0
    for i, xyz in enumerate(pos):
        conf.SetAtomPosition(i, Point3D(*xyz))
    Chem.AssignStereochemistryFrom3D(b)
    return a, b


def describe_3d(mol, label):
    """Serialise a conformer for the page: atoms, bonds, and its stereo readout."""
    conf = mol.GetConformer()
    pos = conf.GetPositions()
    heavy = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() > 1]
    centres = [c for c in stereocentres(mol) if c["specified"]]
    for c in centres:
        c["signed_volume"] = signed_volume(mol, c["atom"], c["controlling_atoms"])

    rdCIPLabeler.AssignCIPLabels(mol)
    cip = {a.GetIdx(): a.GetPropsAsDict().get("_CIPCode")
           for a in mol.GetAtoms() if a.HasProp("_CIPCode")}

    return {
        "label": label,
        "smiles": Chem.MolToSmiles(Chem.RemoveHs(mol)),
        "cip": {str(k): v for k, v in cip.items()},
        "atoms": [
            {"i": a.GetIdx(), "el": a.GetSymbol(),
             "xyz": [round(float(x), 4) for x in pos[a.GetIdx()]],
             "heavy": a.GetAtomicNum() > 1}
            for a in mol.GetAtoms()
        ],
        "bonds": [
            {"i": b.GetBeginAtomIdx(), "j": b.GetEndAtomIdx(),
             "order": b.GetBondTypeAsDouble()}
            for b in mol.GetBonds()
        ],
        "heavy_atom_indices": heavy,
        "stereocentres": centres,
    }


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    audit = json.loads((OUT / "audit.json").read_text())
    assets = {}

    # ---------------------------------------------------------------- 2D figures
    print("[1] 2D depictions")
    figures, seen, missing_stereo = [], set(), []
    for ex in audit["exhibits"]:
        for iso in ex["isomers"]:
            smi = iso["smiles"]
            if smi in seen:
                continue
            seen.add(smi)
            svg, wedged, ez, cip = depict(smi)
            if svg is None:
                print(f"  !! could not parse {smi}")
                continue
            # A figure must not lie about its molecule. Tetrahedral stereo has to
            # show up as a wedge or hash; double-bond stereo has to show up as an
            # assigned E/Z bond. Checked separately, because they are drawn by
            # entirely different mechanisms.
            if "@" in smi and wedged == 0:
                missing_stereo.append((iso["name"], smi, "tetrahedral, no wedge"))
            if ("/" in smi or "\\" in smi) and ez == 0:
                missing_stereo.append((iso["name"], smi, "E/Z, no assigned bond"))
            name = iso["name"] or ex["title"].split(" --")[0]
            path = FIGURES / f"{slug(name)}-{len(figures):02d}.svg"
            path.write_text(svg)
            figures.append({
                "smiles": smi, "name": iso["name"],
                "exhibit": ex["title"], "labels": iso["labels"],
                "file": str(path.relative_to(OUT)),
                "wedge_or_hash_bonds": wedged, "ez_bonds": ez,
                "stereo_labels_drawn": cip,
            })
    assets["figures"] = figures
    print(f"  wrote {len(figures)} SVGs to {FIGURES.relative_to(OUT.parent)}")
    print(f"  {sum(1 for f in figures if f['wedge_or_hash_bonds'])} with a wedge or "
          f"hash bond, {sum(1 for f in figures if f['ez_bonds'])} with an E/Z bond, "
          f"{sum(1 for f in figures if not f['wedge_or_hash_bonds'] and not f['ez_bonds'])}"
          " with no stereochemistry to draw")
    if missing_stereo:
        raise AssertionError(
            f"figures that lose their stereochemistry: {missing_stereo}")

    # -------------------------------------------------- the 3D mirror pair
    print("\n[2] carvone mirror pair")
    a, b = mirror_pair(CARVONE_R)
    pair = [describe_3d(a, "A"), describe_3d(b, "B (reflected)")]
    for p in pair:
        cip = ",".join(f"{k}:{v}" for k, v in p["cip"].items()) or "-"
        sv = ", ".join(f"{c['signed_volume']:+.6f}" for c in p["stereocentres"])
        print(f"  {p['label']:14s} {p['smiles']:34s} CIP {cip:8s} signed volume {sv}")

    sv_a = pair[0]["stereocentres"][0]["signed_volume"]
    sv_b = pair[1]["stereocentres"][0]["signed_volume"]
    assert pair[0]["smiles"] != pair[1]["smiles"], "reflection did not change the molecule"
    assert abs(sv_a + sv_b) < 1e-9, f"signed volumes are not parity-odd: {sv_a}, {sv_b}"

    # ------------------------------------------- the distance matrices
    print("\n[3] distance matrices")
    dm_a = Chem.Get3DDistanceMatrix(a, force=True)
    dm_b = Chem.Get3DDistanceMatrix(b, force=True)
    delta = float(np.max(np.abs(dm_a - dm_b)))
    print(f"  full ({dm_a.shape[0]} atoms, hydrogens included): max|dA - dB| = {delta:.3e}")
    assert delta == 0.0, (
        f"distance matrices differ by {delta}. This is a bug in the asset builder, "
        "not a problem with the theorem: either the reflection was re-optimised or "
        "atom ordering diverged."
    )

    heavy = pair[0]["heavy_atom_indices"]
    dm_heavy = dm_a[np.ix_(heavy, heavy)]
    print(f"  heavy-atom view for display: {dm_heavy.shape[0]}x{dm_heavy.shape[0]}")

    # The counterexample the page needs in order not to mislead. Embedding the two
    # enantiomers SEPARATELY gives distance matrices that differ substantially --
    # not because the theorem fails, but because ETKDG and MMFF settle into
    # different torsional minima at the flexible remote groups. A reader who tried
    # to reproduce the widget the naive way would conclude we were wrong, so the
    # page states this number and we measure it ourselves rather than cite it.
    naive = []
    for smi in (CARVONE_R, CARVONE_S):
        m = Chem.AddHs(Chem.MolFromSmiles(smi))
        ps = rdDistGeom.ETKDGv3()
        ps.randomSeed = 0xF00D
        rdDistGeom.EmbedMolecule(m, ps)
        AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
        naive.append(m)
    order_matches = ([a.GetSymbol() for a in naive[0].GetAtoms()]
                     == [a.GetSymbol() for a in naive[1].GetAtoms()])
    naive_delta = float(np.max(np.abs(
        Chem.Get3DDistanceMatrix(naive[0], force=True)
        - Chem.Get3DDistanceMatrix(naive[1], force=True))))
    print(f"  independently embedded enantiomers, same seed, atom order "
          f"{'matches' if order_matches else 'DIFFERS -- comparison invalid'}: "
          f"max|dA - dB| = {naive_delta:.3f} A")
    assert order_matches, "atom ordering diverged; the naive comparison is meaningless"
    assert naive_delta > 0.5, (
        "independent embedding was expected to differ substantially; if it no longer "
        "does, the conformational-flexibility section needs rewriting")

    assets["mirror_pair"] = {
        "molecule": "carvone",
        "note": ("Built by embedding once and reflecting, so the two share atom "
                 "ordering and are exact mirror images. Independently embedded "
                 "enantiomers would differ by over 1 angstrom through conformer "
                 "artefacts alone."),
        "molecules": pair,
        "distance_matrix_identical": delta == 0.0,
        "distance_matrix_max_abs_difference": delta,
        "naive_independent_embedding_max_abs_difference": naive_delta,
        "naive_note": ("Embedding the two enantiomers separately instead of reflecting "
                       "one conformer gives this much disagreement, from torsional "
                       "minima rather than from any failure of the theorem. Stated on "
                       "the page so a reader reproducing it the naive way is not "
                       "misled."),
        "heavy_atom_labels": [a.GetSymbol() + str(i)
                              for i, a in zip(heavy, [a.GetAtomWithIdx(h) for h in heavy])],
        "distance_matrix_heavy": [[round(float(x), 4) for x in row] for row in dm_heavy],
        "signed_volumes": {"A": sv_a, "B": sv_b},
    }

    (OUT / "assets.json").write_text(json.dumps(assets, indent=2))
    print(f"\nWrote {OUT / 'assets.json'}")


if __name__ == "__main__":
    main()
