"""
python-flint (acb ball arithmetic) port of mst.py, same formulas, same source locators
(Sasaki & Tagoshi LRR 2003, livrev4.texin; see mst.py header).
Ball arithmetic bounds the floating-point rounding only; truncation of the continued fractions and
of the f_n series is controlled separately (cutoff 10^-(digits+8), doubled-depth check).

nu selection: all genuine roots of eq:nudefeq2 form one class {nu+k, -nu-1+k}; the class invariant
c = cos(2 pi nu) is smooth in omega, so it is tracked (polynomial extrapolation) and each node's nu
is polished from the arccos of the predicted c. Spurious exact (half-)integer zeros are deflated.
"""
from flint import acb, arb, ctx
import cmath, math

M = 1
I = acb(0, 1)
SPUR_TOL = [1e-25]


def setprec(digits):
    ctx.dps = digits
    SPUR_TOL[0] = 10.0 ** (-(digits - 12))


def _abg(n, nu, s, eps, lam):
    nn = nu + n
    ie = I * eps
    al = ie * (nn + 1 + s + ie) * (nn + 1 + s - ie) * (nn + 1 + ie) / ((nn + 1) * (2 * nn + 3))
    be = -lam - s * (s + 1) + nn * (nn + 1) + 2 * eps * eps + eps * eps * (s * s + eps * eps) / (nn * (nn + 1))
    ga = -ie * (nn - s + ie) * (nn - s - ie) * (nn - ie) / (nn * (2 * nn - 1))
    return al, be, ga


def cf_depth(eps, digits):
    """smallest N with (eps/2)^(2N)/(N!)^2 < 10^-(digits+10), plus margin (CF tail ~ prod (eps/2n)^2)."""
    e = max(float(eps), 1e-3)
    lg = 0.0
    N = 1
    while True:
        lg += 2 * math.log10(e / (2 * N))
        if lg < -(digits + 10) and N > 2 * e:
            return N + 8
        N += 1


def nu_function(nu, s, eps, lam, depth):
    R = acb(0)
    for n in range(1 + depth, 0, -1):
        al, be, ga = _abg(n, nu, s, eps, lam)
        R = -ga / (be + al * R)
    L = acb(0)
    for n in range(-1 - depth, 0):
        al, be, ga = _abg(n, nu, s, eps, lam)
        L = -al / (be + ga * L)
    al, be, ga = _abg(0, nu, s, eps, lam)
    return be + al * R + ga * L


def _c(z):
    m = z.mid()
    return complex(float(m.real.mid()), float(m.imag.mid()))


def nearest_half(z):
    return round(2 * z.real) / 2


SPUR_TOL = [1e-25]


def is_spurious(z):
    """spurious zeros sit EXACTLY on the lattice (secant converges to them to working precision)."""
    return abs(z.imag) < SPUR_TOL[0] and abs(z.real - nearest_half(z)) < SPUR_TOL[0]


def secant(F, x0, digits, maxit=80):
    x0 = acb(x0)
    x1 = x0 + acb(1e-10, 3e-11) * (1 + abs(_c(x0)))
    f0, f1 = F(x0), F(x1)
    tol = 10.0 ** (-(digits - 4))
    for _ in range(maxit):
        d = f1 - f0
        if _c(d) == 0:
            break
        x2 = (x1 - f1 * (x1 - x0) / d).mid()
        x0, f0 = x1, f1
        x1 = x2
        f1 = F(x1)
        if abs(_c(x1 - x0)) < tol * (1 + abs(_c(x1))):
            break
    return x1


def solve_genuine(s, l, eps, guess, digits):
    lam = l * (l + 1) - s * (s + 1)
    d = cf_depth(eps, digits)
    h = None
    for attempt in range(4):
        hh = h
        F = (lambda nu: nu_function(nu, s, eps, lam, d)) if hh is None else \
            (lambda nu: nu_function(nu, s, eps, lam, d) / (nu - hh))
        try:
            nu = secant(F, guess, digits)
        except Exception:
            return None, None
        z = _c(nu)
        if is_spurious(z):
            h = nearest_half(z)
            continue
        res = abs(_c(nu_function(nu, s, eps, lam, 2 * d)))
        scale = 1 + abs(z) ** 2
        if hh is not None:
            res /= abs(z - hh)
        if res / scale < 10.0 ** (-(digits - 10)):
            return nu, res / scale
        return None, res / scale
    return None, None


