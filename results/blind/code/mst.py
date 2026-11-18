"""
MST (Mano-Suzuki-Takasugi) asymptotic amplitudes of the Teukolsky radial
in-mode on Schwarzschild (a = 0, kappa = 1, q = 0, m irrelevant, tau = eps, eps_+ = eps).

Every formula below is transcribed from
  Sasaki & Tagoshi, Living Rev. Relativ. 6 (2003) 6, arXiv:gr-qc/0306120,
  LaTeX source file livrev4.texin (downloaded to src_dl/lrr/):
    recurrence alpha/beta/gamma     : livrev4.texin lines 247-266 (eq:alpbetgam)
    continued fractions R_n, L_n    : lines 296-308 (eq:Rncont, eq:Lncont)
    nu equation                     : lines 414-418 (eq:nudefeq2), used at n = 0
    f_{-n}^{-nu-1} = f_n^nu         : lines 460-463
    nu -> l as eps -> 0             : lines 465-474; O(eps^2) start value eq:nusol lines 910-918
    A_+^nu, A_-^nu                  : lines 670-678
    K_nu                            : lines 755-776 (eq:Knu), r arbitrary integer
    B^trans, B^inc, B^ref           : lines 805-818
    lambda = l(l+1) - s(s+1)        : livrev4.texin line 87 (lambda_0, a = 0)
  R^in -> B^trans Delta^{-s} e^{-ikr*} (r->r+),
       -> B^inc r^{-1} e^{-i w r*} + B^ref r^{-1-2s} e^{i w r*} (r->inf)
  (general-s form implied by R_+^nu ~ z^{-1}, R_-^nu ~ z^{-1-2s}, lines 664-669).
Units: M = 1, eps = 2 M omega.
"""
import mpmath as mp

M = 1


class MSTError(Exception):
    pass


def _abg(n, nu, s, eps, lam):
    """alpha_n^nu, beta_n^nu, gamma_n^nu (eq:alpbetgam) with kappa=1, q=0, tau=eps."""
    I = mp.mpc(0, 1)
    nn = n + nu
    al = I * eps * (nn + 1 + s + I * eps) * (nn + 1 + s - I * eps) * (nn + 1 + I * eps) / ((nn + 1) * (2 * nn + 3))
    be = -lam - s * (s + 1) + nn * (nn + 1) + 2 * eps * eps + eps * eps * (s * s + eps * eps) / (nn * (nn + 1))
    ga = -I * eps * (nn - s + I * eps) * (nn - s - I * eps) * (nn - I * eps) / (nn * (2 * nn - 1))
    return al, be, ga


def _Rcf(nstart, nu, s, eps, lam, depth):
    R = mp.mpc(0)
    for n in range(nstart + depth, nstart - 1, -1):
        al, be, ga = _abg(n, nu, s, eps, lam)
        R = -ga / (be + al * R)
    return R


def _Lcf(nstart, nu, s, eps, lam, depth):
    L = mp.mpc(0)
    for n in range(nstart - depth, nstart + 1):
        al, be, ga = _abg(n, nu, s, eps, lam)
        L = -al / (be + ga * L)
    return L


def nu_function(nu, s, eps, lam, depth):
    al, be, ga = _abg(0, nu, s, eps, lam)
    return be + al * _Rcf(1, nu, s, eps, lam, depth) + ga * _Lcf(-1, nu, s, eps, lam, depth)


def cf_depth(eps):
    return int(30 + 10 * float(eps) + 0.7 * mp.mp.dps)


def nu_lowfreq(s, l, eps):
    """eq:nusol (livrev4.texin lines 910-918), O(eps^2); 0/0 terms at l = |s| = 0 taken as 0."""
    l = mp.mpf(l)
    c = mp.mpf(-2)
    if s != 0:
        c -= mp.mpf(s * s) / (l * (l + 1))
    c += ((l + 1) ** 2 - s * s) ** 2 / ((2 * l + 1) * (2 * l + 2) * (2 * l + 3))
    if l * l != s * s:
        c -= (l * l - s * s) ** 2 / ((2 * l - 1) * 2 * l * (2 * l + 1))
    return l + c / (2 * l + 1) * eps ** 2


