"""hkcore - certified Schwarzschild scattering core for BAR-HK-1 (build seat build-1, 2026-11-17).

In plain words: for the wave equation of a field of spin s on a Schwarzschild black hole (M = 1) this module computes
the incoming Jost coefficient A_in(w) (greybody factor Gamma = 1/|A_in|^2) with every truncation bounded:

  ODE (r-form, polynomial coefficients)  P2(r) psi'' + P1(r) psi' + [P0a(r) + w^2 P0b(r)] psi = 0
     Regge-Wheeler (RW):  P2 = r^2 (r-2)^2, P1 = 2 r (r-2), P0a = -(r-2)(L r + c), P0b = r^4,  L = l(l+1), c = 2(1-s^2)
     Zerilli (Z, s = 2):  same with an extra factor D = (lam r + 3)^2 and N_Z = 2lam^2(lam+1) r^3 + 6lam^2 r^2 + 18 lam r + 18
  (1) horizon:  psi = x^rho sum a_n x^n, x = r - 2, rho = -2 i w (ingoing, |psi| -> 1); tail of the series bounded by
      a geometric majorant of the recurrence (|a_n| <= A zeta^n for n > N, proved by induction).
  (2) transfer 2+x0 -> R: Taylor steps on exact dyadic positions; tail of every step bounded by Cauchy's estimate on a
      disk of radius rho1 = KAPPA*h with a Gronwall bound for the solution on that disk (no naive ball stepping:
      the state is a ball, but each step's truncation is an explicit bound added to it).
  (3) R -> infinity: u_+ = e^{i w r*} h(r), h ~ sum c_m r^-m (exact recurrence); the remainder e = h - h_M is bounded by a
      Volterra contraction argument on the real axis (|e| <= gamma R^-M / M, |e'| <= gamma R^-(M+1)).
  (4) A_in = W_x(psi, u_+)/(2 i w), W_x = f (psi u' - psi' u); A_out = W_x(psi, u_-)/(-2 i w); flux |A_in|^2-|A_out|^2 = 1.

Two modes share one code path:
  point mode  - w an exact real (or ball), every truncation added as a ball radius -> certified A_in(w) enclosure.
  jet mode    - w = w0 + eps as an acb_series (length ctx.cap); fixed truncation orders define an explicit analytic
                approximant A_M(w); its Taylor coefficients at w0 are computed as balls.  Uniform bounds (see
                `uniform_bounds`) give  B >= sup |A_M| on the circle |w - w0| = rho_w  (Cauchy remainder) and
                eta >= sup |A - A_M| on the real panel [w0 - delta, w0 + delta].  Hence on the panel
                A(w0 + e) in sum_{k<cap} A_k e^k + disc(B mu^cap/(1 - mu) + eta),  mu = delta/rho_w.
Growth bounds along the path use the 2-norm of Y = (psi, psi'/sigma) and the logarithmic norm of the system matrix
(rate <= |sigma^2 - q|/(2 sigma) on a segment), so oscillation costs nothing and only genuine growth is paid.

Rules: ctx.cap is set once here; every public function restores ctx.prec in finally; no flint object is pickled.
Lab files: ideas from <RECON>/seats/computing/greybody.py (horizon series l.26-74, dyadic stepping l.194-206,
asymptotic recurrence l.141-180) - no code copied; all bounds here are new.
"""
import math
import contextlib
from flint import arb, acb, ctx, acb_series

ctx.cap = 64                      # set ONCE (lab rule); jets have exactly JET_LEN coefficients
JET_LEN = 64
PREC = 256
KAPPA = 4                         # Cauchy disk radius / step
DYADIC = 2 ** 30                  # step positions on this grid


class Refuse(Exception):
    """a hypothesis of a bound could not be certified; the caller records INCONCLUSIVE instead of a number"""


@contextlib.contextmanager
def precision(bits=PREC):
    old = ctx.prec
    ctx.prec = bits
    try:
        yield
    finally:
        ctx.prec = old


def require_cap(n):
    """refuse (never silently truncate) when a jet of length n is requested but ctx.cap is smaller"""
    if ctx.cap < n or n > JET_LEN:
        raise Refuse("cap-truncation: jets of length %d requested, ctx.cap = %d (JET_LEN %d)" % (n, ctx.cap, JET_LEN))


# ---------------------------------------------------------------- small exact polynomial helpers (python ints)
def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def pneg(a):
    return [-x for x in a]


def pshift_int(c, a):
    """coefficients of P(a + t) in t, P with integer coefficients, a an integer"""
    return [sum(c[k] * math.comb(k, j) * a ** (k - j) for k in range(j, len(c))) for j in range(len(c))]


def pshift(c, a):
    """coefficients of P(a + t) in t; a an arb (exact dyadic)"""
    out = []
    for j in range(len(c)):
        v = arb(0)
        for k in range(j, len(c)):
            if c[k]:
                v += c[k] * math.comb(k, j) * a ** (k - j)
        out.append(v)
    return out


def peval_abs(c, x):
    """sum |c_k| x^k for x >= 0 (upper bound of |P| on |r| <= x)"""
    v = arb(0)
    for k, ck in enumerate(c):
        if ck:
            v += abs(arb(ck)) * x ** k
    return v


def ub(x):
    """upper bound (as an exact arb) of |x| for arb/acb"""
    if isinstance(x, acb):
        return arb(abs(x).upper())
    return arb(abs(x).upper())


def lb(x):
    if isinstance(x, acb):
        return arb(abs(x).lower())
    return arb(abs(x).lower())


