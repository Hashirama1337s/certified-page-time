"""hkbounds - rigorous one-sided bounds for BAR-HK-1 (build seat build-1, 2026-11-17).

In plain words: where the greybody factor is tiny (low frequency, or high multipole l) we do not solve the wave
equation; we prove an upper bound on Gamma instead, and where the Planck factor is tiny we use Gamma <= 1.

(a) Hyperbolic transfer-matrix bound (real w, Regge-Wheeler with V >= 0).  Write psi = a e^{-iwx} + b e^{iwx}
    (x tortoise); flux gives |a|^2 - |b|^2 = 1, so |a| = cosh T, |b| = sinh T, Gamma = sech^2 T(+inf).
    (i)  Speed bound: d|a|^2/dx = (V/w) Re(i conj(a) b e^{2iwx}) => |dT/dx| <= V/(2w)   (|.| of a product <= cosh sinh).
    (ii) The (a,b) transfer over [x_a, x_b] is E_b^{-1} P0^{-1} N P0 E_a with N the real fundamental matrix of
         y'' = (V - w^2) y in the (y, y_x) basis and E rotations about 0 of the disk; 2T is the hyperbolic distance
         d(0, z) (z = b/a), rotations about 0 keep it, and a hyperbolic isometry moves every point by at least its
         translation length l = 2 arccosh(|tr N|/2).  Hence
              2 T(inf) >= 2 arccosh(tr N / 2) - (1/w) [ int_{-inf}^{x_a} V dx + int_{x_b}^{inf} V dx ].
    (iii) Comparison: on the core V - w^2 >= q_j >= 0 (cell j, constant q_j), so N >= prod_j C_j entrywise with
         C_j = [[cosh a_j, sinh a_j/sqrt q_j],[sqrt q_j sinh a_j, cosh a_j]], a_j = sqrt(q_j) h_j, h_j the tortoise
         length (nonnegative matrices; standard Sturm comparison).  For w in a band [w_lo, w_hi] use q_j from w_hi and
         the shoulders with 1/w_lo (both monotone in w).
    Exact shoulder integrals (V/f = L/r^2 + c/r^3):  int_{-inf}^{x_a} V dx = L(1/2 - 1/r_a) + (c/2)(1/4 - 1/r_a^2),
    int_{x_b}^{inf} V dx = L/r_b + c/(2 r_b^2).
(b) Planck tails with Gamma <= 1 (n = 1/(e^{8 pi w} - 1); S(N) = (1+N)ln(1+N) - N ln N increasing in N, and
    S(n) = ln(1+n) + 8 pi w n exactly because 1 + 1/n = e^{8 pi w}):
       int_W^inf w n dw   <= e^{-8piW} (W/(8pi) + 1/(8pi)^2) / (1 - e^{-8piW})
       int_W^inf S(n) dw  <= e^{-8piW} (W + 2/(8pi)) / (1 - e^{-8piW})
       int_0^eps w n dw   <= eps/(8pi);   int_0^eps S(n) dw <= eps (2 + ln(1 + 1/(8 pi eps)))
(c) Large-l lemma (s = 1, 2; c <= 0): V_L >= L' U, U = f/r^2, L' = L - 3 (c/r^3 >= -6/r^3 >= -3/r^2 for r >= 2).
    With w = wt sqrt(L'), cells with U - wt_hi^2 >= qt_j >= 0 give 2T >= sqrt(L') G - 2 n ln 2, where
    G = 2 sum_j sqrt(qt_j) h_j - (L/L')(1/wt_lo) [(1/2 - 1/r_a) + 1/r_b] (from prod cosh >= 2^{-n} e^{sum a}).
Ideas credited (not copied): transfer-matrix / rapidity bounds and constant comparison cells as used by Newton,
Zenodo 10.5281/zenodo.22800587 (eqs. (35)-(38), file seats/gate-1/src/zenodo_22800587.txt l.394-447); Visser-type
speed bound (Boonserm-Visser arXiv:0806.2209, ABSTRACT-level reference only).
"""
import math
from flint import arb, ctx
import hkcore as H