def nu_lowfreq(s, l, eps):
    c = -2.0
    if s != 0:
        c -= s * s / (l * (l + 1))
    c += ((l + 1) ** 2 - s * s) ** 2 / ((2 * l + 1) * (2 * l + 2) * (2 * l + 3))
    if l * l != s * s:
        c -= (l * l - s * s) ** 2 / ((2 * l - 1) * 2 * l * (2 * l + 1))
    return l + c / (2 * l + 1) * eps ** 2


def _g(nu, s, eps, lam, d):
    return nu_function(nu, s, eps, lam, d)


def solve_u(s, l, eps, h, u0, digits):
    """solve for u = (nu - h)^2 with G(u) = g(h + sqrt u) g(h - sqrt u) (even in sqrt u -> analytic in u,
    regular through the collision of the pair h +- sqrt u). Spurious zero / pole of g at the lattice
    point h is removed by a factor u^(-k)."""
    lam = l * (l + 1) - s * (s + 1)
    d = cf_depth(eps, digits)
    hh = acb(h)
    # order of g at h: probe at tiny offsets
    t1, t2 = acb(0, 1e-12), acb(0, 1e-14)
    try:
        g1, g2 = abs(_c(_g(hh + t1, s, eps, lam, d))), abs(_c(_g(hh + t2, s, eps, lam, d)))
        ratio = g1 / g2 if g2 != 0 else 1.0
    except Exception:
        ratio = 1.0
    k = 0
    if 30 < ratio < 300:
        k = 1          # simple zero at h
    elif 1 / 300 < ratio < 1 / 30:
        k = -1         # simple pole at h

    def G(u):
        r = u.sqrt()
        v = _g(hh + r, s, eps, lam, d) * _g(hh - r, s, eps, lam, d)
        if k == 1:
            v = v / u
        elif k == -1:
            v = v * u
        return v
    try:
        u = secant(G, acb(u0) + acb(0, 1e-9), digits)
    except Exception:
        return None
    return u


def nu_from_u(u, h, prev):
    r = u.sqrt()
    c1, c2 = acb(h) + r, acb(h) - r
    z1, z2 = _c(c1), _c(c2)
    if abs(z1.imag) > 1e-12 or abs(z2.imag) > 1e-12:     # complex pair: Im nu >= 0 representative
        return c1 if z1.imag >= 0 else c2
    return c1 if abs(z1 - prev) <= abs(z2 - prev) else c2


def residual(nu, s, l, eps, digits):
    lam = l * (l + 1) - s * (s + 1)
    d = cf_depth(eps, digits)
    z = _c(nu)
    return abs(_c(nu_function(nu, s, eps, lam, 2 * d))) / (1 + abs(z) ** 2)


