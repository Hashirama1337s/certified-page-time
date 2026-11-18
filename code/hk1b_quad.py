"""hk1b_quad - v2 panel quadrature for BAR-HK-1b (build seat build-1, 2026-11-17).  New file; pinned hkquad.py untouched.

Change from hkquad.panel_integrals (v1): v1 enclosed the Lagrange remainder by Taylor-shifting the degree-126 polynomial
Q(u) = |P(u)|^2 directly to a BALL c +/- h.  On panels where Q varies by orders of magnitude (the turn-on just under a
barrier peak: s=1 l=8 panel [1.31, 1.60] has Q from 4.8e4 down to 3.5) the ball shift cancels terms ~5e4 to get ~3.5,
the enclosure of Q contains 0 and no halving depth helps (main_hk1.log l.180, diagnosed 2026-11-17).
v2: first shift Q exactly to the POINT c (all coefficients, rounding radii only), then evaluate the ball t in [-h, h]
on the re-centred polynomial, whose coefficients carry no cancellation.  Everything else (series integrands, exact
polynomial integration, Lagrange remainder, rA handling) is the v1 mathematics.
"""
from flint import arb, arb_series
import hkcore as H
import hkquad as Q1          # reuse the v1 helpers (_taylor_shift, constants) unchanged

K_ORDER = Q1.K_ORDER
REL_REM = Q1.REL_REM
MAX_DEPTH = 9


def _integrands_shifted(Qshift, w0, delta, c, t_ball, K):
    """series in t (|t| <= ...) of FP, FS, FN at u = c + t0 where t0 = t_ball (a ball around 0 or exact 0);
    Qshift = coefficients of Q(c + t) in t (exact re-centring at the point c)"""
    Qs = arb_series(Q1._taylor_shift(Qshift, t_ball, K + 2))
    ws = arb_series([w0 + delta * (c + t_ball), delta])
    e8 = (ws * (8 * arb.pi())).exp()
    ns = 1 / (e8 - 1)
    G = 1 / Qs
    N = ns * G
    FP = ws * N
    FS = (1 + N) * (1 + N).log() - N * N.log()
    return FP, FS, N


def panel_integrals(co, rA, w0, delta, m=8, K=K_ORDER, prec_bits=H.PREC):
    H.require_cap(K + 2)
    with H.precision(prec_bits):
        w0 = arb(w0); delta = arb(delta); rA = arb(rA)
        re = [c.real * delta ** k for k, c in enumerate(co)]
        im = [c.imag * delta ** k for k, c in enumerate(co)]
        d = len(co)
        Qc = []
        for k in range(2 * d - 1):
            v = arb(0)
            for i in range(max(0, k - d + 1), min(k, d - 1) + 1):
                v += re[i] * re[k - i] + im[i] * im[k - i]
            Qc.append(v)
        m = max(m, int(float((delta * 8 * arb.pi() / arb("0.08")).upper())) + 1)
        stats = {"subintervals": 0, "max_depth": 0}

        def one(c, h, depth):
            Qsh = Q1._taylor_shift(Qc, c, len(Qc))          # exact re-centring at the point c
            ok = True
            out = []
            try:
                FP, FS, FN = _integrands_shifted(Qsh, w0, delta, c, arb(0), K)
                tb = arb(0, h.upper())
                FPb, FSb, FNb = _integrands_shifted(Qsh, w0, delta, c, tb, K)
                Qb = Q1._taylor_shift(Qsh, tb, 1)[0]
            except (ValueError, ZeroDivisionError):
                ok = False
            if ok:
                for F, Fb in ((FP, FPb), (FS, FSb), (FN, FNb)):
                    cs = F.coeffs()
                    v = arb(0)
                    for k in range(0, min(K, len(cs) - 1) + 1, 2):
                        v += cs[k] * 2 * h ** (k + 1) / (k + 1)
                    csb = Fb.coeffs()
                    if len(csb) <= K + 1:
                        ok = False
                        break
                    rem = abs(csb[K + 1]) * 2 * h ** (K + 2) / (K + 2)
                    if not rem.is_finite() or not (rem <= REL_REM * abs(v) or depth >= MAX_DEPTH):
                        ok = False
                        break
                    out.append(v + arb(0, arb(rem.upper())))
            if not ok:
                if depth >= MAX_DEPTH:
                    raise H.Refuse("v2 panel_integrals: sub-interval remainder not controlled at depth %d" % depth)
                a = one(c - h / 2, h / 2, depth + 1)
                b = one(c + h / 2, h / 2, depth + 1)
                return [a[0][i] + b[0][i] for i in range(3)], a[1].min(b[1])
            stats["subintervals"] += 1
            stats["max_depth"] = max(stats["max_depth"], depth)
            return out, arb(Qb.lower())

        h = arb(1) / m
        IP = arb(0); IS = arb(0); IN = arb(0)
        Qmin = None
        for j in range(m):
            c = -1 + (2 * j + 1) * h
            vals, ql = one(c, h, 0)
            IP += vals[0] * delta; IS += vals[1] * delta; IN += vals[2] * delta
            Qmin = ql if Qmin is None else Qmin.min(ql)
        sq = Qmin.sqrt() if Qmin > 0 else arb(0)
        low = (sq - rA).max(arb(1))
        eG = arb((((low + rA) / low) ** 2 - 1).upper())
        if not eG < arb("0.5"):
            raise H.Refuse("v2 panel_integrals: TM remainder too large (eG = %s)" % eG)
        IP_t = IP + arb(0, (abs(IP) * eG).upper())
        IS_t = IS + arb(0, (abs(IS) * eG + 2 * eG * eG * abs(IN)).upper())
        IN_t = IN + arb(0, (abs(IN) * eG).upper())
        return IP_t, IS_t, IN_t, {"eG": eG.str(5), "Qmin": Qmin.str(5), "subintervals": stats["subintervals"],
                                  "max_depth": stats["max_depth"]}