PI8 = None


def pi8():
    return 8 * arb.pi()


def V_rw(L, c, r):
    return (r - 2) * (L * r + c) / r ** 4


def V_d(L, c, d):
    r = 2 + d
    return d * (L * r + c) / r ** 4


def tort(r):
    return r + 2 * (r / 2 - 1).log()


def _turning_points(L, c, W2):
    """float search: inner delta_a = r_a - 2 (V increasing) and outer r_b (V decreasing) with V = W2;
    None if max V < W2.  The inner point is returned as delta = r - 2 (it can be ~1e-40)."""
    def Vd(d):                      # V at r = 2 + d
        r = 2.0 + d
        return d * (L * r + c) / r ** 4

    def V(r):
        return (r - 2) * (L * r + c) / r ** 4
    lo, hi = 2.0, 10.0
    for _ in range(200):
        m1 = lo + (hi - lo) / 3; m2 = hi - (hi - lo) / 3
        if V(m1) < V(m2):
            lo = m1
        else:
            hi = m2
    rp = (lo + hi) / 2
    if V(rp) <= W2:
        return None
    a, b = 0.0, rp - 2
    for _ in range(400):
        m = (a + b) / 2 if a > 0 else b / 1e3
        if Vd(m) < W2:
            a = m
        else:
            b = m
        if a > 0 and b / a < 1 + 1e-12:
            break
    da = b
    a, b = rp, rp * 2
    it = 0
    while V(b) > W2:
        b *= 2
        it += 1
        if it > 400:
            raise H.Refuse("turning point search")
    for _ in range(200):
        m = (a + b) / 2
        if V(m) > W2:
            a = m
        else:
            b = m
    rb = a
    return da, rb, rp


def _cells(da, rb, ratio=1.08):
    """cell boundaries as ('d', delta) for r < 4 (r = 2 + delta) and ('r', r) beyond"""
    pts = [("d", da)]
    d = da
    while 2 + d < min(4.0, rb):
        d = min(d * ratio, 2.0, rb - 2)
        pts.append(("d", d))
        if len(pts) > 100000:
            raise H.Refuse("cells")
    r = 2 + d
    while r < rb:
        r = min(r * ratio, rb)
        pts.append(("r", r))
        if len(pts) > 100000:
            raise H.Refuse("cells")
    return pts


def _pt_r(p):
    kind, v = p
    if kind == "d":
        return 2 + arb(v), arb(v)
    return arb(v), arb(v) - 2


def _tort_diff(p0, p1):
    r0, d0 = _pt_r(p0)
    r1, d1 = _pt_r(p1)
    return (d1 - d0) + 2 * (d1 / d0).log()


def _prod_trace(cells_q_h):
    """lower bound of tr(prod C_j) (C_j nonnegative), cells given as list of (q_j >= 0, h_j > 0) arbs"""
    M11, M12, M21, M22 = arb(1), arb(0), arb(0), arb(1)
    for q, h in cells_q_h:
        if q > 0:
            sq = q.sqrt()
            a = sq * h
            ch = a.cosh()
            sh = a.sinh()
            c11, c12, c21, c22 = ch, sh / sq, sq * sh, ch
        else:
            c11, c12, c21, c22 = arb(1), h, arb(0), arb(1)
        M11, M12, M21, M22 = (M11 * c11 + M12 * c21, M11 * c12 + M12 * c22,
                              M21 * c11 + M22 * c21, M21 * c12 + M22 * c22)
    return arb((M11 + M22).lower())