def track_nu(s, l, omegas, digits, w_start=0.01, verbose=False):
    """follow the physical root along ascending omegas (arb or str). Tracked variable u = (nu - h)^2 with
    h the nearest (half-)integer to Re nu; u is real on both sides of every collision."""
    ws = [arb(w) for w in omegas]
    w0 = min(w_start, float(ws[0].mid()) / 2)
    nu, res = solve_genuine(s, l, 2 * M * arb(w0), nu_lowfreq(s, l, 2 * M * w0), digits)
    if nu is None or abs(_c(nu) - l) > 0.3:
        raise RuntimeError('start failed s=%d l=%d' % (s, l))
    hist = [(w0, _c(nu))]
    out = []
    tolres = 10.0 ** (-(digits - 10))
    for wa_ in ws:
        wf = float(wa_.mid())
        sub = [wf]
        while sub:
            wn = sub[0]
            warb = wa_ if wn == wf else arb(wn)
            zp = hist[-1][1]
            h = nearest_half(zp)
            us = [((z - h) ** 2).real for (_, z) in hist[-3:]]
            ws_ = [x for (x, _) in hist[-3:]]
            if len(us) == 3:
                (a, b, c_) = ws_
                up = (us[0] * (wn - b) * (wn - c_) / ((a - b) * (a - c_)) + us[1] * (wn - a) * (wn - c_) / ((b - a) * (b - c_))
                      + us[2] * (wn - a) * (wn - b) / ((c_ - a) * (c_ - b)))
            elif len(us) == 2:
                up = us[1] + (us[1] - us[0]) * (wn - ws_[1]) / (ws_[1] - ws_[0])
            else:
                up = us[-1]
            eps = 2 * M * warb
            u = solve_u(s, l, eps, h, up, digits)
            ok = False
            if u is not None:
                nu = nu_from_u(u, h, zp)
                z = _c(nu)
                try:
                    res = residual(nu, s, l, eps, digits)
                except Exception:
                    res = 1.0
                uz = _c(u)
                du_pred = abs(up - us[-1])
                ok = (res < tolres and not is_spurious(z) and
                      abs(uz - up) < 0.25 * du_pred + 0.02 * (1 + abs(up)) and abs(z - zp) < 0.3)
            if verbose:
                print('  w=%.6f h=%s up=%.4g u=%s ok=%s' % (wn, h, up, _c(u) if u is not None else None, ok), flush=True)
            if ok:
                hist.append((wn, z))
                if len(hist) > 6:
                    hist.pop(0)
                sub.pop(0)
                # store high-precision nu for the node
                if not sub:
                    out.append(nu)
            else:
                prev = hist[-1][0]
                if wn - prev < 1e-7:
                    raise RuntimeError('tracking failed s=%d l=%d w=%g' % (s, l, wn))
                sub.insert(0, 0.5 * (prev + wn))
    return out


def coeffs_f(nu, s, eps, lam, tolexp, digits):
    small = 10.0 ** (-tolexp)
    nmax = cf_depth(eps, digits)
    while True:
        depth = nmax + 20
        R = acb(0)
        Rs = {}
        for n in range(nmax + depth, 0, -1):
            al, be, ga = _abg(n, nu, s, eps, lam)
            R = -ga / (be + al * R)
            if n <= nmax:
                Rs[n] = R
        L = acb(0)
        Ls = {}
        for n in range(-nmax - depth, 0):
            al, be, ga = _abg(n, nu, s, eps, lam)
            L = -al / (be + ga * L)
            if n >= -nmax:
                Ls[n] = L
        f = {0: acb(1)}
        fmax = 1.0
        np_ = nm_ = None
        for n in range(1, nmax + 1):
            f[n] = f[n - 1] * Rs[n]
            a = abs(_c(f[n]))
            fmax = max(fmax, a)
            if a < small * fmax and n > 4:
                np_ = n
                break
        for n in range(-1, -nmax - 1, -1):
            f[n] = f[n + 1] * Ls[n]
            a = abs(_c(f[n]))
            fmax = max(fmax, a)
            if a < small * fmax and n < -4:
                nm_ = n
                break
        if np_ is not None and nm_ is not None:
            return f, nm_, np_
        nmax *= 2


def _rf(x, n):
    """Pochhammer (x)_n for small integer n (positive or negative)."""
    p = acb(1)
    if n >= 0:
        for k in range(n):
            p = p * (x + k)
    else:
        for k in range(1, -n + 1):
            p = p / (x - k)
    return p


def K_nu(nu, f, nlo, nhi, s, eps, r=0):
    G = lambda z: acb(z).gamma()
    ie = I * eps
    pref = ((ie).exp() * acb(2 * eps) ** (s - nu - r) * acb(2) ** (-s) * I ** r
            * G(1 - s - 2 * ie) * G(r + 2 * nu + 2)
            / (G(r + nu + 1 - s + ie) * G(r + nu + 1 + ie) * G(r + nu + 1 + s + ie)))
    T = ((-1) ** r * G(2 * r + 2 * nu + 1) * G(r + nu + 1 + s + ie) / G(r + nu + 1 - s - ie)
         * G(r + nu + 1 + ie) / G(r + nu + 1 - ie))
    S1 = acb(0)
    for n in range(r, nhi + 1):
        S1 += T * f[n]
        T = (T * (-(n + r + 2 * nu + 1)) / (n + 1 - r) * (n + nu + 1 + s + ie) / (n + nu + 1 - s - ie)
             * (n + nu + 1 + ie) / (n + nu + 1 - ie))
    a = nu + 1 + s - ie
    b = nu + 1 - s + ie
    c = r + 2 * nu + 2
    U = (-1) ** r * _rf(a, r) / (_rf(c, r) * _rf(b, r))
    S2 = acb(0)
    for n in range(r, nlo - 1, -1):
        S2 += U * f[n]
        U = U * (-(c + n - 1)) * (b + n - 1) / ((r - n + 1) * (a + n - 1))
    return pref * S1 / S2


