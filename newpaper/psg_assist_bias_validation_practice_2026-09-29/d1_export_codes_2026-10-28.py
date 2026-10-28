"""Export the two blind coders' codes (D1) to one CSV beside the reconciled first-round codes.

Usage: python -X utf8 d1_export_codes.py <DEVICES.csv (first-round codes, before adjudication edits)>
         <coder1.xlsx> <initials1> <seen1> <coder2.xlsx> <initials2> <seen2> <out.csv>
seenN = Code-tab row numbers (1-based, e.g. 1-10) the coder had checked in the first round.
Codes are written in the DEVICES.csv vocabulary. Aggregate coding data only.
"""
import csv
import re
import sys

import openpyxl

REF = {"independent_experts": "Independent experts",
       "expert_consensus_details_limited": "Consensus, independence not stated",
       "routine_clinical_scoring": "Routine clinical scoring",
       "daily_practice_panel": "Daily-practice panel",
       "algorithm_reference": "Another algorithm's output",
       "not_described": "Not described"}
BLIND = {"explicit": "Explicit", "implied by design": "Implied by design",
         "stated (object unspecified)": "Stated, object unspecified", "not stated": "Not stated",
         "not applicable": "Not applicable"}
PRE = {"not said": "Not said", "says they did": "Says they did",
       "says they did not": "Says they did not (any software)",
       "device output only": "Says they did not (only this device's output)",
       "not applicable": "Not applicable"}
FIELDS = [("reference_type", 7, REF), ("blinding_to_device_output", 9, BLIND), ("prescoring_reported", 11, PRE)]


def norm(s):
    s = str(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def parse_rows(spec):
    out = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return out


def load(xlsx):
    ws = openpyxl.load_workbook(xlsx, data_only=True)["Code"]
    return [[c.value for c in r] for r in ws.iter_rows(min_row=2) if r[1].value]


def main():
    devices_csv, x1, i1, s1, x2, i2, s2, out = sys.argv[1:9]
    devices = {r["k_number"]: r for r in csv.DictReader(open(devices_csv, encoding="utf-8"))}
    coders = [(load(x1), i1, parse_rows(s1)), (load(x2), i2, parse_rows(s2))]
    assert [r[1] for r in coders[0][0]] == [r[1] for r in coders[1][0]]
    rows_out = []
    for i, row in enumerate(coders[0][0], start=1):
        k, device = row[1], row[3]
        for field, col, mapping in FIELDS:
            inverse = {norm(label): code for code, label in mapping.items()}
            rec = {"row": i, "k_number": k, "device": device, "field": field,
                   "first_round_code": devices[k][field]}
            for rows, initials, seen in coders:
                label = rows[i - 1][col]
                code = inverse.get(norm(label))
                if code is None:
                    sys.exit(f"unmapped label {label!r} for {k} {field} ({initials})")
                rec[f"{initials}_code"] = code
                rec[f"{initials}_exposure"] = "seen" if i in seen else "blind"
            rows_out.append(rec)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0]))
        w.writeheader()
        w.writerows(rows_out)
    print(f"wrote {len(rows_out)} rows to {out}")
    for r in rows_out:
        if r[f"{i1}_code"] != r["first_round_code"] or r[f"{i2}_code"] != r["first_round_code"]:
            print("  disagreement:", r["row"], r["k_number"], r["field"], "first", r["first_round_code"],
                  "|", i1, r[f"{i1}_code"], r[f"{i1}_exposure"], "|", i2, r[f"{i2}_code"], r[f"{i2}_exposure"])


if __name__ == "__main__":
    main()
