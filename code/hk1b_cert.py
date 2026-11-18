"""hk1b_cert - BAR-HK-1b instrument (v2), build seat build-1, 2026-11-17.  New file; pinned v1 files untouched.

    py -3.11 memcap.py 8 py -3.11 hk1b_cert.py --controls   controls -> controls_hk1b.json            (build seat)
    py -3.11 memcap.py 8 py -3.11 hk1b_cert.py --probe      FULL probe: every panel of every channel solved and timed,
                                                            every tail channel l = 10..60 and the lemma; no value is
                                                            summed or kept -> probe_hk1b.json            (build seat)
    py -3.11 memcap.py 8 py -3.11 hk1b_cert.py --main       sealed main -> result_hk1b.json             (LEAD ONLY)

v2 vs v1 (hk1_cert.py, run 2026-11-17, PH1-3/6 INCONCLUSIVE at main_hk1.log l.180):
  - panel quadrature re-centred exactly before the ball remainder (hk1b_quad);
  - absolute skip of panels whose certified band bound is <= SKIP_P/SKIP_S (hk1b_channel, stated in advance);
  - rigorous fallbacks: panel -> band bound, channel -> channel_tail_bound; recorded INCONCLUSIVE-LOCAL;
  - fallback widths are summed (with the 2(2l+1)/(2pi) factor) and compared to FALLBACK_BUDGET stated here;
  - no v1 ledger row is reused.
Predictions, bar values, tolerances and PASS logic are those of hk1_cert.py (imported unchanged), with the rounding-
interval reading of AMEND-HK-1-1 (seal 48cf09638b).
"""
import sys
import os
import json
import time
import hashlib
import traceback
from flint import arb, acb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hkcore as H            # noqa: E402
import hkbounds as HB         # noqa: E402
import hk1_cert as V1         # noqa: E402  (pure helpers: BAR, judge_value, ph4_points, ph5_points, tails, assemble)
import hk1b_channel as C2     # noqa: E402
import hk1b_quad as Q2        # noqa: E402

INSTRUMENT_FILES = ("hkcore.py", "hkquad.py", "hkbounds.py", "hkchannel.py", "hk1_cert.py",
                    "hk1b_quad.py", "hk1b_channel.py", "hk1b_cert.py")
FALLBACK_BUDGET_P = arb("1e-15")      # absolute, summed over all fallback panels/channels, per spin, after g factor
FALLBACK_BUDGET_S = arb("1e-13")
L_T, L_BIG = V1.L_T, V1.L_BIG


def instrument_sha256():
    h = hashlib.sha256()
    for f in INSTRUMENT_FILES:
        h.update(f.encode())
        h.update(open(os.path.join(HERE, f), "rb").read())
    return h.hexdigest()


def file_sha(f):
    return hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest()


def gfac(l):
    return arb(2 * (2 * l + 1)) / (2 * arb.pi())