def amplitudes(s, l, omega, nu, digits, tolexp=None, r=0):
    omega = arb(omega)
    eps = 2 * M * omega
    lam = l * (l + 1) - s * (s + 1)
    if tolexp is None:
        tolexp = digits + 8
    nu = acb(nu)
    pi = arb.pi()
    f, nlo, nhi = coeffs_f(nu, s, eps, lam, tolexp, digits)
    fneg = {-n: v for n, v in f.items()}
    Kp = K_nu(nu, f, nlo, nhi, s, eps, r)
    Km = K_nu(-nu - 1, fneg, -nhi, -nlo, s, eps, r)
    sumf = acb(0)
    for n in range(nlo, nhi + 1):
        sumf += f[n]
    ie = I * eps
    Ap = ((-pi * eps / 2).exp() * (I * pi * (nu + 1 - s) / 2).exp() * acb(2) ** (-1 + s - ie)
          * (nu + 1 - s + ie).gamma() / (nu + 1 + s - ie).gamma() * sumf)
    a = nu + 1 + s - ie
    b = nu + 1 - s + ie
    V = acb(1)
    sumAm = acb(0)
    for n in range(0, nhi + 1):
        sumAm += V * f[n]
        V = -V * (a + n) / (b + n)
    V = acb(1)
    for n in range(-1, nlo - 1, -1):
        V = -V * (b + n) / (a + n)
        sumAm += V * f[n]
    Am = acb(2) ** (-1 - s + ie) * (-I * pi * (nu + 1 + s) / 2).exp() * (-pi * eps / 2).exp() * sumAm
    Btrans = acb(eps / omega) ** (2 * s) * sumf
    Binc = (1 / omega) * (Kp - I * (-I * pi * nu).exp() * (pi * (nu - s + ie)).sin()
                          / (pi * (nu + s - ie)).sin() * Km) * Ap * (-ie * eps.log()).exp()
    Bref = acb(omega) ** (-1 - 2 * s) * (Kp + I * (I * pi * nu).exp() * Km) * Am * (ie * eps.log()).exp()
    return dict(nu=nu, Btrans=Btrans, Binc=Binc, Bref=Bref, nlo=nlo, nhi=nhi)


def gamma_factors(s, l, omega, amp, C1=None, E1=None):
    """see mst.py docstring (identical formulas)."""
    w = arb(omega)
    Bt, Bi, Br = amp['Btrans'], amp['Binc'], amp['Bref']
    if s == 0:
        G = (2 * M) ** 2 * abs(Bt / Bi) ** 2
        Rf = abs(Br / Bi) ** 2
    elif s == -2:
        d = 16 * M ** 3 * (1 - 6 * I * M * w - 8 * M ** 2 * w ** 2)
        c0 = (l - 1) * l * (l + 1) * (l + 2) - 12 * I * M * w
        G = abs(d * Bt) ** 2 / abs(4 * w ** 2 * Bi) ** 2
        Rf = abs(c0 * Br) ** 2 / ((4 * w ** 2) ** 2 * abs(4 * w ** 2 * Bi) ** 2)
    elif s == -1:
        # C1 = 4, E1 = 1/16: fixed by flux conservation (unitarity_fit.py, spin1_constants.json)
        C1 = arb(4) if C1 is None else C1
        E1 = arb(1) / 16 if E1 is None else E1
        G = C1 * M ** 4 * (1 + 16 * M ** 2 * w ** 2) / w ** 2 * abs(Bt / Bi) ** 2
        Rf = E1 * (l * (l + 1)) ** 2 / w ** 4 * abs(Br / Bi) ** 2
    else:
        raise ValueError
    return G, Rf