def _solve(s, l, eps, guess, h):
    """secant polish of eq:nudefeq2; if h (half-integer) is given the function is deflated by (nu - h):
    the n = 0 equation has a spurious simple zero at the half-integer where the physical pair of
    roots nu, 2h - nu collides (found numerically, probe3.py)."""
    lam = l * (l + 1) - s * (s + 1)
    d = cf_depth(eps)

    def F(nu):
        try:
            v = nu_function(nu, s, eps, lam, d)
        except ZeroDivisionError:
            return mp.mpc(1e30)
        return v / (nu - h) if h is not None else v
    g = mp.mpc(guess)
    dh = mp.mpf(10) ** (-10) * (1 + abs(g))
    nu = mp.findroot(F, (g, g + mp.mpc(dh, dh / 3)), solver='secant',
                     tol=mp.mpf(10) ** (-2 * (mp.mp.dps - 6)), maxsteps=60, verify=False)
    nu = mp.mpc(nu)
    res = abs(nu_function(nu, s, eps, lam, 2 * d))
    if h is not None:
        res = res / abs(nu - h)
    return nu, res


def _nearest_half(x):
    return mp.nint(2 * mp.re(x)) / 2


def is_spurious(nu):
    """spurious zeros of the n = 0 equation sit exactly on real integers / half-integers."""
    return abs(mp.im(nu)) < 1e-8 and abs(mp.re(nu) - _nearest_half(nu)) < 1e-8


def solve_genuine(s, l, eps, guess):
    """find a genuine root of eq:nudefeq2 from a guess; deflate spurious exact (half-)integer zeros.
    Any genuine root is acceptable: all genuine roots form one class {nu + k, -nu - 1 + k}
    (cos 2 pi nu is fixed by the monodromy); unitarity is checked downstream on every point."""
    tol = mp.mpf(10) ** (-(mp.mp.dps - 12))
    h = None
    for attempt in range(4):
        nu, res = _solve(s, l, eps, guess, h)
        if res < tol and not is_spurious(nu):
            return nu, res
        if is_spurious(nu):
            h = _nearest_half(nu)
            continue
        return None, res
    return None, res


def track_nu(s, l, omegas, w_start='0.01', max_jump=0.08, verbose=False):
    """follow the physical root nu(omega) from nu -> l (eps -> 0) along ascending omegas.
    Representative chosen with Im nu >= 0. Extrapolation: linear in nu; on a collision
    (nu real, near a half-integer h, steep) fall back to probes h + i y."""
    ws = [mp.mpf(w) for w in omegas]
    w0 = min(mp.mpf(w_start), ws[0] / 2)
    nu, res = solve_genuine(s, l, 2 * M * w0, nu_lowfreq(s, l, 2 * M * w0))
    if nu is None:
        raise MSTError('start failed')
    hist = [(w0, nu)]
    out = []
    for w in ws:
        step = w - hist[-1][0]
        if len(hist) >= 2:
            step = min(step, 2 * (hist[-1][0] - hist[-2][0]) + mp.mpf('0.002'))
        while hist[-1][0] < w:
            wb, nb = hist[-1]
            wn = min(w, wb + step)
            guesses = []
            if len(hist) >= 2:
                wa, na = hist[-2]
                g = nb + (nb - na) * (wn - wb) / (wb - wa)
                if abs(mp.im(nb)) > 1e-6:             # complex phase: Re nu stays on a half-integer
                    g = mp.mpc(mp.re(nb), mp.im(g))
                guesses.append(g)
                if abs(mp.im(nb)) < 1e-6 and step < 0.002:
                    h = _nearest_half(g)
                    for y in ('0.01', '0.03', '0.1'):
                        guesses.append(mp.mpc(h, mp.mpf(y)))
            else:
                guesses.append(nb)
            ok = False
            for g in guesses:
                try:
                    nu, res = solve_genuine(s, l, 2 * M * wn, g)
                except Exception:
                    nu = None
                if nu is not None:
                    if mp.im(nu) < 0:
                        nu = mp.conj(nu) if abs(mp.re(nu) - _nearest_half(nu)) < 1e-20 else nu
                    if mp.im(nu) < -1e-20:
                        h = _nearest_half(nu)
                        nu = 2 * h - nu
                    if abs(nu - g) < max_jump or (abs(mp.im(nb)) < 1e-6 and abs(mp.re(nu) - _nearest_half(nb)) < 0.2 and abs(mp.im(nu)) < 0.2):
                        ok = True
                        break
            if verbose:
                print('   try w=%s step=%s guesses=%s -> %s ok=%s' % (mp.nstr(wn, 8), mp.nstr(step, 3), [mp.nstr(g, 6) for g in guesses], mp.nstr(nu, 8) if nu is not None else None, ok), flush=True)
            if ok:
                hist.append((wn, nu))
                step = step * 2
            else:
                step = step / 4
                if step < mp.mpf(10) ** (-7):
                    raise MSTError('nu tracking failed s=%d l=%d w=%s nu=%s' % (s, l, mp.nstr(wn, 8), mp.nstr(nb, 8)))
        out.append(hist[-1][1])
    return out