def gamma_band_bound(L, c, w_lo, w_hi, ratio=1.08):
    """certified upper bound of Gamma(w) for all w in [w_lo, w_hi] (Regge-Wheeler, V >= 0).  Returns arb in [0,1]."""
    with H.precision(128):
        w_lo = arb(w_lo); w_hi = arb(w_hi)
        W2 = w_hi * w_hi
        tp = _turning_points(L, c, float(W2.upper()))
        if tp is None:
            return arb(1)
        da, rb, rp = tp
        # shrink slightly so that V >= w_hi^2 holds on every cell (verified below)
        for shrink in (1e-9, 1e-6, 1e-4, 1e-2, 5e-2):
            da_s = da * (1 + shrink)
            rb_s = rb * (1 - shrink)
            if 2 + da_s >= rb_s:
                return arb(1)
            pts = _cells(da_s, rb_s, ratio)
            ok = True
            cells = []
            for i in range(len(pts) - 1):
                r0, d0 = _pt_r(pts[i]); r1, d1 = _pt_r(pts[i + 1])
                dd = arb((d0 + d1) / 2, ((d1 - d0) / 2).upper())
                # V on the cell, written with delta = r - 2 (exact near the horizon): V = d (L(2+d) + c)/(2+d)^4
                vlow = V_d(L, c, dd)
                v0 = V_d(L, c, d0); v1 = V_d(L, c, d1)
                # certified monotonicity on the cell: r^5 V'(r) = -2 L r^2 + (6L - 3c) r + 8c
                rr = 2 + dd
                dV = -2 * L * rr * rr + (6 * L - 3 * c) * rr + 8 * c
                if dV > 0:
                    vl = v0
                elif dV < 0:
                    vl = v1
                else:
                    vl = vlow
                q = vl - W2
                ql = arb(q.lower())
                if ql < 0:
                    ok = False          # V >= w_hi^2 not certified on this cell: shrink the core and retry
                    break
                h = _tort_diff(pts[i], pts[i + 1])
                cells.append((ql, h))
            if ok:
                break
        if not ok:
            return arb(1)
        tr = _prod_trace(cells)
        if not tr > 2:
            return arb(1)
        ell = 2 * (tr / 2).acosh()
        r_a, d_a = _pt_r(pts[0]); r_b, _ = _pt_r(pts[-1])
        # int_2^{r_a} (L/r^2 + c/r^3) dr = L d/(2 r_a) + c d (r_a + 2)/(8 r_a^2),  d = r_a - 2 (no cancellation)
        IL = L * d_a / (2 * r_a) + arb(c) * d_a * (r_a + 2) / (8 * r_a * r_a)
        IR = L / r_b + arb(c) / (2 * r_b * r_b)
        twoT = ell - (IL + IR) / w_lo
        if not twoT > 0:
            return arb(1)
        T = arb((twoT / 2).lower())
        G = 1 / T.cosh() ** 2
        return arb(G.upper()).min(arb(1))


def planck_tail_P(W):
    W = arb(W)
    e = (-pi8() * W).exp()
    return (e * (W / pi8() + 1 / pi8() ** 2) / (1 - e))


def planck_tail_S(W):
    W = arb(W)
    e = (-pi8() * W).exp()
    return e * (W + 2 / pi8()) / (1 - e)


def zero_region_P(eps):
    return arb(eps) / pi8()


def zero_region_S(eps):
    eps = arb(eps)
    return eps * (2 + (1 + 1 / (pi8() * eps)).log())


def S_of(N):
    """S(N) = (1+N) ln(1+N) - N ln N for an arb N >= 0 (upper/lower via monotonicity)"""
    if N <= 0:
        return arb(0)
    return (1 + N) * (1 + N).log() - N * N.log()


def nbar(w):
    w = arb(w)
    return 1 / ((pi8() * w).exp() - 1)