def ball(r):
    """real ball [0 +/- r] (r an arb upper bound)"""
    return arb(0, arb(r).upper())


def cball(r):
    r = arb(r).upper()
    return acb(arb(0, r), arb(0, r))


def crad(z):
    """upper bound of the distance from z's midpoint to any point of the complex box z"""
    return arb((z.real.rad() ** 2 + z.imag.rad() ** 2).sqrt().upper())


# ---------------------------------------------------------------- equations
class Eq:
    """kind 'RW' (Regge-Wheeler, spin s) or 'Z' (Zerilli, even parity, s = 2); multipole l"""

    def __init__(self, kind, s, l):
        assert kind in ("RW", "Z")
        self.kind, self.s, self.l = kind, s, l
        self.L = L = l * (l + 1)
        if kind == "RW":
            self.c = 2 * (1 - s * s)
            self.D = [1]
            self.NU = [self.c, L]                                    # V/f = NU(r)/(r^3 D(r))
            self.lam = None
        else:
            assert s == 2 and l >= 2
            lam = (l - 1) * (l + 2) // 2
            self.lam = lam
            self.c = None
            self.D = [9, 6 * lam, lam * lam]
            self.NU = [18, 18 * lam, 6 * lam * lam, 2 * lam * lam * (lam + 1)]
        D = self.D
        self.P2 = pmul(pmul([0, 0, 1], [4, -4, 1]), D)              # r^2 (r-2)^2 D
        self.P1 = pmul([0, -4, 2], D)                                # 2 r (r-2) D
        self.P0a = pneg(pmul([-2, 1], self.NU))                      # -(r-2) NU
        self.P0b = pmul([0, 0, 0, 0, 1], D)                          # r^4 D
        # horizon polynomials in x = r - 2:  P2 = x^2 p2, P1 = x p1, P0 = p0a + w^2 p0b
        P2x = pshift_int(self.P2, 2)
        P1x = pshift_int(self.P1, 2)
        assert P2x[0] == 0 and P2x[1] == 0 and P1x[0] == 0
        self.p2 = P2x[2:]
        self.p1 = P1x[1:]
        self.p0a = pshift_int(self.P0a, 2)
        self.p0b = pshift_int(self.P0b, 2)
        J = max(len(self.p2), len(self.p1), len(self.p0a), len(self.p0b))
        self.p2 += [0] * (J - len(self.p2)); self.p1 += [0] * (J - len(self.p1))
        self.p0a += [0] * (J - len(self.p0a)); self.p0b += [0] * (J - len(self.p0b))
        # indicial structure used by the majorant: F_0(sigma) = p2_0 (sigma^2 + 4 w^2)
        assert self.p1[0] == self.p2[0] and self.p0a[0] == 0 and self.p0b[0] == 4 * self.p2[0]
        # far field h-ODE  a2 h'' + a1 h' + a0 h = 0 with a2 = r^2 (r-2) D, a1 = A1a + (i w) A1c, a0 = -NU
        self.a2 = pmul([0, 0, -2, 1], D)
        self.A1a = pmul([0, 2], D)
        self.A1c = pmul([0, 0, 0, 2], D)
        self.a0 = pneg(self.NU)
        self.d1 = len(self.A1c) - 1
        assert len(self.a2) - 1 == self.d1 and len(self.a0) - 1 == self.d1 - 2

    def name(self):
        return "%s s=%d l=%d" % (self.kind, self.s, self.l)

    # --- magnitude bounds on a complex disk / segment (r with Re r >= rmin, |r| <= rmax, |r - 2| >= dmin)
    def Dlow(self, rmin):
        if self.kind == "RW":
            return arb(1)
        return (self.lam * rmin + 3) ** 2

    def NUabs(self, rmax):
        return peval_abs(self.NU, rmax)

    def pq_sup(self, rmin, rmax, dmin, wmax):
        """upper bounds of |p| = |P1/P2| and |q| = |P0/P2| for Re r >= rmin, |r| <= rmax, |r-2| >= dmin, |w| <= wmax"""
        if not (dmin > 0 and rmin > 0):
            raise Refuse("pq_sup: disk touches a singular point")
        p = 2 / (rmin * dmin)
        q = wmax ** 2 * rmax ** 2 / dmin ** 2 + self.NUabs(rmax) / (rmin ** 2 * dmin * self.Dlow(rmin))
        return arb(p.upper()), arb(q.upper())

    def g1g2(self, r):
        """q = w^2 g1(r) - g2(r) on real r (arb ball allowed)"""
        g1 = r * r / ((r - 2) * (r - 2))
        NU = arb(0)
        for k, ck in enumerate(self.NU):
            NU += ck * r ** k
        D = arb(0)
        for k, ck in enumerate(self.D):
            D += ck * r ** k
        g2 = NU / (r * r * (r - 2) * D)
        return g1, g2

    def KU(self, R):
        """sup_{t >= R} t^2 |U(t)|, U = V/f"""
        if self.kind == "RW":
            return self.L + abs(arb(self.c)) / R
        lam = self.lam
        return 2 * (lam + 1) + arb(6) / R + arb(18) / (lam * R * R) + arb(18) / (lam * lam * R ** 3)

    def Dlead(self):
        return self.D[-1]


# ---------------------------------------------------------------- generic numbers (acb or acb_series)
def _is_series(x):
    return isinstance(x, acb_series)


def _exp(x):
    return x.exp()


