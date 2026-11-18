"""hk1_cert - BAR-HK-1 instrument (build seat build-1, 2026-11-17).  Sealed bar: <LAB>/BAR-HK-1.md.

    py -3.11 memcap.py 8 py -3.11 hk1_cert.py --controls     controls + probes, writes controls_hk1.json   (build seat)
    py -3.11 memcap.py 8 py -3.11 hk1_cert.py --probe        timing probe per (s,l) + projected main time   (build seat)
    py -3.11 memcap.py 8 py -3.11 hk1_cert.py --main         the sealed main path, writes result_hk1.json    (LEAD ONLY)

In plain words: the total power and entropy that a Schwarzschild black hole (M = 1) sends out in photons (s = 1) and
gravitons (s = 2) are sums over multipoles l of frequency integrals of the greybody factor Gamma_{s,l}(w).  Every piece
is enclosed: Taylor-model panels (hkcore + hkquad) where the integrand matters, proved upper bounds (hkbounds) where it is
tiny (low frequency, high frequency, high l), and interval arithmetic for alpha, beta and the Page time.

Per (s,l) the per-mode integrals are multiplied by 2(2l+1)/(2 pi) (both helicities; Page 2013, BAR formula_ref).
alpha = P_1 + P_2,  beta = (Sdot_1 + Sdot_2)/(8 pi alpha),  t_*/t_decay = 1 - (beta/(beta+1))^{3/2}.
"""
import sys
import os
import json
import time
import hashlib
import traceback
from flint import arb, acb, ctx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hkcore as H          # noqa: E402
import hkquad as Q          # noqa: E402
import hkbounds as HB       # noqa: E402
import hkchannel as C       # noqa: E402

L_T = 9                     # Taylor-model channels: s = 1: l = 1..L_T, s = 2: l = 2..L_T
L_BIG = 60                  # per-l band bounds for L_T < l <= L_BIG; large-l lemma beyond
WIDTH_CAP = arb("1e-8")     # bar: relative width <= 1e-8
INSTRUMENT_FILES = ("hkcore.py", "hkquad.py", "hkbounds.py", "hkchannel.py", "hk1_cert.py")

# bar values (BAR-HK-1.md l.20-33), as printed (11 significant digits)
BAR = {
    "beta": "1.4846916919", "P_1": "3.3638547856e-5", "alpha": "3.7475287781e-5", "Sdot_1": "1.2683659541e-3",
    "Sdot_2": "1.3000087862e-4", "page_time": "0.5381024532", "P_2": "3.8367399250e-6",
}
PRINTED_BETA = {"Page 2013": "1.48472", "Perez-Gonzalez 2025": "1.48471"}
NEWTON = ("3.8262e-6", "3.8639e-6")
PH4_L = (2, 3)
PH4_W = ("0.05", "0.2", "0.37", "0.6", "1.0")


def instrument_sha256():
    h = hashlib.sha256()
    for f in INSTRUMENT_FILES:
        h.update(f.encode())
        h.update(open(os.path.join(HERE, f), "rb").read())
    return h.hexdigest()


def file_sha256(f):
    return hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest()


def a2s(x):
    return x.str(30, radius=True)


def rel_width(x):
    with H.precision():
        m = abs(x).lower()
        if not m > 0:
            return None
        return float((2 * x.rad() / m).upper())


def rounding_interval(s):
    """the interval of numbers that round to the printed decimal s (half a unit in its last printed digit)"""
    mant, _, ex = s.lower().partition("e")
    ex = int(ex) if ex else 0
    dec = len(mant.split(".")[1]) if "." in mant else 0
    half = arb(5) * arb(10) ** (-(dec + 1) + ex)
    return arb(s), half


def contains_value(x, s):
    v, half = rounding_interval(s)
    strict = bool(x.contains(arb(s)))
    lo = arb(s) - half
    hi = arb(s) + half
    overl = bool(x.overlaps(arb((lo + hi) / 2, half.upper())))
    return strict, overl