def coeffs_f(nu, s, eps, lam, tolexp):
    """minimal two-sided solution f_n normalised f_0 = 1, truncated where |f_n| < 10^-tolexp * max|f|."""
    small = mp.mpf(10) ** (-tolexp)
    nmax = cf_depth(eps)
    while True:
        depth = nmax + 20
        R = mp.mpc(0)
        Rs = {}
        for n in range(nmax + depth, 0, -1):
            al, be, ga = _abg(n, nu, s, eps, lam)
            R = -ga / (be + al * R)
            if n <= nmax:
                Rs[n] = R
        L = mp.mpc(0)
        Ls = {}
        for n in range(-nmax - depth, 0):
            al, be, ga = _abg(n, nu, s, eps, lam)
            L = -al / (be + ga * L)
            if n >= -nmax:
                Ls[n] = L
        f = {0: mp.mpc(1)}
        fmax = mp.mpf(1)
        np_ = None
        for n in range(1, nmax + 1):
            f[n] = f[n - 1] * Rs[n]
            fmax = max(fmax, abs(f[n]))
            if abs(f[n]) < small * fmax and n > 4:
                np_ = n
                break
        nm_ = None
        for n in range(-1, -nmax - 1, -1):
            f[n] = f[n + 1] * Ls[n]
            fmax = max(fmax, abs(f[n]))
            if abs(f[n]) < small * fmax and n < -4:
                nm_ = n
                break
        if np_ is not None and nm_ is not None:
            return f, nm_, np_
        nmax *= 2


def K_nu(nu, f, nlo, nhi, s, eps, r=0):
    """eq:Knu (kappa = 1, tau = eps, eps_+ = eps); f[n] = f_n for nlo <= n <= nhi.
    Terms of the two sums are generated by exact ratio recursions of the gamma/Pochhammer factors."""
    I = mp.mpc(0, 1)
    G = mp.gamma
    pref = (mp.exp(I * eps) * (2 * eps) ** (s - nu - r) * mp.mpf(2) ** (-s) * I ** r
            * G(1 - s - 2 * I * eps) * G(r + 2 * nu + 2)
            / (G(r + nu + 1 - s + I * eps) * G(r + nu + 1 + I * eps) * G(r + nu + 1 + s + I * eps)))
    # S1 = sum_{n=r}^{inf} T_n f_n,
    # T_n = (-1)^n G(n+r+2nu+1)/(n-r)! * G(n+nu+1+s+ie)/G(n+nu+1-s-ie) * G(n+nu+1+ie)/G(n+nu+1-ie)
    T = ((-1) ** r * G(2 * r + 2 * nu + 1) * G(r + nu + 1 + s + I * eps) / G(r + nu + 1 - s - I * eps)
         * G(r + nu + 1 + I * eps) / G(r + nu + 1 - I * eps))
    S1 = mp.mpc(0)
    for n in range(r, nhi + 1):
        S1 += T * f[n]
        T = (T * (-(n + r + 2 * nu + 1)) / (n + 1 - r) * (n + nu + 1 + s + I * eps) / (n + nu + 1 - s - I * eps)
             * (n + nu + 1 + I * eps) / (n + nu + 1 - I * eps))
    # S2 = sum_{n=-inf}^{r} U_n f_n, U_n = (-1)^n /((r-n)! (c)_n) * (a)_n/(b)_n,
    # a = nu+1+s-ie, b = nu+1-s+ie, c = r+2nu+2
    a = nu + 1 + s - I * eps
    b = nu + 1 - s + I * eps
    c = r + 2 * nu + 2
    U = (-1) ** r * mp.rf(a, r) / (mp.rf(c, r) * mp.rf(b, r))
    S2 = mp.mpc(0)
    for n in range(r, nlo - 1, -1):
        S2 += U * f[n]
        # U_{n-1}/U_n = -(r-n+1)^{-1} (c+n-1) (b+n-1) / (a+n-1)
        U = U * (-(c + n - 1)) * (b + n - 1) / ((r - n + 1) * (a + n - 1))
    return pref * S1 / S2