# ---------------------------------------------------------------- (1) horizon Frobenius start
def frob_coeffs(eq, w, N):
    """a_0..a_N for psi = x^rho sum a_n x^n (w: acb or acb_series).  Returns (a, rho)."""
    I = acb(0, 1)
    rho = -2 * I * w
    w2 = w * w
    p2, p1, p0a, p0b = eq.p2, eq.p1, eq.p0a, eq.p0b
    J = len(p2) - 1
    one = acb(1) if not _is_series(w) else acb_series([1])
    a = [one]
    for n in range(1, N + 1):
        num = None
        for j in range(1, J + 1):
            if n - j < 0:
                break
            sig = (n - j) + rho
            Fj = sig * (sig - 1) * p2[j] + sig * p1[j] + p0a[j] + w2 * p0b[j]
            t = Fj * a[n - j]
            num = t if num is None else num + t
        # F_0(n + rho) = p2_0 ((n+rho)^2 + 4 w^2) = p2_0 n (n - 4 i w)  (identity checked in Eq.__init__)
        F0 = (n - 4 * I * w) * (n * p2[0])
        a.append(-num / F0)
    return a, rho


def frob_tail(eq, wmax, N, a_abs_last, x0):
    """majorant tail of the horizon series for n > N, uniform over |w| <= wmax.
    a_abs_last: upper bounds of |a_k| for k = N-J+1..N (list, last = |a_N|).  Returns (tail_S, tail_dS) bounds for
    sum_{n>N} |a_n| x0^n and sum_{n>N} |n + rho| |a_n| x0^n."""
    p2, p1, p0a, p0b = eq.p2, eq.p1, eq.p0a, eq.p0b
    J = len(p2) - 1
    n1 = arb(N + 1)
    rho_abs = 2 * wmax
    u = rho_abs / n1
    den = abs(arb(p2[0])) * (1 - 4 * wmax / n1)
    if not den > 0:
        raise Refuse("frob_tail: N too small for w")
    beta = []
    for j in range(1, J + 1):
        num = (abs(arb(p2[j])) * (1 + u) ** 2 + (abs(arb(p2[j])) + abs(arb(p1[j]))) * (1 + u) / n1
               + (abs(arb(p0a[j])) + wmax ** 2 * abs(arb(p0b[j]))) / n1 ** 2)
        beta.append(num / den)
    # find zeta with sum beta_j zeta^-j <= 1 (bisection in floats, verified in arb)
    lo, hi = 1e-6, 1e6
    bf = [float(b.upper()) for b in beta]
    for _ in range(200):
        z = math.sqrt(lo * hi)
        if sum(b * z ** (-(j + 1)) for j, b in enumerate(bf)) <= 1:
            hi = z
        else:
            lo = z
    zeta = arb(hi * 1.0001)
    chk = sum((beta[j] * zeta ** (-(j + 1)) for j in range(J)), arb(0))
    if not chk <= 1:
        raise Refuse("frob_tail: majorant root not verified")
    y = zeta * x0
    if not y < 1:
        raise Refuse("frob_tail: zeta*x0 = %s >= 1, choose smaller x0" % y)
    A = arb(0)
    for i, ak in enumerate(a_abs_last):
        k = N - (len(a_abs_last) - 1) + i
        A = A.max(arb(ak) / zeta ** k) if A > 0 else arb(ak) / zeta ** k
    tS = A * y ** (N + 1) / (1 - y)
    # sum_{n>N} (n + |rho|) y^n
    sn = y ** (N + 1) * ((N + 1) - N * y) / (1 - y) ** 2
    tD = A * (sn + rho_abs * y ** (N + 1) / (1 - y))
    return arb(tS.upper()), arb(tD.upper())


def horizon_start(eq, w, x0, N, point_tail=None):
    """psi(2+x0), psi_r(2+x0) for the ingoing solution; point_tail = (tS, tD) bounds added as radii (point mode)"""
    a, rho = frob_coeffs(eq, w, N)
    lx = arb(x0).log()
    S = None; Sd = None
    xp = arb(1)
    for n in range(N + 1):
        t = a[n] * xp
        S = t if S is None else S + t
        td = (n + rho) * t
        Sd = td if Sd is None else Sd + td
        xp = xp * x0
    xr = _exp(rho * lx)
    psi = xr * S
    dpsi = xr * Sd / x0
    if point_tail is not None:
        tS, tD = point_tail
        mag = ub(xr) if not _is_series(xr) else None
        psi = psi + cball(mag * tS)
        dpsi = dpsi + cball(mag * tD / x0)
    return psi, dpsi, a


# ---------------------------------------------------------------- (2) step plan and Taylor steps
class Step:
    __slots__ = ("an", "hn", "N", "a", "h", "Q2h", "Q1h", "Q0ah", "Q0bh")


def plan_steps(eq, x0, R, wmax, ch=0.6, theta=0.1875, nterms=None, tol_rel=1e-22):
    """dyadic step plan from 2 + x0 to R valid for |w| <= wmax (floats only decide positions; bounds are in arb)"""
    an = int(round((2 + x0) * DYADIC))
    Rn = int(round(R * DYADIC))
    steps = []
    while an < Rn:
        a = an / DYADIC
        rho = a - 2
        hmax_sing = theta * rho
        # local |q| estimate at a (float)
        g1 = a * a / (rho * rho)
        nu = sum(abs(c) * a ** k for k, c in enumerate(eq.NU))
        dd = sum(c * a ** k for k, c in enumerate(eq.D))
        q = wmax * wmax * g1 + nu / (a * a * rho * dd)
        hmax_w = ch / math.sqrt(q)
        h = min(hmax_sing, hmax_w)
        hn = max(1, min(int(h * DYADIC), Rn - an))
        st = Step()
        st.an, st.hn = an, hn
        st.N = None
        steps.append(st)
        an += hn
    return steps, an