def band_contrib(Gmax, w_lo, w_hi):
    """(P, S) upper bounds for int over [w_lo, w_hi] with Gamma <= Gmax:  w n(w) = w/(e^{8 pi w}-1) is decreasing,
    so w n <= w_lo n(w_lo) (<= 1/(8 pi));  S(Gmax n(w)) <= S(Gmax n(w_lo)) (S increasing, n decreasing)"""
    w_lo = arb(w_lo); w_hi = arb(w_hi)
    width = w_hi - w_lo
    P = Gmax * width * (w_lo * nbar(w_lo)).min(1 / pi8())
    S = width * S_of(arb((Gmax * nbar(w_lo)).upper()))
    return arb(P.upper()), arb(S.upper())


def ir_region(L, c, E, eps=arb(10) ** -20, ratio=2):
    """upper bounds (P, S) of int_0^E for one (s,l) channel (per helicity-mode, before the 2(2l+1)/(2pi) factor)"""
    with H.precision(128):
        E = arb(E)
        P = zero_region_P(eps)
        S = zero_region_S(eps)
        hi = E
        bands = 0
        while hi > eps:
            lo = (hi / ratio).max(eps)
            G = gamma_band_bound(L, c, lo, hi)
            p, s = band_contrib(G, lo, hi)
            P += p; S += s
            hi = lo
            bands += 1
        return arb(P.upper()), arb(S.upper()), bands


def channel_tail_bound(L, c, W_planck_min=arb(1), eps=arb(10) ** -20):
    """(P, S) upper bounds for a whole channel l > L_t (per mode): IR bands up to where the band bound is useless,
    then Gamma <= 1 with the Planck tail.  Bands: ratio 2 below 0.05, ratio 1.05 above."""
    with H.precision(128):
        P = zero_region_P(eps)
        S = zero_region_S(eps)
        lo = arb(eps)
        while True:
            hi = lo * 2 if lo < arb(0.05) else lo * arb(1.05)
            G = gamma_band_bound(L, c, lo, hi)
            if G >= 1 or not G < 1:
                break
            p, s = band_contrib(G, lo, hi)
            P += p; S += s
            lo = hi
        P += planck_tail_P(lo)
        S += planck_tail_S(lo)
        return arb(P.upper()), arb(S.upper()), lo


# ---------------------------------------------------------------- (c) large-l lemma, all l > L_big at once
def _U_cells(wt_hi2, ratio):
    """cells for U(r) = (r-2)/r^3 >= wt_hi2 (U >= wt^2 core); returns (pts, ok)"""
    # turning points of U (peak at r = 3, U(3) = 1/27)
    if not wt_hi2 < arb(1) / 27:
        return None
    # U = V with L = 1, c = 0
    tp = _turning_points(1, 0, float(wt_hi2.upper()))
    if tp is None:
        return None
    return tp


def lemma_band(wt_lo, wt_hi, Lp_min, ratio=1.3):
    """for all L' >= Lp_min and w = wt sqrt(L'), wt in [wt_lo, wt_hi]:  2T >= sqrt(L') G - 2 n ln 2.
    Returns (G, n, S_tilde, I, r_a, r_b) with G possibly <= 0 (useless)."""
    with H.precision(128):
        wt_lo = arb(wt_lo); wt_hi = arb(wt_hi)
        W2 = wt_hi * wt_hi
        tp = _U_cells(W2, ratio)
        if tp is None:
            return None
        da, rb, rp = tp
        for shrink in (1e-9, 1e-6, 1e-4, 1e-2, 5e-2):
            pts = _cells(da * (1 + shrink), rb * (1 - shrink), ratio)
            ok = True
            St = arb(0)
            n = 0
            for i in range(len(pts) - 1):
                r0, d0 = _pt_r(pts[i]); r1, d1 = _pt_r(pts[i + 1])
                dd = arb((d0 + d1) / 2, ((d1 - d0) / 2).upper())
                rr = 2 + dd
                v0 = V_d(1, 0, d0); v1 = V_d(1, 0, d1)
                dV = -2 * rr * rr + 6 * rr           # r^5 U'(r) with L = 1, c = 0
                if dV > 0:
                    vl = v0
                elif dV < 0:
                    vl = v1
                else:
                    vl = V_d(1, 0, dd)
                q = arb((vl - W2).lower())
                if q < 0:
                    ok = False
                    break
                h = _tort_diff(pts[i], pts[i + 1])
                if q > 0:
                    St += q.sqrt() * h
                    n += 1
            if ok:
                break
        if not ok:
            return None
        r_a, d_a = _pt_r(pts[0]); r_b, _ = _pt_r(pts[-1])
        I = d_a / (2 * r_a) + 1 / r_b
        G = 2 * St - (1 + arb(3) / Lp_min) * I / wt_lo
        return arb(G.lower()), n, St, I, r_a, r_b


