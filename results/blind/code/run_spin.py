"""Main run for one spin: Gamma_{s,l}(omega) on two Gauss-Legendre panel rules (A: 12 nodes/panel,
B: 16 nodes/panel), per-l energy and entropy integrals. Usage: run_spin.py <s> <digits> <out.json>"""
import sys, time, json, math
sys.path.insert(0, '<LAB>/blind-1')
import mpmath as mp
from flint import acb, arb, ctx
import mstf

s = int(sys.argv[1]); D = int(sys.argv[2]); outp = sys.argv[3]
WMAX = '1.8'
mstf.setprec(D)
mp.mp.dps = D + 10
edges = ['0', '0.0125', '0.025', '0.05', '0.1'] + ['%.1f' % (0.2 + 0.1 * k) for k in range(17)]
assert edges[-1] == WMAX


def gl_nodes(n):
    xs, ws = [], []
    for i in range(1, n + 1):
        x = mp.cos(mp.pi * (i - mp.mpf(1) / 4) / (n + mp.mpf(1) / 2))
        for _ in range(100):
            p0, p1 = mp.mpf(1), x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < mp.mpf(10) ** (-mp.mp.dps + 3):
                break
        xs.append(x); ws.append(2 / ((1 - x * x) * dp * dp))
    return xs, ws


def panel_nodes(a, b, n):
    xs, ws = gl_nodes(n)
    a, b = mp.mpf(a), mp.mpf(b)
    return [(a + b) / 2 + (b - a) / 2 * x for x in xs], [(b - a) / 2 * w for w in ws]


RULES = {'A': 12, 'B': 16}
nodes = {}
for name, n in RULES.items():
    W, Wt = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        x, w = panel_nodes(a, b, n)
        W += x; Wt += w
    nodes[name] = (W, Wt)
# union of nodes (sorted), evaluated once
allw = sorted(set(mp.nstr(w, D + 5) for name in nodes for w in nodes[name][0]), key=lambda z: mp.mpf(z))

TWO_PI_T = 8 * mp.pi        # 1/T = 8 pi M, M = 1


def integrands(G, w):
    """energy: omega Gamma n ; entropy: (1+N)ln(1+N) - N ln N, N = Gamma n (per mode, per helicity)."""
    w = arb(w)
    x = 8 * arb.pi() * w
    n = 1 / (x.exp() - 1)
    N = G * n
    e = w * N
    if float(N.mid()) <= 0:
        return e, arb(0)
    ent = (1 + N) * N.log1p() - N * N.log()
    return e, ent


res = {'s': s, 'digits': D, 'wmax': WMAX, 'edges': edges, 'rules': RULES, 'per_l': {}, 'failures': [], 'max_rel_radius': 0.0}
t0 = time.time()
prevG = None
negl = set()
l = abs(s)
while True:
    tl = time.time()
    # skip nodes where previous l already had Gamma < 1e-24 (monotone decrease in l at fixed omega, checked below)
    todo = [w for w in allw if w not in negl]
    if not todo:
        break
    nus = mstf.acquire_nu(s, l, todo, D)
    nfail0 = sum(1 for v in nus if v is None)
    if nfail0:
        nus = mstf.repair_nu(s, l, todo, nus, D)
        print('   repaired %d of %d failed nodes' % (nfail0 - sum(1 for v in nus if v is None), nfail0), flush=True)
    Gs = {}
    for w, nu in zip(todo, nus):
        if nu is None:
            res['failures'].append([l, w])
            continue
        a = mstf.amplitudes(s, l, w, nu, D)
        G, R = mstf.gamma_factors(s, l, w, a)
        u = abs(float((1 - G - R).mid()))
        rr = float(G.rad()) / max(float(G.mid()), 1e-300)
        res['max_rel_radius'] = max(res['max_rel_radius'], rr)
        Gs[w] = (G, u)
    # monotonicity check vs previous l
    mono_viol = 0
    if prevG is not None:
        for w in Gs:
            if float(Gs[w][0].mid()) > prevG.get(w, 1.0) * (1 + 1e-12):
                mono_viol += 1
    def gamma_list(ws_keys):
        nn = mstf.acquire_nu(s, l, ws_keys, D)
        if any(v is None for v in nn):
            nn = mstf.repair_nu(s, l, ws_keys, nn, D)
        outg = {}
        for w, nu in zip(ws_keys, nn):
            if nu is None:
                return None
            a_ = mstf.amplitudes(s, l, w, nu, D)
            G_, R_ = mstf.gamma_factors(s, l, w, a_)
            outg[w] = (G_, abs(float((1 - G_ - R_).mid())))
        return outg

    out = {}
    for name, n in RULES.items():
        E = arb(0); S = arb(0); missing = 0; subst = []
        for a, b in zip(edges[:-1], edges[1:]):
            xs, wts = panel_nodes(a, b, n)
            keys = [mp.nstr(x, D + 5) for x in xs]
            need = [k for k in keys if k not in Gs and k not in negl]
            if need:
                ok = False
                for n2 in (n + 1, n + 2, n + 3):
                    xs, wts = panel_nodes(a, b, n2)
                    keys = [mp.nstr(x, D + 5) for x in xs]
                    extra = gamma_list(keys)
                    if extra is not None:
                        Gs.update(extra)
                        subst.append([a, b, n2])
                        ok = True
                        break
                if not ok:
                    missing += 1
                    continue
            for k, wt in zip(keys, wts):
                if k in negl and k not in Gs:
                    continue
                e, en = integrands(Gs[k][0], k)
                E += arb(mp.nstr(wt, D + 5)) * e
                S += arb(mp.nstr(wt, D + 5)) * en
        fac = (2 * l + 1) / arb.pi()       # (2l+1) * 2/(2 pi)
        out[name] = {'P': (fac * E).str(radius=True), 'Sdot': (fac * S).str(radius=True), 'missing_panels': missing,
                     'substituted_panels': subst}
    worst_u = max((v[1] for v in Gs.values()), default=0.0)
    res['per_l'][str(l)] = {'rules': out, 'n_nodes': len(Gs), 'worst_unitarity': worst_u, 'mono_viol': mono_viol,
                            'time_s': round(time.time() - tl, 1),
                            'Gamma_at': {w: Gs[w][0].str(10) for w in list(Gs)[::max(1, len(Gs) // 6)]}}
    print('s=%d l=%d nodes=%d worst|1-G-R|=%.1e mono_viol=%d PA=%s PB=%s SA=%s SB=%s subst=%s/%s t=%.1fs' % (
        s, l, len(Gs), worst_u, mono_viol, out['A']['P'], out['B']['P'], out['A']['Sdot'], out['B']['Sdot'],
        out['A']['substituted_panels'], out['B']['substituted_panels'], time.time() - tl), flush=True)
    prevG = {w: float(Gs[w][0].mid()) for w in Gs}
    negl |= set(w for w in Gs if prevG[w] < 1e-24)
    json.dump(res, open(outp, 'w'), indent=1)
    l += 1
    if l > 40:
        break
res['total_time_s'] = round(time.time() - t0, 1)
json.dump(res, open(outp, 'w'), indent=1)
print('DONE total %.1fs failures %d' % (time.time() - t0, len(res['failures'])))
