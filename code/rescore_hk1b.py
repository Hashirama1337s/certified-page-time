"""rescore_hk1b - re-score result_hk1b.json with the AMEND-HK-1-1 rounding intervals (referee-1 fix F6).  New file.

hk1_cert.ph1() (imported by hk1b_cert) tested the beta enclosure against the POINT values 1.48472 / 1.48471.
AMEND-HK-1-1 reads every printed value as the interval of numbers that round to it (half a unit in the last printed
digit).  This script reads only result_hk1b.json (no recomputation) and applies, with arb:
  containment  : enclosure overlaps the rounding interval of the bar value (PH1, PH2 items, PH3)
  exclusion    : enclosure is disjoint from the rounding interval of each printed beta (PH1)
  width        : 2 rad / |mid| <= 1e-8
  PH3 extra    : enclosure strictly inside Newton's [3.8262e-6, 3.8639e-6]
PH4, PH5, PH6 are copied (they do not involve printed rounded values).  Writes rescore_hk1b.json.
"""
import json, os, sys, hashlib
from flint import arb, ctx

HERE = os.path.dirname(os.path.abspath(__file__))
BAR = {"beta": "1.4846916919", "P_1": "3.3638547856e-5", "alpha": "3.7475287781e-5", "Sdot_1": "1.2683659541e-3",
       "Sdot_2": "1.3000087862e-4", "page_time": "0.5381024532", "P_2": "3.8367399250e-6"}     # BAR-HK-1b l.20-27
PRINTED_BETA = {"Page 2013": "1.48472", "Perez-Gonzalez 2025": "1.48471"}
NEWTON = ("3.8262e-6", "3.8639e-6")


def rounding_interval(s):
    mant, _, ex = s.lower().partition("e")
    ex = int(ex) if ex else 0
    dec = len(mant.split(".")[1]) if "." in mant else 0
    half = arb(5) * arb(10) ** (ex - dec - 1)
    v = arb(s)
    return arb(v, (half + v.rad()).upper()), (v - half), (v + half)


def width(x):
    return float((2 * x.rad() / abs(x).lower()).upper())


def main(path=os.path.join(HERE, "result_hk1b.json")):
    old = ctx.prec
    ctx.prec = 256
    try:
        raw = open(path, "rb").read()
        d = json.loads(raw)
        vals = {k: arb(v) for k, v in d["values"].items()}
        out = {"source": path, "source_sha256": hashlib.sha256(raw).hexdigest(), "rule": "AMEND-HK-1-1 rounding intervals"}

        def judge(k):
            iv, lo, hi = rounding_interval(BAR[k])
            x = vals[k]
            return {"enclosure": d["values"][k], "bar": BAR[k], "rounding_interval": [lo.str(15), hi.str(15)],
                    "overlaps_interval": bool(x.overlaps(iv)), "rel_width": width(x), "width_ok": width(x) <= 1e-8}

        j = judge("beta")
        excl = {}
        for name, v in PRINTED_BETA.items():
            iv, lo, hi = rounding_interval(v)
            excl[name] = {"interval": [lo.str(10), hi.str(10)], "disjoint": not bool(vals["beta"].overlaps(iv)),
                          "gap_to_interval": (lo - vals["beta"]).str(6)}
        j["printed_beta_exclusion"] = excl
        j["outcome"] = "PASS" if (j["overlaps_interval"] and j["width_ok"] and all(e["disjoint"] for e in excl.values())) else "FAIL"
        out["PH1"] = j
        items = {k: judge(k) for k in ("P_1", "alpha", "Sdot_1", "Sdot_2", "page_time")}
        out["PH2"] = {"items": items, "outcome": "PASS" if all(v["overlaps_interval"] and v["width_ok"] for v in items.values()) else "FAIL"}
        j = judge("P_2")
        j["inside_newton"] = bool(vals["P_2"] > arb(NEWTON[0]) and vals["P_2"] < arb(NEWTON[1]))
        j["outcome"] = "PASS" if (j["inside_newton"] and j["overlaps_interval"] and j["width_ok"]) else "FAIL"
        out["PH3"] = j
        for k in ("PH4", "PH5", "PH6"):
            out[k] = {"outcome": d[k]["outcome"], "copied_from_result": True}
        out["original_outcomes"] = {k: d[k]["outcome"] for k in ("PH1", "PH2", "PH3", "PH4", "PH5", "PH6")}
        out["changed"] = [k for k in ("PH1", "PH2", "PH3") if out[k]["outcome"] != d[k]["outcome"]]
        json.dump(out, open(os.path.join(HERE, "rescore_hk1b.json"), "w"), indent=1)
        print(json.dumps({k: out[k]["outcome"] for k in ("PH1", "PH2", "PH3", "PH4", "PH5", "PH6")}), "changed:", out["changed"])
        print(json.dumps(out["PH1"]["printed_beta_exclusion"]))
    finally:
        ctx.prec = old


if __name__ == "__main__":
    main(*sys.argv[1:])
