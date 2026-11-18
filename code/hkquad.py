"""hkquad - certified frequency integrals over one Taylor-model panel (build seat build-1, 2026-11-17).

On the real panel w = w0 + e, |e| <= delta, the Jost coefficient satisfies A(w) in P(e) + disc(rA) (hkcore).
Gamma = 1/|A|^2 with |A| >= 1 (flux), so with Q(e) = |P(e)|^2 (a real polynomial: Re P^2 + Im P^2) and Qmin >= min Q,
    Gamma in Gamma_P (1 +/- eG),   Gamma_P = 1/Q,   eG = (s/(s - rA))^2 - 1,  s = max(1, sqrt(Qmin)) - rA ... (see code)
Integrands (per mode, before the factor 2(2l+1)/(2 pi)):  FP = w n Gamma,  FS = S(n Gamma),  FN = n Gamma (auxiliary),
n = 1/(e^{8 pi w} - 1), S(N) = (1+N) ln(1+N) - N ln N.  Each sub-interval [c - h, c + h] of the panel is integrated by
a degree-K Taylor polynomial at c (arb_series, exact integration) plus the Lagrange remainder bounded by the
(K+1)-th Taylor coefficient enclosed over the whole sub-interval (series evaluated at the ball c +/- h).
Error from rA: int FP(true) in IP (1 +/- eG);  |S(N) - S(N_P)| <= eG S(N_P) + 2 eG^2 N_P.
"""
from flint import arb, acb, arb_series, arb_poly, ctx
import hkcore as H

K_ORDER = 16
REL_REM = arb("1e-15")      # accepted remainder relative to the sub-interval value
MAX_DEPTH = 7


def _real_polys(co):
    re = arb_poly([c.real for c in co])
    im = arb_poly([c.imag for c in co])
    return re, im


def _taylor_shift(coeffs, c, n):
    """first n Taylor coefficients in t of sum coeffs[k] (c + t)^k (classical Horner on coefficient lists; c may be
    a ball, then every coefficient is enclosed for all centres in the ball)"""
    acc = [arb(0)] * n
    for ck in reversed(coeffs):
        new = [acc[0] * c + ck]
        for j in range(1, n):
            new.append(acc[j] * c + acc[j - 1])
        acc = new
    return acc


def _integrands(Qc, w0, delta, c, K):
    """series in t of FP, FS, FN at u = c (c may be a ball) where w = w0 + delta (c + t), up to t^(K+1)"""
    Qs = arb_series(_taylor_shift(Qc, c, K + 2))
    ws = arb_series([w0 + delta * c, delta])
    e8 = (ws * (8 * arb.pi())).exp()
    ns = 1 / (e8 - 1)
    G = 1 / Qs
    N = ns * G
    FP = ws * N
    FS = (1 + N) * (1 + N).log() - N * N.log()
    return FP, FS, N


def panel_integrals(co, rA, w0, delta, m=8, K=K_ORDER, prec_bits=H.PREC):
    """(IP, IS, IN) arb enclosures of the per-mode integrals over [w0 - delta, w0 + delta]."""
    H.require_cap(K + 2)
    with H.precision(prec_bits):
        w0 = arb(w0); delta = arb(delta); rA = arb(rA)
        # scaled variable u = (w - w0)/delta in [-1, 1]; Q(u) = Re(P)^2 + Im(P)^2 with P_k delta^k, by classical
        # convolution (fast polynomial products lose relative accuracy when coefficient sizes span many decades)
        re = [c.real * delta ** k for k, c in enumerate(co)]
        im = [c.imag * delta ** k for k, c in enumerate(co)]
        d = len(co)
        Qc = []
        for k in range(2 * d - 1):
            v = arb(0)
            for i in range(max(0, k - d + 1), min(k, d - 1) + 1):
                v += re[i] * re[k - i] + im[i] * im[k - i]
            Qc.append(v)
        # sub-intervals of u in [-1, 1]: the Lagrange remainder is enclosed over the ball c +/- h, so a sub-interval
        # is halved (recursively) until its remainder is <= REL_REM of its value (or the depth limit is reached)
        m = max(m, int(float((delta * 8 * arb.pi() / arb("0.08")).upper())) + 1)
        stats = {"subintervals": 0, "max_depth": 0}

        def one(c, h, depth):
            FP, FS, FN = _integrands(Qc, w0, delta, c, K)
            cb = arb(c, h.upper())
            ok = True
            out = []
            try:
                FPb, FSb, FNb = _integrands(Qc, w0, delta, cb, K)
                Qb = _taylor_shift(Qc, cb, 1)[0]
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
                    raise H.Refuse("panel_integrals: sub-interval remainder not controlled at depth %d" % depth)
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
            IP += vals[0] * delta; IS += vals[1] * delta; IN += vals[2] * delta      # dw = delta du
            Qmin = ql if Qmin is None else Qmin.min(ql)
        # the TM remainder rA: |A| >= 1 and |A| >= sqrt(Qmin) - rA
        sq = Qmin.sqrt() if Qmin > 0 else arb(0)
        low = (sq - rA).max(arb(1))           # lower bound of |A| on the panel
        # Gamma/Gamma_P = |P|^2/|A|^2 with ||P| - |A|| <= rA:  in [(|A|/(|A|+rA))^2, ((|A|+rA)/|A|)^2]
        eG = ((low + rA) / low) ** 2 - 1
        eG = arb(eG.upper())
        if not eG < arb("0.5"):
            raise H.Refuse("panel_integrals: TM remainder too large (eG = %s)" % eG)
        IP_t = IP + arb(0, (abs(IP) * eG).upper())
        IS_t = IS + arb(0, (abs(IS) * eG + 2 * eG * eG * abs(IN)).upper())
        IN_t = IN + arb(0, (abs(IN) * eG).upper())
        return IP_t, IS_t, IN_t, {"eG": eG.str(5), "Qmin": Qmin.str(5), "subintervals": stats["subintervals"],
                                  "max_depth": stats["max_depth"]}