def amplitudes(s, l, omega, nu, tolexp=None, r=0):
    """B^trans, B^inc, B^ref (livrev4.texin lines 805-818) for a given physical root nu."""
    I = mp.mpc(0, 1)
    omega = mp.mpf(omega)
    eps = 2 * M * omega
    lam = l * (l + 1) - s * (s + 1)
    if tolexp is None:
        tolexp = mp.mp.dps + 8
    nu = mp.mpc(nu)
    f, nlo, nhi = coeffs_f(nu, s, eps, lam, tolexp)
    fneg = {-n: v for n, v in f.items()}            # f_n^{-nu-1} = f_{-n}^{nu}
    Kp = K_nu(nu, f, nlo, nhi, s, eps, r)
    Km = K_nu(-nu - 1, fneg, -nhi, -nlo, s, eps, r)
    sumf = mp.fsum(f[n] for n in range(nlo, nhi + 1))
    Ap = (mp.exp(-mp.pi * eps / 2) * mp.exp(I * mp.pi * (nu + 1 - s) / 2) * mp.mpf(2) ** (-1 + s - I * eps)
          * mp.gamma(nu + 1 - s + I * eps) / mp.gamma(nu + 1 + s - I * eps) * sumf)
    # sum_n (-1)^n (a)_n/(b)_n f_n, a = nu+1+s-ie, b = nu+1-s+ie
    a = nu + 1 + s - I * eps
    b = nu + 1 - s + I * eps
    V = mp.mpc(1)
    sumAm = mp.mpc(0)
    for n in range(0, nhi + 1):
        sumAm += V * f[n]
        V = -V * (a + n) / (b + n)
    V = mp.mpc(1)
    for n in range(-1, nlo - 1, -1):
        V = -V * (b + n) / (a + n)       # V_n = V_{n+1} * (-(b+n)/(a+n))
        sumAm += V * f[n]
    Am = mp.mpf(2) ** (-1 - s + I * eps) * mp.exp(-I * mp.pi * (nu + 1 + s) / 2) * mp.exp(-mp.pi * eps / 2) * sumAm
    Btrans = (eps / omega) ** (2 * s) * sumf
    Binc = (1 / omega) * (Kp - I * mp.exp(-I * mp.pi * nu) * mp.sin(mp.pi * (nu - s + I * eps))
                          / mp.sin(mp.pi * (nu + s - I * eps)) * Km) * Ap * mp.exp(-I * eps * mp.log(eps))
    Bref = omega ** (-1 - 2 * s) * (Kp + I * mp.exp(I * mp.pi * nu) * Km) * Am * mp.exp(I * eps * mp.log(eps))
    return dict(nu=nu, Btrans=Btrans, Binc=Binc, Bref=Bref, nlo=nlo, nhi=nhi, Kp=Kp, Km=Km)


# spin-1 constants (s = -1): fixed by flux conservation in unitarity_fit.py, see BLIND-REPORT.md
C1_SPIN1 = None
E1_SPIN1 = None


def gamma_factors(s, l, omega, amp, C1=None, E1=None):
    """transmission (Gamma) and reflection probabilities from Teukolsky amplitudes.
    s = 0 : psi = r R; Gamma = (2M)^2 |Bt/Bi|^2, Refl = |Br/Bi|^2.
    s = -2: LRR livrev2.texin lines 604-622: Bi = -Ai/(4w^2), Br = -4w^2 Ar/c0, Bt = At/d,
            c0 = (l-1)l(l+1)(l+2) - 12 i M w (line 567), d at a = 0, r+ = 2M:
            d = 16 M^3 (1 - 6 i M w - 8 M^2 w^2).  Gamma = |At/Ai|^2, Refl = |Ar/Ai|^2.
    s = -1: Gamma = C1 M^4 (1+16 M^2 w^2)/w^2 |Bt/Bi|^2, Refl = E1 (l(l+1))^2 / w^4 |Br/Bi|^2."""
    w = mp.mpf(omega)
    Bt, Bi, Br = amp['Btrans'], amp['Binc'], amp['Bref']
    I = mp.mpc(0, 1)
    if s == 0:
        G = (2 * M) ** 2 * abs(Bt / Bi) ** 2
        Rf = abs(Br / Bi) ** 2
    elif s == -2:
        d = 16 * M ** 3 * (1 - 6 * I * M * w - 8 * M ** 2 * w ** 2)
        c0 = (l - 1) * l * (l + 1) * (l + 2) - 12 * I * M * w
        G = abs(d * Bt) ** 2 / abs(4 * w ** 2 * Bi) ** 2
        Rf = abs(c0 * Br) ** 2 / (abs(4 * w ** 2) ** 2 * abs(4 * w ** 2 * Bi) ** 2)
    elif s == -1:
        C1 = C1 if C1 is not None else C1_SPIN1
        E1 = E1 if E1 is not None else E1_SPIN1
        G = C1 * M ** 4 * (1 + 16 * M ** 2 * w ** 2) / w ** 2 * abs(Bt / Bi) ** 2
        Rf = E1 * (l * (l + 1)) ** 2 / w ** 4 * abs(Br / Bi) ** 2
    else:
        raise MSTError('spin not supported')
    return G, Rf