def prepare_step(eq, st, prec_bits=None):
    a = arb(st.an) / DYADIC
    h = arb(st.hn) / DYADIC
    st.a, st.h = a, h
    Q2 = pshift(eq.P2, a)
    Q1 = pshift(eq.P1, a)
    Q0a = pshift(eq.P0a, a)
    Q0b = pshift(eq.P0b, a)
    st.Q2h = [acb(Q2[j] * h ** j) for j in range(len(Q2))]
    st.Q1h = [acb(Q1[j] * h ** (j + 1)) for j in range(len(Q1))]
    st.Q0ah = [acb(Q0a[j] * h ** (j + 2)) for j in range(len(Q0a))]
    st.Q0bh = [acb(Q0b[j] * h ** (j + 2)) for j in range(len(Q0b))]


def taylor_step(st, w2, psi, dpsi):
    """truncated Taylor map over one step (st.N terms); works for acb and acb_series"""
    h = st.h
    Q2h, Q1h, Q0ah, Q0bh = st.Q2h, st.Q1h, st.Q0ah, st.Q0bh
    B = [psi, dpsi * h]
    S = psi + B[1]
    Sd = B[1]
    inv0 = 1 / Q2h[0]
    n2, n1 = len(Q2h), len(Q1h)
    n0 = max(len(Q0ah), len(Q0bh))
    if len(Q0ah) < n0:
        Q0ah = Q0ah + [acb(0)] * (n0 - len(Q0ah))
    if len(Q0bh) < n0:
        Q0bh = Q0bh + [acb(0)] * (n0 - len(Q0bh))
    for k in range(0, st.N - 1):
        na = None
        for j in range(1, n2):
            idx = k - j + 2
            if idx < 0:
                break
            if idx >= 2:
                t = B[idx] * (Q2h[j] * (idx * (idx - 1)))
                na = t if na is None else na + t
        for j in range(0, n1):
            idx = k - j + 1
            if idx < 0:
                break
            if idx >= 1:
                t = B[idx] * (Q1h[j] * idx)
                na = t if na is None else na + t
        nb = None
        for j in range(0, n0):
            idx = k - j
            if idx < 0:
                break
            if not Q0ah[j].is_zero():
                t = B[idx] * Q0ah[j]
                na = t if na is None else na + t
            if not Q0bh[j].is_zero():
                t = B[idx] * Q0bh[j]
                nb = t if nb is None else nb + t
        if nb is None:
            num = na
        elif na is None:
            num = w2 * nb
        else:
            num = na + w2 * nb
        Bn = num * (-inv0 / ((k + 2) * (k + 1)))
        B.append(Bn)
        S = S + Bn
        Sd = Sd + Bn * (k + 2)
    return S, Sd / h


# ---------------------------------------------------------------- per-step analytic bounds
def step_disk_bounds(eq, st, wmax):
    """Cauchy data: (rho1, sigma_c, ||A||_F sup on the disk |r - a| <= rho1)"""
    rho1 = KAPPA * st.h
    rmin = st.a - rho1
    rmax = st.a + rho1
    dmin = st.a - 2 - rho1
    P, Q = eq.pq_sup(rmin, rmax, dmin, wmax)
    sig_c = Q.sqrt()
    An = (2 * Q + P * P).sqrt()
    return rho1, sig_c, An


def step_tail_factors(eq, st, wmax):
    """relative truncation of the step: |delta psi| <= tS*|Y|_{sig_c}, |delta psi'| <= tD*|Y|_{sig_c}"""
    rho1, sig_c, An = step_disk_bounds(eq, st, wmax)
    M = (rho1 * An).exp()
    kap = arb(KAPPA)
    geo = 1 / (1 - 1 / kap)
    tS = M * kap ** (-(st.N + 1)) * geo
    tD = sig_c * M * kap ** (-st.N) * geo
    return arb(tS.upper()), arb(tD.upper()), sig_c


def choose_terms(eq, st, wmax, tol_rel):
    rho1, sig_c, An = step_disk_bounds(eq, st, wmax)
    lnM = float((rho1 * An).upper())
    # need e^lnM * 4^-(N+1) * (1 + sig_c) <= tol_rel  (relative)
    extra = math.log(1 + float(sig_c.upper())) + math.log(4.0 / 3.0)
    N = int(math.ceil((lnM + extra - math.log(tol_rel)) / math.log(KAPPA))) + 1
    st.N = max(N, 8)


def segment_rate(eq, st, w0, dw2, sigma2, backward=False):
    """log-norm growth rate bound on the real segment [a, a+h] for w with |w^2 - w0^2| <= dw2:
    forward (increasing r): rate <= sup |sigma2 - q|/(2 sigma), q = w^2 g1 - g2 (the -p diagonal only helps);
    backward: rate <= sup |sigma2 - q|/(2 sigma) + sup p,  p = 2/(r(r-2)).  Returns (rate, sigma)."""
    sig = sigma2.sqrt()
    rate = arb(0)
    nsub = 4
    for i in range(nsub):
        lo = st.a + st.h * i / nsub
        hi = st.a + st.h * (i + 1) / nsub
        r = arb((lo + hi) / 2, ((hi - lo) / 2).upper())
        g1, g2 = eq.g1g2(r)
        dev = abs(sigma2 - w0 * w0 * g1 + g2) + dw2 * abs(g1)
        rr = dev / (2 * sig)
        if backward:
            rr = rr + 2 / (lo * (lo - 2))
        rate = rate.max(arb(rr.upper())) if i else arb(rr.upper())
    return rate, sig