def large_l_lemma(L_big, wt_max=arb("0.1"), wt_min=arb("0.02"), band_ratio=arb("1.05"), rho=2, ratio=1.1):
    """Uniform bound for every l > L_big (s = 1, 2): with L' = l(l+1) - 3 and w <= wt_max sqrt(L'),
         Gamma_l(w) <= 4 exp(-min_k (sqrt(L') G_k - 2 n_k ln 2))  <=  K exp(-Gs (l - 1)),
    Gs = min_k G_k, K = 4 exp(-min_k [L_big (G_k - Gs) - 2 n_k ln 2])  (uses sqrt(L') >= l - 1 for l >= 2)."""
    with H.precision(128):
        Lp_min = arb((L_big + 1) * (L_big + 2) - 3)
        sLp = Lp_min.sqrt()
        rows = []
        GN = []
        hi = arb(wt_max)
        while hi > wt_min:
            lo = (hi / band_ratio).max(wt_min)
            res = lemma_band(lo, hi, Lp_min, ratio)
            if res is None or not res[0] > 0:
                raise H.Refuse("large-l lemma: band [%s, %s] not certified" % (lo.str(5), hi.str(5)))
            G, n = res[0], res[1]
            rows.append((lo.str(8), hi.str(8), G.str(8), n))
            GN.append((G, n))
            hi = lo
        # asymptotic regime wt <= wt_min: base band at wt_min, extension by far cells (see module doc)
        base = lemma_band(wt_min / rho, wt_min * arb("1.5"), Lp_min, ratio)   # core where U >= (1.5 wt_min)^2
        if base is None:
            raise H.Refuse("large-l lemma: base band")
        _, n_base, St_base, _, r_a0, r_b0 = base
        f0 = 1 - 2 / r_b0
        disc = f0 - (wt_min * r_b0) ** 2
        if not disc > 0:
            raise H.Refuse("large-l lemma: far-cell discriminant")
        s_far = (arb(rho) - 1) / rho * disc.sqrt()
        if not (9 * (wt_min / rho) ** 2 <= r_a0 - 2 and (2 + 9 * wt_min ** 2) ** 3 <= 9 and r_a0 <= 3):
            raise H.Refuse("large-l lemma: near-horizon premise")
        IL0 = (r_a0 - 2) / (2 * r_a0)
        NT = (rho * IL0 / wt_min).max(arb(9) / 4 * wt_min)
        G0 = 2 * St_base - (1 + arb(3) / Lp_min) * (NT + rho / (wt_min * r_b0))
        slope_ok = sLp * s_far >= arb(2).log()
        if not (G0 > 0 and slope_ok):
            raise H.Refuse("large-l lemma: asymptotic regime not certified")
        GN.append((arb(G0.lower()), n_base))
        Gs = GN[0][0]
        for G, n in GN:
            Gs = Gs.min(G)
        ln2 = arb(2).log()
        mstar = None
        for G, n in GN:
            v = L_big * (G - Gs) - 2 * n * ln2
            mstar = v if mstar is None else mstar.min(v)
        K = 4 * (-mstar).exp()
        return {"L_big": L_big, "Gs": arb(Gs.lower()), "K": arb(K.upper()), "wt_max": wt_max, "wt_min": wt_min,
                "bands": rows, "G0_asym": G0.str(10), "s_far": s_far.str(10), "n_base": n_base}


