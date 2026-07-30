"""
Does the Leffingwell curation lose or conflate concentration-dependent odour
descriptions? Measured, not estimated -- and the answer is essentially no.

Many raw Leffingwell records qualify a descriptor by concentration ("on dilution a
blue cheese nuance"). Since the benchmark's labels are binary and carry no
intensity dimension, I expected that information to be either discarded or merged
into a single vector asserting both regimes at once. Two cases are possible:

  A. the dilution clause sits after the first semicolon, and
     correct_spell_errors_v1 truncates there -- so it is dropped
  B. the dilution qualifier sits inside the first clause, so words from both
     regimes land in the same label set

Result: A = 23, B = 8, out of 3,510 molecules. Negligible. An earlier crude
approximation of mine suggested ~37 for case B and I had loosely described 221
records as affected; both were wrong. The effect is real but far too small to
carry an argument, and the page treats it as illustration at most.

The reason it is small is worth recording: the pipeline unions the text-derived
descriptors with a pre-existing `Labels` column that Sanchez-Lengeling et al. had
already cleaned from the full description, so most information lost to the
semicolon truncation is recovered from there.

What this script does establish, and what makes it worth keeping: a 99.97%-faithful
reimplementation of the Leffingwell curation, which independently confirms we
understand that pipeline end to end.
"""

import ast
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
# The notebook is not vendored here; point this at a clone of
# https://github.com/BioMachineLearning/openpom to re-run.
NOTEBOOK_ENV = "OPENPOM_CLONE"

DILUTION = re.compile(
    r"\b(on dilution|in dilution|upon dilution|when diluted|diluted|dilution)\b",
    re.I)


def load_curation_logic(notebook):
    """Execute the curation cells verbatim rather than paraphrasing them.

    Paraphrasing is how I got this wrong the first time: the real clean_desc does
    exact word matching, and my approximation used stem matching, which
    hallucinated `odorless` out of the word "odor".
    """
    nb = json.loads(Path(notebook).read_text())
    ns = {}
    # required_desc, spellcorrect, correct_spell_errors_v1, merger_root_dict,
    # clean_desc, update_desc, handle_odorless, get_req_desc
    for i in (4, 28, 29, 34, 35, 40, 43, 50):
        src = "\n".join(
            line for line in "".join(nb["cells"][i]["source"]).split("\n")
            if not re.match(
                r"\s*(behavior|molecules|mol_behaviors|print|display|odor_list|odors_df)",
                line))
        exec(src, ns)
    # cell 49: Leffingwell drops 'cortex', so it uses 137 descriptors, not 138
    ns["required"] = {d for d in ns["required_desc"] if d != "cortex"}
    return ns


def main(notebook):
    ns = load_curation_logic(notebook)
    fix, clean = ns["correct_spell_errors_v1"], ns["clean_desc"]
    update, odorless, REQ = ns["update_desc"], ns["handle_odorless"], ns["required"]

    sparse = pd.read_csv(DATA / "pyrfume_lf_behavior_sparse.csv")
    mols = pd.read_csv(DATA / "pyrfume_lf_molecules.csv")
    curated = pd.read_csv(DATA / "curated_leffingwell.csv")

    def prior(v):
        """The `Labels` column is a Python list literal, not a ';'-joined string.
        Concatenating it raw was the bug that stalled validation at 85.8%."""
        try:
            return ";".join(ast.literal_eval(str(v)))
        except (ValueError, SyntaxError):
            return ""

    def pipeline(raw, labels):
        merged = update(prior(labels), clean(fix(str(raw))))
        return {d for d in odorless(merged).split(";") if d in REQ}

    def from_text(text):
        got = clean(fix(text))
        return {d for d in (got or "").split(";") if d in REQ}

    print("[1] Validating the reimplementation against curated_leffingwell.csv")
    mine = [pipeline(r, l) for r, l in zip(sparse["Raw Labels"], sparse["Labels"])]
    smiles = sparse.Stimulus.map(dict(zip(mols.CID, mols.IsomericSMILES)))
    theirs = {s: {x for x in str(d).split(";") if x}
              for s, d in zip(curated.IsomericSMILES, curated.Updated_Desc)}
    ok = sum(1 for s, m in zip(smiles, mine) if s in theirs and theirs[s] == m)
    bad = sum(1 for s, m in zip(smiles, mine) if s in theirs and theirs[s] != m)
    print(f"    exact match {ok}  mismatch {bad}  -> {ok / (ok + bad):.2%} reproduced")
    if ok / (ok + bad) < 0.97:
        raise AssertionError(
            "reimplementation is not faithful; the counts below would be worthless")

    print("\n[2] Case A -- dilution-only odour info lost to the semicolon truncation,"
          "\n    and not recovered from the pre-existing Labels column")
    a, examples_a = 0, []
    for raw, labels in zip(sparse["Raw Labels"].astype(str), sparse["Labels"]):
        parts = raw.split(";")
        if len(parts) < 2 or not DILUTION.search(";".join(parts[1:])):
            continue
        lost = (from_text(";".join(parts[1:])) - from_text(parts[0])
                - {d for d in prior(labels).split(";") if d in REQ})
        if lost:
            a += 1
            if len(examples_a) < 5:
                examples_a.append((raw, sorted(lost)))
    print(f"    count: {a} / {len(sparse)}")
    for raw, lost in examples_a:
        print(f"      {raw[:84]}\n        lost: {lost}")

    print("\n[3] Case B -- neat and diluted descriptors merged into one label vector")
    b, examples_b = 0, []
    for raw in sparse["Raw Labels"].astype(str):
        head = raw.split(";")[0]
        m = DILUTION.search(head)
        if not m:
            continue
        neat, diluted = from_text(head[:m.start()]), from_text(head[m.end():])
        if neat and (diluted - neat):
            b += 1
            if len(examples_b) < 5:
                examples_b.append((head, sorted(neat), sorted(diluted - neat)))
    print(f"    count: {b} / {len(sparse)}")
    for head, neat, extra in examples_b:
        print(f"      {head[:84]}\n        neat {neat}  +diluted {extra}")

    print(f"\nVERDICT: {a} + {b} of {len(sparse)}. Too small to carry an argument."
          "\nThe concentration leg of the ceiling rests on the metadata being"
          "\ndiscarded wholesale (4,137 of 4,626 stimuli), not on this.")


if __name__ == "__main__":
    import os
    import sys
    clone = os.environ.get(NOTEBOOK_ENV) or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not clone:
        sys.exit(f"set {NOTEBOOK_ENV} or pass the path to an openpom clone")
    main(Path(clone) / "openpom" / "data" / "leffingwell_dataset_curation.ipynb")
