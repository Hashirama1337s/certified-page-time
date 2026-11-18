"""hk1b_channel - v2 channel driver for BAR-HK-1b (build seat build-1, 2026-11-17).  New file; pinned files untouched.

Same layout as hkchannel.run_channel (v1): IR region (0, E] by hyperbolic band bounds, Taylor-model panels on
[E, W_HI], Planck tail above.  Changes:
 (1) panels use the re-centred quadrature hk1b_quad.panel_integrals;
 (2) ABSOLUTE SKIP (stated in advance): before a panel is solved, its per-mode contribution is bounded with the
     certified band bound Gamma <= G(band) (hkbounds.gamma_band_bound, hkbounds.band_contrib).  If that bound is
     <= SKIP_P (P) and <= SKIP_S (S) the panel contributes [0, bound] and is not solved;
 (3) PANEL FALLBACK: if a panel solve raises, the panel contributes [0, band bound] (Gamma <= min(1, G)), the panel
     is recorded INCONCLUSIVE locally, and the width is charged to the fallback ledger;
 (4) CHANNEL FALLBACK: if the channel driver itself raises, the whole channel contributes [0, channel_tail_bound]
     (band bounds + Planck, valid for every w) and the channel is recorded INCONCLUSIVE locally.
All three keep the totals rigorous; only widths grow.  No v1 ledger row is reused (v1 panels used a different
quadrature code path); the v2 ledger is keyed by the v2 instrument hash.
"""
import time
from flint import arb
import hkcore as H
import hkbounds as HB
import hkchannel as C1           # reuse panel_edges, Ledger, a2s/s2a, W_HI, RHO_FACTOR (unchanged helpers)
import hk1b_quad as Q2

W_HI = C1.W_HI
SKIP_P = arb("1e-22")            # per-mode absolute skip thresholds (stated before any v2 main run)
SKIP_S = arb("1e-20")
a2s, s2a, Ledger, panel_edges = C1.a2s, C1.s2a, C1.Ledger, C1.panel_edges


def do_panel(eq, lo, hi, prec_bits=H.PREC):
    t0 = time.time()
    with H.precision(prec_bits):
        lo = arb(lo); hi = arb(hi)
        w0 = (lo + hi) / 2
        delta = (hi - lo) / 2
        rho_w = C1.RHO_FACTOR * delta
        P = H.make_plan(eq, lo, hi, wmax_disk=w0 + rho_w, wmin_disk=w0 - rho_w)
        B, eta = H.uniform_bounds(eq, P, w0, delta, rho_w)
        co = H.jet_solve(eq, P, w0)
        mu = delta / rho_w
        rA = B * mu ** H.JET_LEN / (1 - mu) + eta
        IP, IS, IN, info = Q2.panel_integrals(co, rA, w0, delta)
        info.update({"B": B.str(5), "eta": eta.str(5), "rA": rA.str(5), "steps": len(P.steps), "R": float(P.R),
                     "M": P.M, "jet_prec": P.jet_prec, "sec": round(time.time() - t0, 3)})
        return IP, IS, IN, info


def band_panel_bound(L, c, lo, hi):
    with H.precision(128):
        G = HB.gamma_band_bound(L, c, lo, hi)
        p, s = HB.band_contrib(G.min(arb(1)), lo, hi)
        return p, s, G


