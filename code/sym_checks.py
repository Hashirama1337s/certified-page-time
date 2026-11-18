"""symbolic identities used by the instrument (sympy; build seat build-1).  Each prints True."""
import sympy as sp
r, L, c, w, n = sp.symbols('r L c w n', real=True)
h = sp.Function('h')
f = 1 - 2 / r
# (1) r^5 V'(r) = -2 L r^2 + (6L - 3c) r + 8c for V = (r-2)(L r + c)/r^4   (hkbounds monotone cells)
V = (r - 2) * (L * r + c) / r ** 4
print(sp.simplify(r ** 5 * sp.diff(V, r) - (-2 * L * r ** 2 + (6 * L - 3 * c) * r + 8 * c)) == 0)
# (2) F_0(n + rho) = 4 D(2) ((n+rho)^2 + 4 w^2) = 4 D(2) n (n - 4 i w) with rho = -2 i w   (hkcore frob_coeffs)
rho = -2 * sp.I * w
print(sp.expand((n + rho) ** 2 + 4 * w ** 2 - n * (n - 4 * sp.I * w)) == 0)
# (3) far field: u = e^{i w r*} h(r), r* = r + 2 ln(r/2 - 1):  f (f u')' + (w^2 - V) u = e^{i w r*} f [f h'' + (f' + 2 i w) h' - (V/f) h]
rs = r + 2 * sp.log(r / 2 - 1)
u = sp.exp(sp.I * w * rs) * h(r)
lhs = f * sp.diff(f * sp.diff(u, r), r) + (w ** 2 - V) * u
rhs = sp.exp(sp.I * w * rs) * f * (f * sp.diff(h(r), r, 2) + (sp.diff(f, r) + 2 * sp.I * w) * sp.diff(h(r), r) - (V / f) * h(r))
print(sp.simplify(sp.expand(lhs - rhs)) == 0)
# (4) polynomial r-form: r^4 [f (f psi')' + (w^2 - V) psi] = r^2 (r-2)^2 psi'' + 2 r (r-2) psi' + [w^2 r^4 - (r-2)(L r + c)] psi
p = sp.Function('p')
lhs = r ** 4 * (f * sp.diff(f * sp.diff(p(r), r), r) + (w ** 2 - V) * p(r))
rhs = r ** 2 * (r - 2) ** 2 * sp.diff(p(r), r, 2) + 2 * r * (r - 2) * sp.diff(p(r), r) + (w ** 2 * r ** 4 - (r - 2) * (L * r + c)) * p(r)
print(sp.simplify(sp.expand(lhs - rhs)) == 0)
# (5) asymptotic recurrence of hkcore.far_coeffs (RW) equals 2iw m c_m = [(m-1)m - L] c_{m-1} - 2((m-1)^2 - s^2) c_{m-2} with c = 2(1-s^2)
m, s = sp.symbols('m s')
X_m1 = (m - 1) * m - L
X_m2 = -2 * (m - 2) * (m - 1) - 2 * (m - 2) - 2 * (1 - s ** 2)
print(sp.expand(X_m2 + 2 * ((m - 1) ** 2 - s ** 2)) == 0)
# (6) S(n) = ln(1+n) + 8 pi w n exactly when n = 1/(e^{8 pi w} - 1)   (hkbounds Planck tails)
x = sp.symbols('x', positive=True)
nn = 1 / (sp.exp(x) - 1)
print(sp.simplify(1 + nn - nn * sp.exp(x)) == 0)          # 1 + n = n e^x, hence ln(1+n) = x + ln n
N, lnN = sp.symbols('N lnN', positive=True)
S = (1 + N) * (x + lnN) - N * lnN                         # S(n) with ln(1+n) -> x + ln n
print(sp.expand(S - ((x + lnN) + x * N)) == 0)            # = ln(1+n) + x n