def sigma2_choice(eq, st, w0):
    am = st.a + st.h / 2
    g1, g2 = eq.g1g2(am)
    v = abs(w0 * w0 * g1 - g2)
    v = arb(v.mid())
    if not v > 0:
        v = arb(1e-6)
    return v


def seg_sigma_rate(eq, st, w0, dw2, backward=False):
    """choose the basis scale sigma for the segment (several candidates, smallest certified rate wins).
    Any sigma > 0 gives a valid bound; the choice only affects tightness."""
    am = st.a + st.h / 2
    g1, g2 = eq.g1g2(am)
    qm = abs(w0 * w0 * g1 - g2).mid()
    spread = dw2 * g1.mid() + abs(w0 * w0).mid() * 0
    # sup |q| over the segment (cheap enclosure)
    r = arb((st.a + st.h / 2), (st.h / 2).upper())
    G1, G2 = eq.g1g2(r)
    qmax = (abs(w0 * w0 * G1 - G2) + dw2 * abs(G1)).upper()
    cands = [arb(qm), arb(qmax), arb(qm) + arb(spread), (arb(qm) * arb(qmax)).sqrt(), arb(qmax) / 2]
    best = None
    for s2 in cands:
        if not s2 > 0:
            continue
        rate, sig = segment_rate(eq, st, w0, dw2, s2, backward)
        if best is None or rate < best[0]:
            best = (rate, sig)
    if best is None:
        best = segment_rate(eq, st, w0, dw2, arb(1e-6), backward)
    return best


# ---------------------------------------------------------------- (3) far field
def far_coeffs(eq, w, M):
    """c_0..c_{M+1} of h_+ = sum c_m r^-m for u_+ = e^{i w r*} h_+ (for u_- pass -w).  w: acb or series."""
    I = acb(0, 1)
    d1 = eq.d1
    a2, A1a, A1c, a0 = eq.a2, eq.A1a, eq.A1c, eq.a0
    top = A1c[d1]
    iw = I * w
    inv_iw = 1 / iw
    one = acb(1) if not _is_series(w) else acb_series([1])
    c = [one]

    def coefXY(mp, p):
        X = 0
        Y = 0
        j = p + mp + 2
        if 0 <= j < len(a2):
            X += a2[j] * mp * (mp + 1)
        j = p + mp + 1
        if 0 <= j < len(A1a):
            X += -mp * A1a[j]
        if 0 <= j < len(A1c):
            Y += -mp * A1c[j]
        j = p + mp
        if 0 <= j < len(a0):
            X += a0[j]
        return X, Y

    for m in range(1, M + 2):
        p = d1 - 1 - m
        sX = None; sY = None
        for mp in range(0, m):
            X, Y = coefXY(mp, p)
            if X:
                t = c[mp] * X
                sX = t if sX is None else sX + t
            if Y:
                t = c[mp] * Y
                sY = t if sY is None else sY + t
        val = None
        if sX is not None:
            val = sX * inv_iw
        if sY is not None:
            val = sY if val is None else val + sY
        if val is None:
            val = one * 0
        c.append(val * (acb(1) / (m * top)))
    return c, coefXY


def far_residual_bound(eq, c, coefXY, M, w, R):
    """Volterra bound (real w, real axis) for e = h - h_M at R.  c: coefficient balls (point or uniform w-ball)."""
    I = acb(0, 1)
    d1 = eq.d1
    iw = I * w
    pmin = -(M + 3)
    rho_hat = {}                       # power k of t^-k  ->  |coefficient| bound (divided by lead D)
    degD = len(eq.D) - 1
    for p in range(pmin - 2, d1 - 1 - M):
        s = acb(0)
        used = False
        for mp in range(0, M + 1):
            X, Y = coefXY(mp, p)
            if X or Y:
                s += c[mp] * (X + iw * Y)
                used = True
        if used:
            k = 3 + degD - p
            rho_hat[k] = ub(s) / eq.Dlead()
    alpha = M + 1
    Rr = arb(R)
    Cf = 1 / (1 - 2 / Rr)
    KU = eq.KU(Rr)
    q = Cf * (2 / ((alpha + 1) * Rr) + Cf * KU / (alpha * (alpha - 1)))
    if not q < 1:
        raise Refuse("far field: Volterra contraction q = %s >= 1" % q)
    F = arb(0)
    for k, v in rho_hat.items():
        if k < alpha + 1:
            raise Refuse("far field: residual power %d too low" % k)
        F += v * Rr ** (alpha + 1 - k) / (k - 1)
    F = Cf * F
    gam = F / (1 - q)
    e0 = gam * Rr ** (1 - alpha) / (alpha - 1)
    e1 = gam * Rr ** (-alpha)
    return arb(e0.upper()), arb(e1.upper())


def rstar(R):
    R = arb(R)
    return R + 2 * (R / 2 - 1).log()


def far_solution(eq, w, M, R, sign=+1, point_err=None):
    """u, u' at R for u_sign; point_err = (e0, e1) adds the certified remainder as radii (point mode, real w)"""
    I = acb(0, 1)
    ws = w if sign > 0 else -w
    c, coefXY = far_coeffs(eq, ws, M)
    Rr = arb(R)
    Rinv = 1 / Rr
    h = None; hp = None
    pw = arb(1)
    for m in range(0, M + 1):
        t = c[m] * pw
        h = t if h is None else h + t
        if m:
            tp = c[m] * (-m * pw * Rinv)
            hp = tp if hp is None else hp + tp
        pw = pw * Rinv
    if point_err is not None:
        e0, e1 = point_err
        h = h + cball(e0)
        hp = hp + cball(e1)
    f = 1 - 2 * Rinv
    E = _exp(I * ws * rstar(Rr))
    u = E * h
    du = E * (I * ws * h / f + hp)
    return u, du, c, coefXY


