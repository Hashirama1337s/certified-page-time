"""Controls (run after the main jobs):
 C1 low-frequency limit: s = 0, l = 0: Gamma -> 16 M^2 w^2  (sigma_abs = pi Gamma / w^2 -> 16 pi M^2 = horizon area)
 C2 precision: Gamma at sample nodes, 40 vs 55 digits
 C3 K_nu matching index r = 0 vs r = 1 (eq:Knu says K_nu is independent of r)
 C4 f_n series cutoff 10^-(D+8) vs 10^-(D+23)
 C5 flux conservation |1 - Gamma - Refl| at the same samples
 C6 s = 0 l = 0 crude independent check: Gamma(w) at w -> large -> 1
"""
import sys, time, json
sys.path.insert(0, '<LAB>/blind-1')
from flint import acb, arb, ctx
import mstf

out = {}
t0 = time.time()
mstf.setprec(40)
# C1
c1 = {}
ws = ['0.001', '0.0001', '0.00001']
nus = mstf.acquire_nu(0, 0, ws, 40)
for w, nu in zip(ws, nus):
    a = mstf.amplitudes(0, 0, w, nu, 40)
    G, R = mstf.gamma_factors(0, 0, w, a)
    c1[w] = {'Gamma_over_16w2': (G / (16 * arb(w) ** 2)).str(15), 'unitarity': (1 - G - R).str(3)}
out['C1_area_limit_s0_l0'] = c1
print('C1', c1, flush=True)

samples = [(-1, 1, ['0.03', '0.17', '0.31', '0.62', '1.13']), (-1, 3, ['0.21', '0.55', '1.2']),
           (-2, 2, ['0.03', '0.21', '0.44', '0.9', '1.37']), (-2, 4, ['0.33', '0.8', '1.5']), (-1, 9, ['1.1', '1.7']),
           (-2, 10, ['1.3', '1.75'])]
c2 = []
for s, l, ws in samples:
    mstf.setprec(40)
    n40 = mstf.acquire_nu(s, l, ws, 40)
    n40 = mstf.repair_nu(s, l, ws, n40, 40)
    vals40 = {}
    for w, nu in zip(ws, n40):
        a = mstf.amplitudes(s, l, w, nu, 40)
        G, R = mstf.gamma_factors(s, l, w, a)
        a1 = mstf.amplitudes(s, l, w, nu, 40, r=1)
        G1, _ = mstf.gamma_factors(s, l, w, a1)
        a2 = mstf.amplitudes(s, l, w, nu, 40, tolexp=63)
        G2, _ = mstf.gamma_factors(s, l, w, a2)
        vals40[w] = (G, R, G1, G2, mstf._c(nu))
    mstf.setprec(55)
    n55 = mstf.acquire_nu(s, l, ws, 55)
    n55 = mstf.repair_nu(s, l, ws, n55, 55)
    for w, nu in zip(ws, n55):
        a = mstf.amplitudes(s, l, w, nu, 55)
        G55, _ = mstf.gamma_factors(s, l, w, a)
        G, R, G1, G2, z = vals40[w]
        g = float(G.mid())
        row = {'s': s, 'l': l, 'w': w, 'nu40': str(z), 'nu55': str(mstf._c(nu)), 'Gamma40': G.str(20), 'Gamma55': G55.str(25),
               'rel_40_vs_55': abs(float((G - G55).mid())) / g,
               'rel_r0_vs_r1': abs(float((G - G1).mid())) / g,
               'rel_cutoff': abs(float((G - G2).mid())) / g,
               'unitarity40': abs(float((1 - G - R).mid()))}
        c2.append(row)
        print(row, flush=True)
out['C2_C3_C4_C5_samples'] = c2
out['C2_max_rel_40_vs_55'] = max(r['rel_40_vs_55'] for r in c2)
out['C3_max_rel_r0_vs_r1'] = max(r['rel_r0_vs_r1'] for r in c2)
out['C4_max_rel_cutoff'] = max(r['rel_cutoff'] for r in c2)
out['C5_max_unitarity'] = max(r['unitarity40'] for r in c2)
out['time_s'] = round(time.time() - t0, 1)
json.dump(out, open('<LAB>/blind-1/controls.json', 'w'), indent=1)
print('DONE', out['C2_max_rel_40_vs_55'], out['C3_max_rel_r0_vs_r1'], out['C4_max_rel_cutoff'], out['C5_max_unitarity'], out['time_s'])