def do_main():
    t0 = time.time()
    sha = instrument_sha256()
    log = V1.log_to(os.path.join(HERE, "main_hk1b.log"))
    log("MAIN v2 start, instrument sha256 %s" % sha)
    ledger = C2.Ledger(os.path.join(HERE, "ledger_hk1b.jsonl"), sha[:16])
    result = {"bar": "BAR-HK-1b", "instrument_sha256": sha, "files": {f: file_sha(f) for f in INSTRUMENT_FILES},
              "config": {"L_T": L_T, "L_BIG": L_BIG, "SKIP_P": C2.SKIP_P.str(3), "SKIP_S": C2.SKIP_S.str(3),
                         "FALLBACK_BUDGET_P": FALLBACK_BUDGET_P.str(3), "FALLBACK_BUDGET_S": FALLBACK_BUDGET_S.str(3)}}
    vals = chans = tl = None
    try:
        chans = {}
        for (s, l) in V1.channel_list():
            key = "CH|%d|%d" % (s, l)
            row = ledger.get(key)
            if row is None:
                row = C2.run_channel_safe(s, l, ledger, log=log)
                ledger.put(key, row)
                log("channel s=%d l=%d: %s panels %d skipped %d fallbacks %d" % (s, l, row["status"], row["panels"],
                    row["skipped"], row["fallbacks"]))
            chans[(s, l)] = row
        tl = V1.tails(ledger, log)
        vals, extra = V1.assemble(chans, tl)
        with H.precision():
            fb = {}
            for s in (1, 2):
                fp = arb(0); fs = arb(0)
                for (ss, l), row in chans.items():
                    if ss == s:
                        fp += gfac(l) * arb(row["fallback_P_width"]); fs += gfac(l) * arb(row["fallback_S_width"])
                fb[str(s)] = {"P": fp.str(5), "S": fs.str(5),
                              "within_budget": bool(fp <= FALLBACK_BUDGET_P and fs <= FALLBACK_BUDGET_S)}
        result["fallback_widths"] = fb
        result["channel_status"] = {"%d,%d" % k: {kk: v.get(kk) for kk in ("status", "notes", "panels", "skipped",
                                    "fallbacks", "P_mode", "S_mode")} for k, v in chans.items()}
        result["tails"] = {str(s): {"P": V1.a2s(tl[s][0]), "S": V1.a2s(tl[s][1])} for s in tl}
        result["values"] = {k: V1.a2s(v) for k, v in vals.items()}
        result["closed_forms"] = {k: V1.a2s(v) for k, v in extra.items()}
    except Exception as e:
        result["values_error"] = "%s: %s" % (type(e).__name__, e)
        result["values_traceback"] = traceback.format_exc()
        log("VALUES INCONCLUSIVE: %s" % e)

    def rec(name, fn):
        try:
            result[name] = fn()
        except Exception as e:
            result[name] = {"outcome": "INCONCLUSIVE", "reason": "%s: %s" % (type(e).__name__, e)}
        log("%s -> %s" % (name, result[name].get("outcome")))

    def need():
        return {"outcome": "INCONCLUSIVE", "reason": "values not computed"} if vals is None else None

    def ph1():
        if need():
            return need()
        j = V1.judge_value(vals["beta"], V1.BAR["beta"])
        j["excludes_printed"] = {k: (not bool(vals["beta"].overlaps(arb(v)))) for k, v in V1.PRINTED_BETA.items()}
        ok = j["width_ok"] and j["overlaps_bar_rounding_interval"] and all(j["excludes_printed"].values())
        j["outcome"] = "PASS" if ok else "FAIL"
        return j

    def ph2():
        if need():
            return need()
        items = {k: V1.judge_value(vals[k], V1.BAR[k]) for k in ("P_1", "alpha", "Sdot_1", "Sdot_2", "page_time")}
        ok = all(v["width_ok"] and v["overlaps_bar_rounding_interval"] for v in items.values())
        return {"items": items, "outcome": "PASS" if ok else "FAIL"}

    def ph3():
        if need():
            return need()
        j = V1.judge_value(vals["P_2"], V1.BAR["P_2"])
        with H.precision():
            j["inside_newton"] = bool(vals["P_2"] > arb(V1.NEWTON[0]) and vals["P_2"] < arb(V1.NEWTON[1]))
        j["outcome"] = "PASS" if (j["inside_newton"] and j["width_ok"] and j["overlaps_bar_rounding_interval"]) else "FAIL"
        return j

    def ph4():
        ok, rows = V1.ph4_points()
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    def ph5():
        ok, rows = V1.ph5_points()
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    def ph6():
        if need():
            return need()
        with H.precision():
            Pn = arb(0)
            for (s, l), row in chans.items():
                if s == 1 and l >= 2:
                    Pn += gfac(l) * arb(row["P_mode"])
            tp = tl[1][0]
            Pn = Pn + arb(tp / 2, (tp / 2).upper())
            disjoint = bool(Pn < arb(V1.NEWTON[0]) or Pn > arb(V1.NEWTON[1]))
        return {"P2_with_s1_potential": V1.a2s(Pn), "newton": V1.NEWTON, "disjoint": disjoint,
                "outcome": "PASS" if disjoint else "FAIL"}

    for name, fn in (("PH1", ph1), ("PH2", ph2), ("PH3", ph3), ("PH4", ph4), ("PH5", ph5), ("PH6", ph6)):
        rec(name, fn)
    result["sec"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "result_hk1b.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    log("MAIN v2 done in %.1fs -> result_hk1b.json" % result["sec"])


def do_probe(log=print, out=None):
    """FULL probe: every panel of every Taylor-model channel is solved (timing + status only), every per-l tail channel
    and the lemma are evaluated.  The probe ledger is deleted afterwards; no value is summed, printed or kept."""
    t0 = time.time()
    sha = instrument_sha256()
    pl = os.path.join(HERE, "probe_ledger_hk1b.jsonl")
    if os.path.exists(pl):
        os.remove(pl)
    ledger = C2.Ledger(pl, sha[:16])
    rows = []
    for (s, l) in V1.channel_list():
        try:
            r = C2.run_channel(s, l, ledger, solve=False)
            rows.append({k: r[k] for k in ("s", "l", "status", "panels", "skipped", "fallbacks", "panel_sec_total",
                                          "panel_sec_max", "sec", "notes")})
            log("probe s=%d l=%d: %s, %d panels (%d skipped, %d fallback), %.1fs, max panel %.2fs" % (
                s, l, r["status"], r["panels"], r["skipped"], r["fallbacks"], r["sec"], r["panel_sec_max"]))
        except Exception as e:
            rows.append({"s": s, "l": l, "status": "CHANNEL-FAIL (would use channel fallback)", "error": str(e)})
            log("probe s=%d l=%d: CHANNEL-FAIL %s" % (s, l, e))
    tt = time.time()
    tail_rows = []
    with H.precision(128):
        for s in (1, 2):
            for l in range(L_T + 1, L_BIG + 1):
                t1 = time.time()
                try:
                    HB.channel_tail_bound(l * (l + 1), 2 * (1 - s * s))
                    st = "OK"
                except Exception as e:
                    st = "FAIL %s" % e
                tail_rows.append({"s": s, "l": l, "status": st, "sec": round(time.time() - t1, 2)})
        try:
            lem = HB.large_l_lemma(L_BIG)
            HB.large_l_tail_sum(lem)
            lem_st = "OK"
        except Exception as e:
            lem_st = "FAIL %s" % e
    t_tails = time.time() - tt
    ledger = None
    os.remove(pl)
    total = time.time() - t0
    n_fail_tails = sum(1 for r in tail_rows if r["status"] != "OK")
    res = {"instrument_sha256": sha, "channels": rows, "tail_channels_l10_60": {"n": len(tail_rows), "failures": n_fail_tails,
           "sec": round(t_tails, 1)}, "lemma": lem_st, "probe_sec": round(total, 1),
           "projected_main_sec": round(total + 10, 0),
           "note": "projected main = this full probe's wall time (the main repeats exactly this work, plus summation, PH4, PH5)"}
    log("FULL probe: %.0f s; tails %d channels (%d failures) %.0f s; lemma %s; projected main %.0f s" % (
        total, len(tail_rows), n_fail_tails, t_tails, lem_st, res["projected_main_sec"]))
    if out:
        json.dump(res, open(out, "w"), indent=1)
    return res


def do_controls():
    t0 = time.time()
    sha = instrument_sha256()
    log = V1.log_to(os.path.join(HERE, "controls_hk1b.log"))
    log("CONTROLS v2 start, instrument sha256 %s" % sha)
    res = {"instrument_sha256": sha, "files": {f: file_sha(f) for f in INSTRUMENT_FILES}}
    edges = C2.panel_edges(C2.W_HI, arb("1e-6"))

    def rec(name, fn):
        t = time.time()
        try:
            res[name] = fn()
        except Exception as e:
            res[name] = {"outcome": "INCONCLUSIVE", "reason": "%s: %s" % (type(e).__name__, e),
                         "traceback": traceback.format_exc()}
        res[name]["sec"] = round(time.time() - t, 1)
        log("%s -> %s (%.1fs)" % (name, res[name].get("outcome"), res[name]["sec"]))

    def c1():
        ok, rows = V1.ph5_points()
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    def c2():
        ok, rows = V1.ph4_points(ws=("0.37",), ls=(2,))
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    def c4():
        refused = False
        try:
            eq = H.Eq("RW", 1, 1)
            with H.precision():
                P = H.make_plan(eq, arb("0.25"), arb("0.35"), wmax_disk=arb("0.5"), wmin_disk=arb("0.1"))
            H.jet_solve(eq, P, arb(3) / 10, length=H.JET_LEN + 1)
        except H.Refuse:
            refused = True
        return {"refused_overlong_jet": refused, "outcome": "PASS" if refused else "FAIL"}

    # C12: the panels that stopped the v1 main now pass through the Taylor model (no fallback)
    def c12():
        rows = []
        ok = True
        for (s, l) in ((1, 8), (2, 8), (1, 9), (2, 9), (1, 7)):
            try:
                ip, is_, in_, info = C2.do_panel(H.Eq("RW", s, l), edges[1], edges[0])
                rw = V1.rel_width(ip)
                with H.precision():
                    aw = float((2 * ip.rad()).upper()); aws = float((2 * is_.rad()).upper())
                # pass: Taylor-model solve succeeded and the width is negligible, either relatively (< 1e-6) or
                # absolutely (< 1e-20 per mode, far below the fallback budgets 1e-15 / 1e-13)
                good = (rw is not None and rw < 1e-6) or (aw < 1e-20 and aws < 1e-20)
                rows.append({"s": s, "l": l, "panel": 0, "rel_width_P": rw, "abs_width_P": aw, "abs_width_S": aws,
                             "max_depth": info["max_depth"], "tm_ok": good})
            except Exception as e:
                good = False
                rows.append({"s": s, "l": l, "panel": 0, "error": str(e)})
            ok = ok and good
        return {"rows": rows, "outcome": "PASS" if ok else "FAIL"}

    # C13: v2 quadrature agrees with v1 on panels where v1 succeeded (overlap) - same jets, two quadratures
    def c13():
        import hkquad as Q1
        rows = []
        ok = True
        for (s, l, k) in ((1, 1, 0), (1, 1, 10), (1, 1, 40), (2, 2, 5), (1, 4, 8)):
            eq = H.Eq("RW", s, l)
            with H.precision():
                lo, hi = edges[k + 1], edges[k]
                w0 = (lo + hi) / 2; delta = (hi - lo) / 2; rho_w = 5 * delta
                P = H.make_plan(eq, lo, hi, wmax_disk=w0 + rho_w, wmin_disk=w0 - rho_w)
                B, eta = H.uniform_bounds(eq, P, w0, delta, rho_w)
                co = H.jet_solve(eq, P, w0)
                rA = B * (delta / rho_w) ** H.JET_LEN / (1 - delta / rho_w) + eta
                a = Q1.panel_integrals(co, rA, w0, delta)
                b = Q2.panel_integrals(co, rA, w0, delta)
                ov = all(bool(a[i].overlaps(b[i])) for i in range(3))
                rows.append({"s": s, "l": l, "k": k, "v1_P": a[0].str(15), "v2_P": b[0].str(15), "v1_S": a[1].str(15),
                             "v2_S": b[1].str(15), "overlap": ov})
                ok = ok and ov
        return {"rows": rows, "outcome": "PASS" if ok else "FAIL"}

    # C14: fallback teeth - force every panel solve of a small channel to fail; the channel result must stay finite,
    #      contain the honest Taylor-model result, and be flagged INCONCLUSIVE-LOCAL
    def c14():
        s, l = 2, 7
        tmpA = os.path.join(HERE, "ctl_b_A.jsonl"); tmpB = os.path.join(HERE, "ctl_b_B.jsonl")
        for f in (tmpA, tmpB):
            if os.path.exists(f):
                os.remove(f)
        honest = C2.run_channel(s, l, C2.Ledger(tmpA, sha[:16]))
        orig = C2.do_panel

        def broken(*a, **k):
            raise H.Refuse("forced failure (control C14)")
        C2.do_panel = broken
        try:
            forced = C2.run_channel(s, l, C2.Ledger(tmpB, sha[:16]))
        finally:
            C2.do_panel = orig
        for f in (tmpA, tmpB):
            os.remove(f)
        with H.precision():
            contains = bool(arb(forced["P_mode"]).contains(arb(honest["P_mode"])) and
                            arb(forced["S_mode"]).contains(arb(honest["S_mode"])))
        flagged = forced["status"].startswith("INCONCLUSIVE") and forced["fallbacks"] > 0
        return {"honest_status": honest["status"], "forced_status": forced["status"], "forced_fallbacks": forced["fallbacks"],
                "forced_contains_honest": contains, "outcome": "PASS" if (contains and flagged) else "FAIL"}

    # C15: channel-level fallback contains the honest channel (s = 2, l = 9)
    def c15():
        s, l = 2, 9
        tmp = os.path.join(HERE, "ctl_b_C.jsonl")
        if os.path.exists(tmp):
            os.remove(tmp)
        honest = C2.run_channel(s, l, C2.Ledger(tmp, sha[:16]))
        os.remove(tmp)
        orig = C2.run_channel

        def broken(*a, **k):
            raise H.Refuse("forced channel failure (control C15)")
        C2.run_channel = broken
        try:
            fb = C2.run_channel_safe(s, l, None)
        finally:
            C2.run_channel = orig
        with H.precision():
            contains = bool(arb(fb["P_mode"]).contains(arb(honest["P_mode"])) and arb(fb["S_mode"]).contains(arb(honest["S_mode"])))
        return {"fallback_status": fb["status"], "contains_honest": contains, "honest_status": honest["status"],
                "outcome": "PASS" if (contains and fb["status"].startswith("INCONCLUSIVE")) else "FAIL"}

    # C5: checkpoint write + reload + resume with the v2 driver (s = 2, l = 7)
    def c5():
        tmp1 = os.path.join(HERE, "ctl_b_D.jsonl"); tmp2 = os.path.join(HERE, "ctl_b_E.jsonl")
        for f in (tmp1, tmp2):
            if os.path.exists(f):
                os.remove(f)
        part = C2.run_channel(2, 7, C2.Ledger(tmp1, sha[:16]), max_panels=2)
        lb = C2.Ledger(tmp1, sha[:16])
        n_rel = sum(1 for k in lb.rows if k.startswith("PAN"))
        resumed = C2.run_channel(2, 7, lb)
        fresh = C2.run_channel(2, 7, C2.Ledger(tmp2, sha[:16]))
        same = resumed["P_mode"] == fresh["P_mode"] and resumed["S_mode"] == fresh["S_mode"]
        for f in (tmp1, tmp2):
            os.remove(f)
        return {"interrupted_returned_none": part is None, "panels_reloaded": n_rel, "resumed_equals_fresh": same,
                "outcome": "PASS" if (part is None and n_rel == 2 and same) else "FAIL"}

    # C6: recon positive control on a full channel with the v2 driver (s = 1, l = 2; enclosure must contain recon)
    def c6():
        d = json.load(open("<RECON>/seats/computing/out/s1_n20.json"))
        Pr, Sr = d["l"]["2"]["P"], d["l"]["2"]["S"]
        tmp = os.path.join(HERE, "ctl_b_F.jsonl")
        if os.path.exists(tmp):
            os.remove(tmp)
        r = C2.run_channel(1, 2, C2.Ledger(tmp, sha[:16]))
        os.remove(tmp)
        with H.precision():
            P = gfac(2) * arb(r["P_mode"]); S = gfac(2) * arb(r["S_mode"])
            okP = bool(P.contains(arb(Pr))); okS = bool(S.contains(arb(Sr)))
        return {"P_l2": V1.a2s(P), "recon_P": Pr, "S_l2": V1.a2s(S), "recon_S": Sr, "contains_P": okP, "contains_S": okS,
                "status": r["status"], "outcome": "PASS" if (okP and okS) else "FAIL"}

    # C9: large-l lemma
    def c9():
        lem = HB.large_l_lemma(L_BIG)
        p, sb = HB.large_l_tail_sum(lem)
        return {"Gs": lem["Gs"].str(8), "P_tail": p.str(5), "S_tail": sb.str(5), "outcome": "PASS"}

    for name, fn in (("C1_PH5", c1), ("C2_PH4_one_freq", c2), ("C4_cap_refusal", c4), ("C9_large_l_lemma", c9),
                     ("C12_v1_failing_panels", c12), ("C13_v1_v2_quadrature_agree", c13), ("C14_panel_fallback_teeth", c14),
                     ("C15_channel_fallback", c15), ("C5_checkpoint_resume", c5), ("C6_recon_channel_s1_l2", c6)):
        rec(name, fn)
    rec("P_full_probe", lambda: dict(do_probe(log=log, out=os.path.join(HERE, "probe_hk1b.json")), outcome="DONE"))
    res["sec"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "controls_hk1b.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    log("CONTROLS v2 done in %.1fs -> controls_hk1b.json" % res["sec"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--main"]:
        do_main()
    elif a == ["--controls"]:
        do_controls()
    elif a == ["--probe"]:
        do_probe(out=os.path.join(HERE, "probe_hk1b.json"))
    else:
        print(__doc__)
        sys.exit(2)