def run_channel(s, l, ledger, tol_P=arb("1e-17"), tol_S=arb("1e-15"), w_floor=arb("1e-6"), log=None,
                max_panels=None, solve=True):
    """per-mode P, S enclosures for channel (s, l).  solve=False is the probe path: every panel is solved and timed but
    nothing is summed or reported (no values leave the probe).  Returns dict (strings) with local status."""
    eq = H.Eq("RW", s, l)
    L = l * (l + 1)
    c = 2 * (1 - s * s)
    t0 = time.time()
    edges = panel_edges(W_HI, w_floor)
    status = "OK"
    notes = []
    fb_P = arb(0); fb_S = arb(0)
    with H.precision():
        IP = arb(0); IS = arb(0)
        npan = nskip = nfb = 0
        stop_edge = None
        IRP = IRS = None
        timings = []
        for k in range(len(edges) - 1):
            hi, lo = edges[k], edges[k + 1]
            irk = "IR|%d|%d|%s" % (s, l, a2s(hi))
            row = ledger.get(irk)
            if row is None:
                p, sb, nb = HB.ir_region(L, c, hi)
                row = {"P": a2s(p), "S": a2s(sb), "bands": nb}
                ledger.put(irk, row)
            p, sb = s2a(row["P"]), s2a(row["S"])
            if p < tol_P and sb < tol_S:
                stop_edge = hi
                IRP, IRS = p, sb
                break
            if max_panels is not None and npan >= max_panels:
                return None
            key = "PAN|%d|%d|%d|%s|%s" % (s, l, k, a2s(lo), a2s(hi))
            row = ledger.get(key)
            if row is None:
                bp, bs, G = band_panel_bound(L, c, lo, hi)
                if bp <= SKIP_P and bs <= SKIP_S:
                    row = {"kind": "skip", "IP": a2s(arb(bp / 2, (bp / 2).upper())),
                           "IS": a2s(arb(bs / 2, (bs / 2).upper())), "G": G.str(5)}
                else:
                    try:
                        ip, is_, in_, info = do_panel(eq, lo, hi)
                        row = {"kind": "TM", "IP": a2s(ip), "IS": a2s(is_), "IN": a2s(in_), "info": info}
                    except Exception as e:          # rigorous fallback, recorded
                        row = {"kind": "fallback", "IP": a2s(arb(bp / 2, (bp / 2).upper())),
                               "IS": a2s(arb(bs / 2, (bs / 2).upper())), "G": G.str(5),
                               "reason": "%s: %s" % (type(e).__name__, e)}
                ledger.put(key, row)
                if log:
                    log("  s=%d l=%d panel %d [%.6g, %.6g] %s %s" % (s, l, k, float(lo), float(hi), row["kind"],
                        ("%.2fs" % row["info"]["sec"]) if row["kind"] == "TM" else row.get("reason", "")[:80]))
            if row["kind"] == "TM":
                timings.append(row["info"]["sec"])
            elif row["kind"] == "skip":
                nskip += 1
            else:
                nfb += 1
                status = "INCONCLUSIVE-LOCAL (panel fallback)"
                notes.append("panel %d: %s" % (k, row["reason"][:200]))
                fb_P += 2 * s2a(row["IP"]).rad(); fb_S += 2 * s2a(row["IS"]).rad()
            IP += s2a(row["IP"]); IS += s2a(row["IS"])
            npan += 1
        if stop_edge is None:
            raise H.Refuse("channel s=%d l=%d: IR bound did not close above %s" % (s, l, w_floor))
        TP = HB.planck_tail_P(W_HI)
        TS = HB.planck_tail_S(W_HI)
        P = IP + arb((IRP + TP) / 2, ((IRP + TP) / 2).upper())
        S = IS + arb((IRS + TS) / 2, ((IRS + TS) / 2).upper())
        out = {"s": s, "l": l, "status": status, "notes": notes, "panels": npan, "skipped": nskip, "fallbacks": nfb,
               "fallback_P_width": a2s(fb_P), "fallback_S_width": a2s(fb_S), "E_ir": a2s(stop_edge),
               "panel_sec_total": round(sum(timings), 1), "panel_sec_max": max(timings) if timings else 0,
               "sec": round(time.time() - t0, 2)}
        if solve:
            out["P_mode"] = a2s(P); out["S_mode"] = a2s(S)
        return out


def run_channel_safe(s, l, ledger, log=None):
    """run_channel with the channel-level rigorous fallback"""
    try:
        return run_channel(s, l, ledger, log=log)
    except Exception as e:
        with H.precision(128):
            p, sb, W = HB.channel_tail_bound(l * (l + 1), 2 * (1 - s * s))
        if log:
            log("CHANNEL FALLBACK s=%d l=%d: %s" % (s, l, e))
        return {"s": s, "l": l, "status": "INCONCLUSIVE-LOCAL (channel fallback)", "notes": ["%s: %s" % (type(e).__name__, e)],
                "P_mode": a2s(arb(p / 2, (p / 2).upper())), "S_mode": a2s(arb(sb / 2, (sb / 2).upper())),
                "fallback_P_width": a2s(p), "fallback_S_width": a2s(sb), "panels": 0, "skipped": 0, "fallbacks": 0}