def log_to(path):
    def f(msg):
        line = time.strftime("%H:%M:%S ") + msg
        print(line, flush=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    return f


# ---------------------------------------------------------------- pieces
def channel_list():
    out = []
    for s in (1, 2):
        for l in range(max(s, 1), L_T + 1):
            out.append((s, l))
    return out


def run_all_channels(ledger, log):
    res = {}
    for (s, l) in channel_list():
        key = "CH|%d|%d" % (s, l)
        row = ledger.get(key)
        if row is None:
            r = C.run_channel(s, l, ledger, log=log)
            ledger.put(key, r)
            row = r
            log("channel s=%d l=%d: P_mode %s S_mode %s panels %d (%.1fs)" % (s, l, r["P_mode"][:40], r["S_mode"][:40],
                                                                               r["panels"], r["sec"]))
        res[(s, l)] = row
    return res


def tails(ledger, log, s_list=(1, 2), l_from=None):
    """per-mode tail upper bounds for L_T < l <= L_BIG and the lemma for l > L_BIG; returns per spin (P, S) totals
    already multiplied by 2(2l+1)/(2 pi)"""
    out = {}
    l_from = (L_T + 1) if l_from is None else l_from
    with H.precision(128):
        for s in s_list:
            c = 2 * (1 - s * s)
            P = arb(0); S = arb(0)
            for l in range(l_from, L_BIG + 1):
                key = "TAIL|%d|%d" % (s, l)
                row = ledger.get(key)
                if row is None:
                    p, sb, W = HB.channel_tail_bound(l * (l + 1), c)
                    row = {"P": a2s(p), "S": a2s(sb), "W_top": a2s(W)}
                    ledger.put(key, row)
                g = arb(2 * (2 * l + 1)) / (2 * arb.pi())
                P += g * arb(row["P"]); S += g * arb(row["S"])
            key = "LEMMA|%d" % L_BIG
            row = ledger.get(key)
            if row is None:
                lem = HB.large_l_lemma(L_BIG)
                p, sb = HB.large_l_tail_sum(lem)
                row = {"P": a2s(p), "S": a2s(sb), "Gs": lem["Gs"].str(10), "K": lem["K"].str(10),
                       "G0_asym": lem["G0_asym"], "nbands": len(lem["bands"])}
                ledger.put(key, row)
            P += arb(row["P"]); S += arb(row["S"])
            out[s] = (arb(P.upper()), arb(S.upper()))
            log("tail s=%d (l > %d): P <= %s, S <= %s" % (s, l_from - 1, out[s][0].str(5), out[s][1].str(5)))
    return out


def assemble(chans, tl):
    with H.precision():
        tot = {}
        for s in (1, 2):
            P = arb(0); S = arb(0)
            for (ss, l), row in chans.items():
                if ss != s:
                    continue
                g = arb(2 * (2 * l + 1)) / (2 * arb.pi())
                P += g * arb(row["P_mode"]); S += g * arb(row["S_mode"])
            tp, ts = tl[s]
            P = P + arb(tp / 2, (tp / 2).upper())
            S = S + arb(ts / 2, (ts / 2).upper())
            tot[s] = (P, S)
        P1, S1 = tot[1]
        P2, S2 = tot[2]
        alpha = P1 + P2
        beta = (S1 + S2) / (8 * arb.pi() * alpha)
        x = beta / (beta + 1)
        page = 1 - x ** arb("1.5")
        extra = {
            "M_star_over_M0": x.sqrt(), "S_star_over_SBH0": x, "t_decay_over_M0^3": 1 / (3 * alpha),
            "t_star_over_M0^3": page / (3 * alpha), "peak_maxmixed_2b_over_1pb": 2 * beta / (1 + beta),
            "t23_over_t_decay": 1 - ((beta - 1) / (beta + 1)) ** arb("1.5"),
            "ratio_photon_Sdot_over_dSBH": S1 / (8 * arb.pi() * P1), "ratio_graviton_Sdot_over_dSBH": S2 / (8 * arb.pi() * P2),
        }
        return {"P_1": P1, "P_2": P2, "Sdot_1": S1, "Sdot_2": S2, "alpha": alpha, "beta": beta, "page_time": page}, extra


def judge_value(x, barval):
    rw = rel_width(x)
    strict, overl = contains_value(x, barval)
    return {"enclosure": a2s(x), "rel_width": rw, "width_ok": (rw is not None and rw <= 1e-8),
            "contains_bar_value_strict": strict, "overlaps_bar_rounding_interval": overl, "bar_value": barval}


def ph4_points(ws=PH4_W, ls=PH4_L):
    rows = []
    ok = True
    for l in ls:
        for wv in ws:
            with H.precision():
                w = arb(wv) if "." not in wv else arb(int(round(float(wv) * 1000))) / 1000
            rw = H.point_solve(H.Eq("RW", 2, l), w)
            zz = H.point_solve(H.Eq("Z", 2, l), w)
            with H.precision():
                ov = bool(rw["Gamma"].overlaps(zz["Gamma"]))
                fl_rw = bool(rw["flux_minus_1"].contains(0))
                fl_z = bool(zz["flux_minus_1"].contains(0))
                rows.append({"l": l, "w": wv, "Gamma_RW": a2s(rw["Gamma"]), "Gamma_Z": a2s(zz["Gamma"]),
                             "overlap": ov, "flux_RW_contains_0": fl_rw, "flux_Z_contains_0": fl_z,
                             "flux_RW_width": rw["flux_minus_1"].str(3), "flux_Z_width": zz["flux_minus_1"].str(3)})
            ok = ok and ov and fl_rw and fl_z
    return ok, rows


def ph5_points():
    rows = []
    ok = True
    for (wv, tol) in ((arb(1) / 1000, arb("1e-2")), (arb(1) / 10 ** 6, arb("1e-5"))):
        with H.precision():
            w = arb(wv)
        out = H.point_solve(H.Eq("RW", 0, 0), w)
        with H.precision():
            d = out["Gamma"] / (16 * w * w) - 1
            inside = bool(abs(d) < tol)
            rows.append({"w": w.str(5), "Gamma_over_16w2_minus_1": a2s(d), "tol": tol.str(3), "certified_within": inside,
                         "flux_contains_0": bool(out["flux_minus_1"].contains(0))})
            ok = ok and inside
    return ok, rows


# ---------------------------------------------------------------- modes
def do_main():
    t0 = time.time()
    sha = instrument_sha256()
    log = log_to(os.path.join(HERE, "main_hk1.log"))
    log("MAIN start, instrument sha256 %s" % sha)
    ledger = C.Ledger(os.path.join(HERE, "ledger_hk1.jsonl"), sha[:16])
    result = {"bar": "BAR-HK-1", "instrument_sha256": sha,
              "files": {f: file_sha256(f) for f in INSTRUMENT_FILES}, "config": {"L_T": L_T, "L_BIG": L_BIG,
              "W_HI": C.W_HI.str(10), "JET_LEN": H.JET_LEN, "PREC": H.PREC}}
    vals = None
    try:
        chans = run_all_channels(ledger, log)
        tl = tails(ledger, log)
        vals, extra = assemble(chans, tl)
        result["channels"] = {"%d,%d" % k: {kk: v[kk] for kk in ("P_mode", "S_mode", "panels", "E_ir")} for k, v in chans.items()}
        result["tails"] = {str(s): {"P": a2s(tl[s][0]), "S": a2s(tl[s][1])} for s in tl}
        result["values"] = {k: a2s(v) for k, v in vals.items()}
        result["closed_forms"] = {k: a2s(v) for k, v in extra.items()}
    except Exception as e:      # recorded, never hidden
        result["values_error"] = "%s: %s" % (type(e).__name__, e)
        result["values_traceback"] = traceback.format_exc()
        log("VALUES INCONCLUSIVE: %s" % e)

    def rec(name, fn):
        try:
            result[name] = fn()
        except Exception as e:
            result[name] = {"outcome": "INCONCLUSIVE", "reason": "%s: %s" % (type(e).__name__, e)}
        log("%s -> %s" % (name, result[name].get("outcome")))

    def ph1():
        if vals is None:
            return {"outcome": "INCONCLUSIVE", "reason": "values not computed"}
        j = judge_value(vals["beta"], BAR["beta"])
        excl = {k: (not bool(vals["beta"].overlaps(arb(v)))) for k, v in PRINTED_BETA.items()}
        j["excludes_printed"] = excl
        ok = j["width_ok"] and j["overlaps_bar_rounding_interval"] and all(excl.values())
        j["outcome"] = "PASS" if ok else "FAIL"
        return j

    def ph2():
        if vals is None:
            return {"outcome": "INCONCLUSIVE", "reason": "values not computed"}
        items = {k: judge_value(vals[k], BAR[k]) for k in ("P_1", "alpha", "Sdot_1", "Sdot_2", "page_time")}
        ok = all(v["width_ok"] and v["overlaps_bar_rounding_interval"] for v in items.values())
        return {"items": items, "outcome": "PASS" if ok else "FAIL"}

    def ph3():
        if vals is None:
            return {"outcome": "INCONCLUSIVE", "reason": "values not computed"}
        P2 = vals["P_2"]
        j = judge_value(P2, BAR["P_2"])
        with H.precision():
            inside = bool(P2 > arb(NEWTON[0]) and P2 < arb(NEWTON[1]))
        j["inside_newton"] = inside
        j["outcome"] = "PASS" if (inside and j["width_ok"] and j["overlaps_bar_rounding_interval"]) else "FAIL"
        return j

    def ph4():
        ok, rows = ph4_points()
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    def ph5():
        ok, rows = ph5_points()
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    def ph6():
        if vals is None:
            return {"outcome": "INCONCLUSIVE", "reason": "values not computed"}
        # graviton power computed with the s = 1 potential: sum over l >= 2 of the s = 1 channels + s = 1 tail
        with H.precision():
            Pn = arb(0)
            for (s, l), row in chans.items():
                if s == 1 and l >= 2:
                    Pn += arb(2 * (2 * l + 1)) / (2 * arb.pi()) * arb(row["P_mode"])
            tp = tl[1][0]
            Pn = Pn + arb(tp / 2, (tp / 2).upper())
            lo, hi = arb(NEWTON[0]), arb(NEWTON[1])
            disjoint = bool(Pn < lo or Pn > hi)
        return {"P2_with_s1_potential": a2s(Pn), "newton": NEWTON, "disjoint": disjoint,
                "outcome": "PASS" if disjoint else "FAIL"}

    for name, fn in (("PH1", ph1), ("PH2", ph2), ("PH3", ph3), ("PH4", ph4), ("PH5", ph5), ("PH6", ph6)):
        rec(name, fn)
    result["sec"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "result_hk1.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    log("MAIN done in %.1fs -> result_hk1.json" % result["sec"])


def do_probe(out=None, log=print):
    """timing per channel: count panels (IR closing edge, cheap) and time one representative panel"""
    t0 = time.time()
    rows = []
    total = 0.0
    for (s, l) in channel_list():
        L = l * (l + 1); c = 2 * (1 - s * s)
        edges = C.panel_edges(C.W_HI, arb("1e-6"))
        n = None
        tir = time.time()
        for k in range(len(edges) - 1):
            p, sb, _ = HB.ir_region(L, c, edges[k])
            if p < arb("1e-17") and sb < arb("1e-15"):
                n = k
                break
        tir = time.time() - tir
        if n is None:
            rows.append({"s": s, "l": l, "panels": None, "note": "IR did not close"})
            continue
        kk = max(0, n // 2)
        tp = time.time()
        C.do_panel(H.Eq("RW", s, l), edges[kk + 1], edges[kk])
        tp = time.time() - tp
        tlow = time.time()
        if n >= 1:
            C.do_panel(H.Eq("RW", s, l), edges[n], edges[n - 1])
        tlow = time.time() - tlow
        est = n * max(tp, tlow) + tir
        total += est
        rows.append({"s": s, "l": l, "panels": n, "sec_panel_mid": round(tp, 2), "sec_panel_low": round(tlow, 2),
                     "sec_ir_search": round(tir, 2), "projected_sec": round(est, 1)})
        log("probe s=%d l=%d: %d panels, %.2fs/%.2fs per panel -> %.0fs" % (s, l, n, tp, tlow, est))
    # tails timing (one l) and lemma
    tt = time.time()
    HB.channel_tail_bound(11 * 12, 0)
    t_tail = time.time() - tt
    tail_total = t_tail * 2 * (L_BIG - L_T)
    proj = total + tail_total + 30
    res = {"rows": rows, "tail_sec_per_l": round(t_tail, 2), "projected_main_sec": round(proj, 0),
           "probe_sec": round(time.time() - t0, 1)}
    log("projected main: %.0f s (%.1f min); probe took %.0f s" % (proj, proj / 60, res["probe_sec"]))
    if out:
        json.dump(res, open(out, "w"), indent=1)
    return res


def do_controls():
    t0 = time.time()
    sha = instrument_sha256()
    log = log_to(os.path.join(HERE, "controls_hk1.log"))
    log("CONTROLS start, instrument sha256 %s" % sha)
    res = {"instrument_sha256": sha, "files": {f: file_sha256(f) for f in INSTRUMENT_FILES}}

    def rec(name, fn):
        t = time.time()
        try:
            res[name] = fn()
        except Exception as e:
            res[name] = {"outcome": "INCONCLUSIVE", "reason": "%s: %s" % (type(e).__name__, e),
                         "traceback": traceback.format_exc()}
        res[name]["sec"] = round(time.time() - t, 1)
        log("%s -> %s (%.1fs)" % (name, res[name].get("outcome"), res[name]["sec"]))

    # C1: PH5 closed-form low-frequency limit (s = 0, l = 0)
    def c1():
        ok, rows = ph5_points()
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    # C2: PH4 at one frequency + flux identity (Zerilli vs Regge-Wheeler, l = 2, Mw = 0.37)
    def c2():
        ok, rows = ph4_points(ws=("0.37",), ls=(2,))
        return {"points": rows, "outcome": "PASS" if ok else "FAIL"}

    # C3: flux identity with teeth: the honest solve passes at several (s,l,w); a horizon start mis-normalised by
    #     1e-6 (relative) must make the certified flux enclosure exclude 0
    def c3():
        rows = []
        good = True
        for (s, l, num, den) in ((1, 1, 3, 10), (1, 2, 1, 20), (2, 2, 37, 100), (2, 4, 9, 10), (1, 3, 3, 2)):
            with H.precision():
                w = arb(num) / den
            o = H.point_solve(H.Eq("RW", s, l), w)
            with H.precision():
                ok = bool(o["flux_minus_1"].contains(0))
            rows.append({"s": s, "l": l, "w": "%d/%d" % (num, den), "flux_minus_1": a2s(o["flux_minus_1"]), "contains_0": ok})
            good = good and ok
        with H.precision():
            w = arb(3) / 10
            sc = 1 + arb(10) ** -6
        bad = H.point_solve(H.Eq("RW", 1, 2), w, start_scale=sc)
        with H.precision():
            teeth = not bool(bad["flux_minus_1"].contains(0))
        return {"rows": rows, "teeth_flux_misnormalised": a2s(bad["flux_minus_1"]), "teeth_excludes_0": teeth,
                "outcome": "PASS" if (good and teeth) else "FAIL"}

    # C4: cap-truncation refusal (jets longer than ctx.cap must be refused, never truncated)
    def c4():
        refused = False
        try:
            eq = H.Eq("RW", 1, 1)
            with H.precision():
                P = H.make_plan(eq, arb("0.25"), arb("0.35"), wmax_disk=arb("0.5"), wmin_disk=arb("0.1"))
            H.jet_solve(eq, P, arb(3) / 10, length=H.JET_LEN + 1)
        except H.Refuse:
            refused = True
        ok_normal = True
        return {"refused_overlong_jet": refused, "outcome": "PASS" if (refused and ok_normal) else "FAIL"}

    # C5: checkpoint write + reload + compare (panel row) and resume of an interrupted channel
    def c5():
        tmp1 = os.path.join(HERE, "ctl_ledger_a.jsonl")
        tmp2 = os.path.join(HERE, "ctl_ledger_b.jsonl")
        for f in (tmp1, tmp2):
            if os.path.exists(f):
                os.remove(f)
        s, l = 2, 7
        la = C.Ledger(tmp1, sha[:16])
        part = C.run_channel(s, l, la, max_panels=2)      # interrupted after 2 panels
        lb_reload = C.Ledger(tmp1, sha[:16])                # reload from disk
        n_reloaded = sum(1 for k in lb_reload.rows if k.startswith("PAN"))
        full_resumed = C.run_channel(s, l, lb_reload)       # resumes, reusing the 2 stored panels
        fresh = C.run_channel(s, l, C.Ledger(tmp2, sha[:16]))
        same = (full_resumed["P_mode"] == fresh["P_mode"] and full_resumed["S_mode"] == fresh["S_mode"])
        with H.precision():
            # serialisation round trip: the reloaded ball must contain the original midpoint
            row = next(r for k, r in lb_reload.rows.items() if k.startswith("PAN"))
            x = arb(row["IP"])
            rt = arb(x.str(40, radius=True))
            roundtrip = bool(rt.contains(x.mid()))
        for f in (tmp1, tmp2):
            os.remove(f)
        return {"interrupted_returned_none": part is None, "panels_reloaded": n_reloaded, "resumed_equals_fresh": same,
                "roundtrip_contains": roundtrip, "P_mode": fresh["P_mode"],
                "outcome": "PASS" if (part is None and n_reloaded == 2 and same and roundtrip) else "FAIL"}

    # C6: positive control against the recon float for one channel (s = 1, l = 2; recon s1_n20.json, 40 digits)
    def c6():
        recon = "<RECON>/seats/computing/out/s1_n20.json"
        d = json.load(open(recon))
        Pr, Sr = d["l"]["2"]["P"], d["l"]["2"]["S"]
        tmp = os.path.join(HERE, "ctl_ledger_c.jsonl")
        if os.path.exists(tmp):
            os.remove(tmp)
        r = C.run_channel(1, 2, C.Ledger(tmp, sha[:16]))
        os.remove(tmp)
        with H.precision():
            g = arb(2 * 5) / (2 * arb.pi())
            P = g * arb(r["P_mode"]); S = g * arb(r["S_mode"])
            # recon floats are estimates (not certified, internally consistent to ~1e-24); our certified enclosure
            # (width ~1e-14 relative) must CONTAIN them.  (First version demanded |diff| < 1e-18 |P| as a ball
            # inequality, impossible below the certified width - a control-design slip, fixed 2026-11-17.)
            okP = bool(P.contains(arb(Pr)))
            okS = bool(S.contains(arb(Sr)))
        return {"P_l2": a2s(P), "recon_P": Pr, "S_l2": a2s(S), "recon_S": Sr, "agree_P": okP, "agree_S": okS,
                "panels": r["panels"], "outcome": "PASS" if (okP and okS) else "FAIL"}

    # C7: PH6 null as a probe - an upper bound for the photon-potential "graviton power" using crude tails only
    def c7():
        with H.precision(128):
            tl = tails(C.Ledger(os.path.join(HERE, "ctl_ledger_tail.jsonl"), sha[:16]), log, s_list=(1,), l_from=2)
            up = tl[1][0]
            lo, hi = arb(NEWTON[0]), arb(NEWTON[1])
            disjoint_by_crude = bool(up < lo)
        os.remove(os.path.join(HERE, "ctl_ledger_tail.jsonl"))
        return {"crude_upper_bound_sum_l>=2_s1": up.str(6), "newton_low": NEWTON[0], "disjoint_by_crude_bound": disjoint_by_crude,
                "note": "PH6 proper uses the Taylor-model s=1 channels (main); this probe only checks the crude bound",
                "outcome": "PASS" if disjoint_by_crude else "PROBE-ONLY"}

    # C8: wrong-potential teeth at the integrand level: s=1 vs s=2 greybody at one point must be disjoint
    def c8():
        with H.precision():
            w = arb(37) / 100
        g1 = H.point_solve(H.Eq("RW", 1, 2), w, want_out=False)["Gamma"]
        g2 = H.point_solve(H.Eq("RW", 2, 2), w, want_out=False)["Gamma"]
        with H.precision():
            dis = not bool(g1.overlaps(g2))
        return {"Gamma_s1_l2": a2s(g1), "Gamma_s2_l2": a2s(g2), "disjoint": dis, "outcome": "PASS" if dis else "FAIL"}

    # C9: large-l lemma certificate
    def c9():
        lem = HB.large_l_lemma(L_BIG)
        p, sb = HB.large_l_tail_sum(lem)
        return {"L_big": L_BIG, "Gs": lem["Gs"].str(8), "K": lem["K"].str(5), "P_tail": p.str(5), "S_tail": sb.str(5),
                "bands": len(lem["bands"]), "outcome": "PASS"}

    # C10: soundness spot-checks of the hyperbolic band bound against certified point solves in every region
    def c10():
        rows = []
        ok = True
        for (s, l, lo, hi) in ((1, 1, "1e-4", "2e-4"), (1, 1, "0.01", "0.02"), (2, 2, "0.05", "0.0525"),
                               (1, 3, "0.3", "0.315"), (2, 6, "0.6", "0.63"), (1, 11, "1.0", "1.05"),
                               (2, 11, "0.5", "0.525"), (1, 20, "2.0", "2.1")):
            with H.precision():
                G = HB.gamma_band_bound(l * (l + 1), 2 * (1 - s * s), arb(lo), arb(hi))
                for wv in (lo, hi):
                    w = arb(wv)
                    g = H.point_solve(H.Eq("RW", s, l), w, want_out=False)["Gamma"]
                    good = bool(g <= G) or bool(G >= 1)
                    rows.append({"s": s, "l": l, "w": wv, "bound": G.str(5), "point": g.str(8), "bound_ge_point": good})
                    ok = ok and good
        return {"rows": rows, "outcome": "PASS" if ok else "FAIL"}

    # C11: Taylor-model panel vs independent certified point solves at interior frequencies
    def c11():
        rows = []
        ok = True
        edges = C.panel_edges(C.W_HI, arb("1e-6"))
        for (s, l, k) in ((1, 1, 8), (2, 2, 3), (1, 4, 8)):
            eq = H.Eq("RW", s, l)
            with H.precision():
                lo, hi = edges[k + 1], edges[k]
                w0 = (lo + hi) / 2; delta = (hi - lo) / 2; rho_w = C.RHO_FACTOR * delta
                P = H.make_plan(eq, lo, hi, wmax_disk=w0 + rho_w, wmin_disk=w0 - rho_w)
                B, eta = H.uniform_bounds(eq, P, w0, delta, rho_w)
                co = H.jet_solve(eq, P, w0)
                mu = delta / rho_w
                rA = B * mu ** H.JET_LEN / (1 - mu) + eta
                for frac in (arb(-1), arb(-1) / 3, arb(5) / 7, arb(1)):
                    e = frac * delta
                    A = sum((co[j] * e ** j for j in range(H.JET_LEN)), acb(0)) + H.cball(rA)
                    G_tm = 1 / abs(A) ** 2
                    g = H.point_solve(eq, w0 + e, want_out=False)["Gamma"]
                    ov = bool(G_tm.overlaps(g))
                    rows.append({"s": s, "l": l, "w": (w0 + e).str(10), "Gamma_TM": G_tm.str(15), "Gamma_point": g.str(15),
                                 "overlap": ov})
                    ok = ok and ov
        return {"rows": rows, "outcome": "PASS" if ok else "FAIL"}

    for name, fn in (("C1_PH5", c1), ("C2_PH4_one_freq", c2), ("C3_flux_teeth", c3), ("C4_cap_refusal", c4),
                     ("C9_large_l_lemma", c9), ("C8_wrong_potential_point", c8), ("C10_band_bound_soundness", c10),
                     ("C11_TM_vs_point", c11), ("C7_PH6_crude_probe", c7),
                     ("C5_checkpoint_resume", c5), ("C6_recon_channel_s1_l2", c6)):
        rec(name, fn)
    rec("P1_timing_probe", lambda: dict(do_probe(log=log), outcome="DONE"))
    res["sec"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "controls_hk1.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    log("CONTROLS done in %.1fs -> controls_hk1.json" % res["sec"])


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--main"]:
        do_main()
    elif args == ["--controls"]:
        do_controls()
    elif args == ["--probe"]:
        do_probe(out=os.path.join(HERE, "probe_hk1.json"))
    else:
        print(__doc__)
        sys.exit(2)
