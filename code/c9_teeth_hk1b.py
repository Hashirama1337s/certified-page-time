"""c9_teeth_hk1b - control C9 with teeth (referee-1 fix F4), build seat build-1, 2026-11-17.  New file.

v1/v2 control C9 printed PASS whenever large_l_lemma returned (it could only fail by exception).  This control can
fail on its own logic:
  A  honest lemma (L_big = 60) certifies: Gs > 0, K finite, tail sums finite.
  B  soundness: certified point Gamma_l(w) (hkcore.point_solve, Regge-Wheeler) <= eps_l = K exp(-Gs (l-1)) at sample
     (s, l > 60, w <= wt_max sqrt(L')) points.  A FAIL here would mean the lemma is wrong.
  C  teeth 1: an impossible configuration (wt_max = 0.19, the core U >= wt^2 almost empty near U_max = 1/27) must be
     REFUSED by the lemma code.
  D  teeth 2: a falsified certificate (Gs x 4, K = 4) must be CAUGHT by check B at some sample point - this shows that
     check B can fail.
Outcome PASS only if A, B hold, C refuses and D catches.  Writes c9_teeth_hk1b.json.
"""
import sys, os, json, time
from flint import arb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hkcore as H
import hkbounds as HB

POINTS = [(1, 61, 0.5), (1, 61, 3.0), (1, 61, 6.0), (2, 61, 6.0), (2, 61, 2.0), (1, 80, 7.9), (2, 75, 7.4)]


def main():
    t0 = time.time()
    out = {}
    lem = HB.large_l_lemma(60)
    p, s = HB.large_l_tail_sum(lem)
    with H.precision():
        Gs, K = lem["Gs"], lem["K"]
        A_ok = bool(Gs > 0 and K.is_finite() and p.is_finite() and s.is_finite())
    out["A_honest"] = {"Gs": Gs.str(8), "K": K.str(5), "P_tail": p.str(5), "S_tail": s.str(5), "ok": A_ok}

    rows = []
    B_ok = True
    D_caught = False
    for (sp, l, wv) in POINTS:
        with H.precision():
            Lp = arb(l * (l + 1) - 3)
            w = arb(int(round(wv * 1024))) / 1024
            if not w <= arb("0.1") * Lp.sqrt():
                raise SystemExit("sample point outside the lemma range")
        eqn = H.Eq("RW", sp, l)
        with H.precision():
            Pl = H.make_plan(eqn, w, w)
        Pl.Nh = 400          # large L: the horizon majorant needs n >> sqrt(L) terms (any Nh is a valid choice)
        g = H.point_solve(eqn, w, P=Pl, want_out=False)["Gamma"]
        with H.precision():
            eps = K * (-Gs * (l - 1)).exp()
            eps_wrong = 4 * (-(4 * Gs) * (l - 1)).exp()
            sound = bool(g <= eps)
            caught = bool(g > eps_wrong)
        rows.append({"s": sp, "l": l, "w": w.str(8), "Gamma_point": g.str(6), "eps_lemma": eps.str(4),
                     "sound": sound, "eps_falsified": eps_wrong.str(4), "falsified_violated": caught})
        B_ok = B_ok and sound
        D_caught = D_caught or caught
    out["B_soundness"] = {"rows": rows, "ok": B_ok}

    refused = False
    try:
        HB.large_l_lemma(60, wt_max=arb("0.19"))
    except H.Refuse as e:
        refused = True
        out["C_reason"] = str(e)
    out["C_teeth_refusal"] = refused
    out["D_teeth_falsified_caught"] = D_caught
    out["outcome"] = "PASS" if (A_ok and B_ok and refused and D_caught) else "FAIL"
    out["sec"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "c9_teeth_hk1b.json"), "w"), indent=1)
    print(json.dumps({k: (v if k != "B_soundness" else {"ok": v["ok"]}) for k, v in out.items()}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
