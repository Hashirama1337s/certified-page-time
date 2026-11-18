"""hkchannel - one (s, l) channel of the Page integrals, with a resumable ledger (build seat build-1, 2026-11-17).

Per mode (before the factor 2(2l+1)/(2 pi)):  P = int_0^inf w n Gamma dw,  S = int_0^inf S(n Gamma) dw.
Layout:  (0, E]          IR region, hyperbolic band bounds (hkbounds.ir_region): contributes [0, IR]
         [E, W_HI]       geometric Taylor-model panels, w0 +/- delta, delta = w0/10, rho_w = w0/2 (hkcore + hkquad)
         [W_HI, inf)     Gamma <= 1 Planck tail: contributes [0, tail]
Ledger: one JSON line per finished panel, keyed by (s, l, k, endpoints); values are arb strings with radii
(never pickled flint objects); on resume a panel whose key and config hash match is reloaded, not recomputed.
"""
import json
import os
import time
import hashlib
from flint import arb, acb
import hkcore as H
import hkquad as Q
import hkbounds as HB

W_HI = arb(205) / 128          # 1.6015625, exact dyadic (panel centres must be exact)
PANEL_SHRINK = (9, 11)          # e_{k+1} = e_k * 9/11 (rounded to the dyadic grid) -> delta = w0/10
RHO_FACTOR = 5                  # rho_w = 5 delta (mu = 1/5)
DY = 2 ** 48
STR_DIGITS = 40


def cfg_hash(extra=""):
    src = ""
    here = os.path.dirname(os.path.abspath(__file__))
    for f in ("hkcore.py", "hkquad.py", "hkbounds.py", "hkchannel.py"):
        src += open(os.path.join(here, f), "rb").read().hex()[:0] + hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()
    return hashlib.sha256((src + extra).encode()).hexdigest()[:16]


def a2s(x):
    return x.str(STR_DIGITS, radius=True)


def s2a(s):
    return arb(s)


class Ledger:
    def __init__(self, path, cfg):
        self.path = path
        self.cfg = cfg
        self.rows = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    r = json.loads(line)
                    if r.get("cfg") == cfg:
                        self.rows[r["key"]] = r

    def get(self, key):
        return self.rows.get(key)

    def put(self, key, row):
        row = dict(row)
        row["key"] = key
        row["cfg"] = self.cfg
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        self.rows[key] = row


def panel_edges(e_top, e_min):
    """dyadic edges e_0 = e_top > e_1 > ... > e_K >= e_min (approximately geometric with ratio 9/11)"""
    edges = [arb(e_top)]
    with H.precision():
        while True:
            nxt = edges[-1] * PANEL_SHRINK[0] / PANEL_SHRINK[1]
            n = int(float(nxt.mid()) * DY)
            e = arb(n) / DY
            if e < arb(e_min):
                break
            edges.append(e)
    return edges


def do_panel(eq, lo, hi, prec_bits=H.PREC):
    """certified per-mode (IP, IS, IN) on [lo, hi] plus diagnostics"""
    t0 = time.time()
    with H.precision(prec_bits):
        lo = arb(lo); hi = arb(hi)
        w0 = (lo + hi) / 2
        delta = (hi - lo) / 2
        rho_w = RHO_FACTOR * delta
        P = H.make_plan(eq, lo, hi, wmax_disk=w0 + rho_w, wmin_disk=w0 - rho_w)
        B, eta = H.uniform_bounds(eq, P, w0, delta, rho_w)
        co = H.jet_solve(eq, P, w0)
        mu = delta / rho_w
        rA = B * mu ** H.JET_LEN / (1 - mu) + eta
        IP, IS, IN, info = Q.panel_integrals(co, rA, w0, delta)
        return IP, IS, IN, {"B": B.str(5), "eta": eta.str(5), "rA": rA.str(5), "eG": info["eG"],
                            "steps": len(P.steps), "R": float(P.R), "M": P.M, "sec": round(time.time() - t0, 3)}


def run_channel(s, l, ledger, tol_P=arb("1e-17"), tol_S=arb("1e-15"), w_floor=arb("1e-6"), log=None,
                max_panels=None):
    """per-mode certified P, S for the Regge-Wheeler channel (s, l).  Returns dict of arb strings + diagnostics."""
    eq = H.Eq("RW", s, l)
    L = l * (l + 1)
    c = 2 * (1 - s * s)
    t0 = time.time()
    edges = panel_edges(W_HI, w_floor)
    with H.precision():
        IP = arb(0); IS = arb(0)
        npan = 0
        stop_edge = None
        IRP = IRS = None
        for k in range(len(edges) - 1):
            hi, lo = edges[k], edges[k + 1]
            # can the IR bound already close (0, hi]?
            irk = "IR|%d|%d|%s" % (s, l, a2s(hi))
            row = ledger.get(irk) if ledger else None
            if row is None:
                p, sb, nb = HB.ir_region(L, c, hi)
                row = {"P": a2s(p), "S": a2s(sb), "bands": nb}
                if ledger:
                    ledger.put(irk, row)
            p, sb = s2a(row["P"]), s2a(row["S"])
            if p < tol_P and sb < tol_S:
                stop_edge = hi
                IRP, IRS = p, sb
                break
            if max_panels is not None and npan >= max_panels:
                return None
            key = "PAN|%d|%d|%d|%s|%s" % (s, l, k, a2s(lo), a2s(hi))
            row = ledger.get(key) if ledger else None
            if row is None:
                ip, is_, in_, info = do_panel(eq, lo, hi)
                row = {"IP": a2s(ip), "IS": a2s(is_), "IN": a2s(in_), "info": info}
                if ledger:
                    ledger.put(key, row)
                if log:
                    log("  s=%d l=%d panel %d [%.6g, %.6g] P=%s S=%s %.2fs" % (s, l, k, float(lo), float(hi),
                        ip.str(8), is_.str(8), info["sec"]))
            IP += s2a(row["IP"]); IS += s2a(row["IS"])
            npan += 1
        if stop_edge is None:
            raise H.Refuse("channel s=%d l=%d: IR bound did not close above the floor %s" % (s, l, w_floor))
        TP = HB.planck_tail_P(W_HI)
        TS = HB.planck_tail_S(W_HI)
        P = IP + arb(0, 0) + arb((IRP + TP) / 2, ((IRP + TP) / 2).upper())
        S = IS + arb((IRS + TS) / 2, ((IRS + TS) / 2).upper())
        return {"s": s, "l": l, "P_mode": a2s(P), "S_mode": a2s(S), "panels": npan, "E_ir": a2s(stop_edge),
                "IR_P": a2s(IRP), "IR_S": a2s(IRS), "tail_P": a2s(TP), "tail_S": a2s(TS),
                "sec": round(time.time() - t0, 2)}
