"""Combine per-l integrals into P_1, P_2, alpha, Sdot_1, Sdot_2, beta, t_page/t_decay for rules A and B,
plus a crude upper bound on the omega > WMAX tail (Gamma_l <= 1 for l <= 6w+11, (6w+12)^2 modes)."""
import json, sys
import mpmath as mp
mp.mp.dps = 40
D = '<LAB>/blind-1/'
r1 = json.load(open(D + 'main_s1.json'))
r2 = json.load(open(D + 'main_s2.json'))


def mid(sv):
    # arb string "[x +/- r]" -> mpf mid, mpf rad
    s = sv.strip('[]')
    if '+/-' in s:
        a, b = s.split('+/-')
        return mp.mpf(a.strip()), mp.mpf(b.strip())
    return mp.mpf(s), mp.mpf(0)


def totals(r, rule):
    P = mp.mpf(0); S = mp.mpf(0); rad = mp.mpf(0); last = None
    for l, v in sorted(r['per_l'].items(), key=lambda kv: int(kv[0])):
        p, pr = mid(v['rules'][rule]['P']); q, qr = mid(v['rules'][rule]['Sdot'])
        P += p; S += q; rad += pr + qr
        last = (int(l), p, q)
    return P, S, rad, last


wmax = mp.mpf(r1['wmax'])
B = lambda w: (6 * w + 12) ** 2
n = lambda w: 1 / (mp.exp(8 * mp.pi * w) - 1)
tailP = mp.quad(lambda w: B(w) * w * n(w), [wmax, wmax + 1, mp.inf]) / mp.pi
tailS = mp.quad(lambda w: B(w) * ((1 + n(w)) * mp.log1p(n(w)) - n(w) * mp.log(n(w))), [wmax, wmax + 1, mp.inf]) / mp.pi

res = {}
for rule in ('A', 'B'):
    P1, S1, rad1, last1 = totals(r1, rule)
    P2, S2, rad2, last2 = totals(r2, rule)
    alpha = P1 + P2
    beta = (S1 + S2) / (8 * mp.pi * alpha)
    tr = 1 - (beta / (beta + 1)) ** mp.mpf(1.5)
    res[rule] = dict(P1=P1, P2=P2, alpha=alpha, Sdot1=S1, Sdot2=S2, beta=beta, t_ratio=tr,
                     ballrad=rad1 + rad2, last_l_s1=last1, last_l_s2=last2)
out = {'tail_bound_P_per_spin': mp.nstr(tailP, 5), 'tail_bound_Sdot_per_spin': mp.nstr(tailS, 5)}
for k in ('P1', 'P2', 'alpha', 'Sdot1', 'Sdot2', 'beta', 't_ratio'):
    a, b = res['A'][k], res['B'][k]
    out[k] = {'B_16node': mp.nstr(b, 20), 'A_12node': mp.nstr(a, 20), 'rel_diff_A_B': mp.nstr(abs(a - b) / abs(b), 3)}
out['ball_radius_sum_B'] = mp.nstr(res['B']['ballrad'], 3)
out['last_l_s1'] = [res['B']['last_l_s1'][0], mp.nstr(res['B']['last_l_s1'][1], 3), mp.nstr(res['B']['last_l_s1'][2], 3)]
out['last_l_s2'] = [res['B']['last_l_s2'][0], mp.nstr(res['B']['last_l_s2'][1], 3), mp.nstr(res['B']['last_l_s2'][2], 3)]
out['failures_s1'] = r1['failures']; out['failures_s2'] = r2['failures']
out['missing_panels'] = sum(v['rules'][ru]['missing_panels'] for r in (r1, r2) for v in r['per_l'].values() for ru in ('A', 'B'))
out['worst_unitarity'] = max(v['worst_unitarity'] for r in (r1, r2) for v in r['per_l'].values())
out['mono_viol'] = sum(v['mono_viol'] for r in (r1, r2) for v in r['per_l'].values())
out['max_rel_ball_radius_Gamma'] = max(r1['max_rel_radius'], r2['max_rel_radius'])
out['time_s'] = [r1.get('total_time_s'), r2.get('total_time_s')]
json.dump(out, open(D + 'combined.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