# ---------------------------------------------------------------- configuration of one solve
class Plan:
    """everything fixed for a w-set: x0, N_h, steps (with N), R, M"""
    pass


def make_plan(eq, wlo, whi, wmax_disk=None, x0=0.25, tol_rel=1e-24, wR=25.0, R_min=12.0, M=None, ch=0.6,
              wmin_disk=None):
    """plan valid for real w in [wlo, whi] (and, for jets, |w| <= wmax_disk, |w| >= wmin_disk)."""
    P = Plan()
    P.eq = eq
    P.x0 = arb(x0)
    wmax = wmax_disk if wmax_disk is not None else whi
    P.wmax = wmax
    P.wlo, P.whi = wlo, whi
    R = max(R_min, wR / float(wlo), 1.3 * math.sqrt(eq.L + 2) / float(wlo))
    steps, Rn = plan_steps(eq, x0, R, float(wmax), ch=ch)
    P.Rn = Rn
    P.R = arb(Rn) / DYADIC
    with precision():
        for st in steps:
            prepare_step(eq, st)
            choose_terms(eq, st, arb(wmax), tol_rel)
    P.steps = steps
    # horizon series length: terms decay like (x0/2)^n; majorant needs a margin
    P.Nh = int(math.ceil((-math.log(tol_rel) + 10) / math.log(2.0 / x0))) + 12
    if M is None:
        # optimal truncation of the asymptotic series: about 2 w R terms (capped)
        M = 2 * float(wlo) * float(P.R) * 0.85
        if wmin_disk is not None:
            # keep the truncated series tame on the whole disk (|w| >= wmin_disk) - this bounds B
            M = min(M, 2 * float(wmin_disk) * float(P.R) * 0.95)
        M = max(int(min(M, 150)), 8)
    P.M = M
    return P


# ---------------------------------------------------------------- (4) point mode: certified A_in, A_out
def point_solve(eq, w, P=None, want_out=True, prec_bits=PREC, start_scale=None):
    """certified enclosures of A_in(w), A_out(w), Gamma(w) for real w (arb, exact or ball)."""
    with precision(prec_bits):
        w = arb(w)
        if P is None:
            P = make_plan(eq, arb(w.lower()), arb(w.upper()))
        x0 = P.x0
        wa = acb(w)
        wmax = arb(abs(w).upper())
        # horizon tail
        a, rho = frob_coeffs(eq, wa, P.Nh)
        J = len(eq.p2) - 1
        last = [ub(a[k]) for k in range(P.Nh - J + 1, P.Nh + 1)]
        tS, tD = frob_tail(eq, wmax, P.Nh, last, x0)
        psi, dpsi, _ = horizon_start(eq, wa, x0, P.Nh, point_tail=(tS, tD))
        if start_scale is not None:            # teeth only: a mis-normalised horizon start must break the flux check
            psi = psi * start_scale
            dpsi = dpsi * start_scale
        w2 = wa * wa
        # norm-based error propagation (no wrapping): state = exact midpoints, E = error bound in the 2-norm of
        # (psi, psi'/sigma_i); the error is carried by the EXACT step map, whose growth is exp(h * rate_i)
        w0 = arb(w.mid())
        dw2 = arb(abs(w * w - w0 * w0).upper())
        sig_prev = None
        E = None
        for st in P.steps:
            rate, sig = seg_sigma_rate(eq, st, w0, dw2)
            if E is None:
                E = (crad(psi) ** 2 + (crad(dpsi) / sig) ** 2).sqrt()
            else:
                E = E * (sig_prev / sig).max(arb(1))
            psi_m, dpsi_m = psi.mid(), dpsi.mid()
            fS, fD, sig_c = step_tail_factors(eq, st, wmax)
            Ymag = (ub(psi_m) ** 2 + (ub(dpsi_m) / sig_c) ** 2).sqrt()
            psi, dpsi = taylor_step(st, w2, psi_m, dpsi_m)
            loc = ((crad(psi) + fS * Ymag) ** 2 + ((crad(dpsi) + fD * Ymag) / sig) ** 2).sqrt()
            E = arb((E * (st.h * rate).exp() + loc).upper())
            sig_prev = sig
        psi = psi.mid() + cball(E)
        dpsi = dpsi.mid() + cball(E * sig_prev)
        R = P.R
        # far field remainders (real w)
        up, dup, c, cxy = far_solution(eq, wa, P.M, R, +1)
        e0, e1 = far_residual_bound(eq, c, cxy, P.M, wa, R)
        up, dup, c, cxy = far_solution(eq, wa, P.M, R, +1, point_err=(e0, e1))
        f = 1 - 2 / R
        I = acb(0, 1)
        Ain = f * (psi * dup - dpsi * up) / (2 * I * wa)
        out = {"A_in": Ain, "R": R, "steps": len(P.steps), "M": P.M}
        if want_out:
            um, dum, cm, cxym = far_solution(eq, wa, P.M, R, -1)
            e0m, e1m = far_residual_bound(eq, cm, cxym, P.M, -wa, R)
            um, dum, cm, cxym = far_solution(eq, wa, P.M, R, -1, point_err=(e0m, e1m))
            Aout = f * (psi * dum - dpsi * um) / (-2 * I * wa)
            out["A_out"] = Aout
            out["flux_minus_1"] = abs(Ain) ** 2 - abs(Aout) ** 2 - 1
        G = 1 / abs(Ain) ** 2
        # |A_in| >= 1 is a theorem (flux); intersect for a tighter upper bound of Gamma
        out["Gamma"] = G
        return out


