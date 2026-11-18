"""Fix the two spin-1 flux constants by flux conservation Gamma + Refl = 1:
   C1 * X + E1 * Y = 1, X = (1+16 M^2 w^2)/w^2 |Bt/Bi|^2 (M^4 = 1), Y = (l(l+1))^2/w^4 |Br/Bi|^2.
   Solve from two (l, w) points, then test the same two constants on many other (l, w) points."""
import sys, time, json
sys.path.insert(0, '<LAB>/blind-1')
from flint import acb, arb, ctx
import mstf
D = 30
mstf.setprec(D)
t0 = time.time()
pts = {}
for l in [1, 2, 3]:
    ws = ['0.07', '0.15', '0.25', '0.35', '0.5', '0.7', '0.9']
    nus = mstf.acquire_nu(-1, l, ws, D)
    for w, nu in zip(ws, nus):
        a = mstf.amplitudes(-1, l, w, nu, D)
        wa = arb(w)
        X = (1 + 16 * wa ** 2) / wa ** 2 * abs(a['Btrans'] / a['Binc']) ** 2
        Y = arb(l * (l + 1)) ** 2 / wa ** 4 * abs(a['Bref'] / a['Binc']) ** 2
        pts[(l, w)] = (X, Y)
(X1, Y1), (X2, Y2) = pts[(1, '0.25')], pts[(2, '0.5')]
det = X1 * Y2 - X2 * Y1
C1 = (Y2 - Y1) / det
E1 = (X1 - X2) / det
print('C1 =', C1.str(25), ' E1 =', E1.str(25))
worst = 0
for k, (X, Y) in pts.items():
    r = C1 * X + E1 * Y - 1
    worst = max(worst, abs(float(r.mid())))
    print(k, 'Gamma', (C1 * X).str(12), 'C1*X+E1*Y-1 =', r.str(3))
print('worst', worst, 'time %.1f' % (time.time() - t0))
json.dump({'C1': C1.str(radius=True), 'E1': E1.str(radius=True), 'worst_unitarity_residual': worst}, open('<LAB>/blind-1/spin1_constants.json', 'w'), indent=1)