def _normalize(nu):
    z = _c(nu)
    if abs(z.imag) > 1e-12:
        h = nearest_half(z)
        if abs(z.real - h) < 1e-12 and z.imag < 0:
            return 2 * acb(h) - nu
        if abs(z.real - h) >= 1e-12 and z.imag < 0:
            return nu.conjugate() if False else nu
    return nu


def acquire_nu(s, l, omegas, digits, w_start=0.01, verbose=False):
    """no-continuity root acquisition: at each node accept ANY genuine root of eq:nudefeq2
    (one class {nu+k, -nu-1+k}); fast path = extrapolation from the previous nodes, fallback = grid of
    guesses on the real axis and on the lines Re nu = h (h integer or half-integer)."""
    ws = [arb(w) for w in omegas]
    tolres = 10.0 ** (-(digits - 10))
    out = []
    hist = []
    for wa_ in ws:
        wf = float(wa_.mid())
        eps = 2 * M * wa_
        guesses = []
        if len(hist) >= 2:
            (w1, z1), (w2, z2) = hist[-2:]
            guesses.append(z2 + (z2 - z1) * (wf - w2) / (w2 - w1))
        if hist:
            guesses.append(hist[-1][1])
        if not hist:
            guesses.append(nu_lowfreq(s, l, 2 * M * wf))
        grid = []
        for hx in [l - 0.5, l - 1, l, l - 1.5, l + 0.5, l - 2]:
            for y in [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0]:
                grid.append(complex(hx, y))
        for x in range(0, 31):
            grid.append(complex(l + 0.5 - 0.05 * x, 0.0))
        found = None
        ntry = 0
        for g in guesses + grid:
            ntry += 1
            nu, res = solve_genuine(s, l, eps, g, digits)
            if nu is not None and res is not None and res < tolres:
                found = _normalize(nu)
                break
        if verbose:
            print('  w=%s tries=%d nu=%s' % (wf, ntry, _c(found) if found is not None else None), flush=True)
        if found is None:
            out.append(None)
            continue
        hist.append((wf, _c(found)))
        out.append(found)
    return out


def repair_nu(s, l, omegas, nus, digits):
    """retry failed nodes (None) using successful neighbours on both sides: direct guesses and the
    collision-regular variable u = (nu - h)^2 interpolated between the neighbours."""
    tolres = 10.0 ** (-(digits - 10))
    out = list(nus)
    for i, nu in enumerate(nus):
        if nu is not None:
            continue
        wa_ = arb(omegas[i])
        wf = float(wa_.mid())
        eps = 2 * M * wa_
        lo = next((j for j in range(i - 1, -1, -1) if out[j] is not None), None)
        hi = next((j for j in range(i + 1, len(out)) if out[j] is not None), None)
        cands = []
        for j in (lo, hi):
            if j is not None:
                cands.append(_c(out[j]))
        found = None
        for z in cands:
            nu2, res = solve_genuine(s, l, eps, z, digits)
            if nu2 is not None and res < tolres:
                found = nu2
                break
        if found is None and lo is not None and hi is not None:
            zl, zh = _c(out[lo]), _c(out[hi])
            wl, wh = float(arb(omegas[lo]).mid()), float(arb(omegas[hi]).mid())
            for h in sorted(set([nearest_half(zl), nearest_half(zh)])):
                ul, uh = ((zl - h) ** 2).real, ((zh - h) ** 2).real
                up = ul + (uh - ul) * (wf - wl) / (wh - wl)
                for du in (0, 0.01, -0.01, 0.05, -0.05):
                    u = solve_u(s, l, eps, h, up + du, digits)
                    if u is None:
                        continue
                    nu2 = nu_from_u(u, h, zl)
                    z2 = _c(nu2)
                    if is_spurious(z2):
                        continue
                    try:
                        res = residual(nu2, s, l, eps, digits)
                    except Exception:
                        continue
                    if res < tolres:
                        found = nu2
                        break
                if found is not None:
                    break
        out[i] = _normalize(found) if found is not None else None
    return out