# ---------------------------------------------------------------- jets and uniform bounds (Taylor model in w)
def jet_solve(eq, P, w0, length=JET_LEN, prec_bits=PREC, rel_target=1e-40):
    """Taylor coefficients (acb balls) of the approximant A_M(w0 + eps), eps^0..eps^(length-1).
    Rounding radii grow along the path (cancellation inside the Taylor recurrences at large |w|); the working
    precision is doubled (and the step data recomputed at that precision) until |A_0| has relative radius
    <= rel_target.  This only changes rounding, never the approximant."""
    prec = prec_bits
    for _ in range(4):
        co = _jet_solve_once(eq, P, w0, length, prec)
        with precision(prec):
            r0 = crad(co[0])
            a0 = abs(co[0]).lower()
            if a0 > 0 and r0 < a0 * rel_target:
                P.jet_prec = prec
                return co
        prec *= 2
    raise Refuse("jet_solve: rounding radius not controlled up to %d bits" % prec)


def _jet_solve_once(eq, P, w0, length, prec_bits):
    require_cap(length)
    with precision(prec_bits):
        for st in P.steps:
            prepare_step(eq, st)
        w = acb_series([acb(w0), 1])
        psi, dpsi, _ = horizon_start(eq, w, P.x0, P.Nh)
        w2 = w * w
        for st in P.steps:
            psi, dpsi = taylor_step(st, w2, psi, dpsi)
        up, dup, _, _ = far_solution(eq, w, P.M, P.R, +1)
        R = P.R
        f = 1 - 2 / R
        I = acb(0, 1)
        A = (psi * dup - dpsi * up) * f / (2 * I * w)
        co = A.coeffs()
        co = co + [acb(0)] * (length - len(co))
        return co[:length]


def _forward_bounds(eq, P, w0, rw, disk, frob_mag):
    """upper bounds of |Y_N| (2-norm, sigma_i basis) at each step start and at R, uniformly over the w-set.
    frob_mag = (|psi_N(x0)|, |psi_N'(x0)|) bounds.  Returns (list of (|Y| at start of step i, sigma_i), Yend, sig_end)."""
    w0 = arb(w0)
    rw = arb(rw)
    wmax = w0 + rw
    dw2 = rw * (2 * w0 + rw)
    out = []
    ps, dps = frob_mag
    rates = [seg_sigma_rate(eq, st, w0, dw2) for st in P.steps]
    sig = rates[0][1]
    Y = (ps ** 2 + (dps / sig) ** 2).sqrt()
    prev_sig = sig
    for i, st in enumerate(P.steps):
        rate, sig = rates[i]
        if i:
            Y = Y * (prev_sig / sig).max(arb(1))
        out.append((arb(Y.upper()), sig))
        fS, fD, sig_c = step_tail_factors(eq, st, wmax)
        # |Y|_{sig_c} <= max(1, sig/sig_c) |Y|_sig ; truncation adds (fS, fD/sig) * that
        conv = (sig / sig_c).max(arb(1))
        trunc = ((fS * conv) ** 2 + (fD * conv / sig) ** 2).sqrt()
        Y = Y * ((st.h * rate).exp() + trunc)
        prev_sig = sig
    return out, arb(Y.upper()), prev_sig


def _backward_U(eq, P, w0, rw, sig_end, Uend):
    """upper bounds of |Y_u| (exact outgoing solution, 2-norm in sigma_i basis) at the END of each step, real w-set"""
    w0 = arb(w0)
    rw = arb(rw)
    dw2 = rw * (2 * w0 + rw)
    n = len(P.steps)
    res = [None] * n
    Y = Uend
    sig_next = sig_end
    for i in range(n - 1, -1, -1):
        st = P.steps[i]
        rate, sig = seg_sigma_rate(eq, st, w0, dw2, backward=True)
        # convert from next basis (sig_next) to this step's basis at its end point
        Y = Y * (sig_next / sig).max(arb(1)) if i < n - 1 else Y * (sig_end / sig).max(arb(1))
        res[i] = (arb(Y.upper()), sig)      # at end of step i (r_{i+1}) in basis sig
        Y = Y * (st.h * rate).exp()          # now at start of step i
        sig_next = sig
    return res, arb(Y.upper()), sig_next


def frob_majorant(eq, wmax, N, im_max, rew_min):
    """A_n >= |a_n| for all w with |w| <= wmax, |Im w| <= im_max, Re w >= rew_min, via the absolute recurrence
    A_n = sum_j b_j(n) A_{n-j},  b_j(n) = (|s|^2|p2_j| + |s|(|p2_j|+|p1_j|) + |p0a_j| + wmax^2|p0b_j|) / (|p2_0| n m_n),
    |s| <= n-j+2wmax,  m_n <= |n - 4 i w| = sqrt((n + 4 Im w)^2 + 16 (Re w)^2)"""
    p2, p1, p0a, p0b = eq.p2, eq.p1, eq.p0a, eq.p0b
    J = len(p2) - 1
    A = [arb(1)]
    for n in range(1, N + 1):
        t = (n - 4 * im_max).max(arb(0))
        m_n = (t * t + 16 * rew_min * rew_min).sqrt()
        den = abs(arb(p2[0])) * n * m_n
        if not den > 0:
            raise Refuse("frob_majorant: |n - 4 i w| not bounded below")
        v = arb(0)
        for j in range(1, J + 1):
            if n - j < 0:
                break
            s = n - j + 2 * wmax
            num = (s * s * abs(arb(p2[j])) + s * (abs(arb(p2[j])) + abs(arb(p1[j])))
                   + abs(arb(p0a[j])) + wmax * wmax * abs(arb(p0b[j])))
            v += num * A[n - j]
        A.append(arb((v / den).upper()))
    return A