def S_lowfreq_bound(eps, W):
    """int_0^W S(N) dw for any N <= eps n(w), using n <= 1/(8 pi w):  w* = eps/(8 pi), L = ln(W/w*) (W > w*):
    <= w* (2 ln 2 + 1) + w* ((1 + ln 2) L + L^2/2)"""
    eps = arb(eps); W = arb(W)
    ws = eps / pi8()
    if not W > ws:
        return W * (2 + (1 + 1 / (pi8() * W)).log())
    Lg = (W / ws).log()
    ln2 = arb(2).log()
    return ws * (2 * ln2 + 1) + ws * ((1 + ln2) * Lg + Lg * Lg / 2)


def large_l_tail_sum(lem):
    """(P, S) upper bounds of sum_{l > L_big} (2l+1)/pi * [per-mode P, S] for one spin (both helicities included).
    eps_l = K e^{-Gs (l-1)};  W_l = wt_max sqrt(L') in [wt_max (l-1), wt_max (l+1)];  each series is bounded by its
    first term over (1 - ratio) with an explicit ratio bound valid for all l >= m (terms = polynomial x geometric)."""
    with H.precision(128):
        m = lem["L_big"] + 1
        G = lem["Gs"]
        K = lem["K"]
        wtm = arb(lem["wt_max"])
        x = (-G).exp()
        pi = arb.pi()
        p8 = pi8()
        y = (-p8 * wtm).exp()
        Wm = wtm * (m - 1)
        denom = 1 - (-p8 * Wm).exp()
        q = arb(2 * m + 3) / (2 * m + 1)
        q1 = arb(m + 2) / (m + 1)
        # P1: (2l+1)/pi * eps_l/384
        t1 = (2 * m + 1) / pi * K * x ** (m - 1) / 384
        r1 = q * x
        # P2: (2l+1)/pi * Planck_P(W_l) with W_l >= wt (l-1)
        t2 = (2 * m + 1) / pi * (-p8 * Wm).exp() * (wtm * (m + 1) / p8 + 1 / p8 ** 2) / denom
        r2 = q * q1 * y
        # S1: (2l+1)/pi * S_lowfreq(eps_l, W_l):  <= (2l+1)/pi * w*_l (a + b Lg_l + Lg_l^2/2),  w*_l = eps_l/(8 pi),
        #     Lg_l = ln(8 pi W_l/eps_l) <= ln(8 pi wt (l+1)/K) + G (l-1) =: c0 + G (l-1) (if c0 < 0 use 0 floor below)
        ln2 = arb(2).log()
        c0 = (p8 * wtm * (m + 1) / K).log()
        c0 = c0.max(arb(0))
        Lm = c0 + G * (m - 1)
        poly_m = (2 * ln2 + 1) + (1 + ln2) * Lm + Lm * Lm / 2
        t3 = (2 * m + 1) / pi * K * x ** (m - 1) / p8 * poly_m
        Lm1 = Lm + G + (p8 * wtm * (m + 2) / K).log().max(arb(0)) - c0   # bound of Lg at l = m+1 (monotone)
        poly_m1 = (2 * ln2 + 1) + (1 + ln2) * Lm1 + Lm1 * Lm1 / 2
        r3 = q * x * poly_m1 / poly_m * (arb(m + 2) / (m + 1)) ** 2
        # S2: (2l+1)/pi * Planck_S(W_l)
        t4 = (2 * m + 1) / pi * (-p8 * Wm).exp() * (wtm * (m + 1) + 2 / p8) / denom
        r4 = q * q1 * y
        for r in (r1, r2, r3, r4):
            if not r < 1:
                raise H.Refuse("large-l tail: ratio >= 1")
        P = t1 / (1 - r1) + t2 / (1 - r2)
        S = t3 / (1 - r3) + t4 / (1 - r4)
        return arb(P.upper()), arb(S.upper())