def frob_uniform(eq, P, wball, wmax, im_max, rew_min):
    """bounds |psi_N(x0)|, |psi_N'(x0)| (truncated) and Frobenius tails (tS, tD) uniform over the w-ball"""
    a, rho = frob_coeffs(eq, wball, P.Nh)
    try:
        Amaj = frob_majorant(eq, wmax, P.Nh, arb(im_max), arb(rew_min))
    except Refuse:
        Amaj = None
    x0 = P.x0
    S = arb(0); Sd = arb(0)
    xp = arb(1)
    rho_abs = 2 * wmax
    for n in range(P.Nh + 1):
        an = ub(a[n])
        if Amaj is not None:
            an = an.min(Amaj[n])
        a[n] = acb(arb(0, an))            # keep the bound for the tail start below
        S += an * xp
        Sd += (n + rho_abs) * an * xp
        xp = xp * x0
    J = len(eq.p2) - 1
    last = [ub(a[k]) for k in range(P.Nh - J + 1, P.Nh + 1)]
    tS, tD = frob_tail(eq, wmax, P.Nh, last, x0)
    xr = (2 * im_max * abs(x0.log())).exp()             # |x0^rho| = exp(2 Im(w) ln x0)
    return xr * S, xr * Sd / x0, xr * tS, xr * tD / x0


def uniform_bounds(eq, P, w0, delta, rho_w, prec_bits=PREC):
    """B >= sup_{|w-w0|=rho_w} |A_M(w)|  and  eta >= sup_{w real, |w-w0|<=delta} |A(w) - A_M(w)|"""
    with precision(prec_bits):
        w0 = arb(w0)
        delta = arb(delta)
        rho_w = arb(rho_w)
        if not rho_w < w0:
            raise Refuse("disk reaches w = 0")
        R = P.R
        f = 1 - 2 / R
        rs = rstar(R)
        I = acb(0, 1)
        # ---- B on the complex disk
        wdisk = acb(arb(w0, rho_w.upper()), arb(0, rho_w.upper()))
        wmaxd = w0 + rho_w
        psN, dpsN, _, _ = frob_uniform(eq, P, wdisk, wmaxd, rho_w, w0 - rho_w)
        _, Yend, sig_end = _forward_bounds(eq, P, w0, rho_w, True, (psN, dpsN))
        cdisk, _ = far_coeffs(eq, wdisk, P.M)
        hM = arb(0); hMp = arb(0)
        for m in range(P.M + 1):
            hM += ub(cdisk[m]) * R ** (-m)
            if m:
                hMp += m * ub(cdisk[m]) * R ** (-m - 1)
        Eb = (rho_w * rs).exp()
        uM = Eb * hM
        duM = Eb * (wmaxd * hM / f + hMp)
        psR = Yend
        dpsR = Yend * sig_end
        B = f * (psR * duM + dpsR * uM) / (2 * (w0 - rho_w))
        # ---- eta on the real panel
        wseg = acb(arb(w0, delta.upper()))
        wmaxs = w0 + delta
        wmin = w0 - delta
        psN, dpsN, tS0, tD0 = frob_uniform(eq, P, wseg, wmaxs, arb(0), w0 - delta)
        fwd, Yend_s, sig_end_s = _forward_bounds(eq, P, w0, delta, False, (psN + tS0, dpsN + tD0))
        cseg, cxy = far_coeffs(eq, wseg, P.M)
        e0, e1 = far_residual_bound(eq, cseg, cxy, P.M, wseg, R)
        hM = arb(0); hMp = arb(0)
        for m in range(P.M + 1):
            hM += ub(cseg[m]) * R ** (-m)
            if m:
                hMp += m * ub(cseg[m]) * R ** (-m - 1)
        uabs = hM + e0
        duabs = wmaxs * uabs / f + hMp + e1
        Uend = (uabs ** 2 + (duabs / sig_end_s) ** 2).sqrt()
        bwd, Ustart, sig0 = _backward_U(eq, P, w0, delta, sig_end_s, Uend)
        eta = arb(0)
        # Frobenius tail at r0 = 2 + x0: W(delta, u) with |u| <= Ustart, |u'| <= sig0 Ustart
        f0 = P.x0 / (2 + P.x0)
        eta += f0 * (tS0 * sig0 * Ustart + tD0 * Ustart)
        for i, st in enumerate(P.steps):
            Yi, sig_i = fwd[i]
            fS, fD, sig_c = step_tail_factors(eq, st, wmaxs)
            conv = (sig_i / sig_c).max(arb(1))
            dps = fS * conv * Yi
            ddps = fD * conv * Yi
            Ui, sig_u = bwd[i]
            r1 = st.a + st.h
            fi = 1 - 2 / r1
            eta += fi * (dps * sig_u * Ui + ddps * Ui)
        # far-field remainder
        psR = Yend_s
        dpsR = Yend_s * sig_end_s
        eta += f * (psR * (wmaxs * e0 / f + e1) + dpsR * e0)
        eta = eta / (2 * wmin)
        return arb(B.upper()), arb(eta.upper())
