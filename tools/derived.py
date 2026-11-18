#!/usr/bin/env python
"""derived.py -- every derived number quoted in README.md, paper.md and CLAIMS.md, computed from the shipped results.

Reads (nothing else):
  results/hk1b/result_hk1b.json   certified enclosures of the sealed HOLD run (values, closed_forms, channel_status, tails)
  results/blind/results.json      the blind second implementation (not rigorous; error estimates from its convergence study)
Writes results/derived.json and prints it. All arithmetic is ball arithmetic (python-flint / Arb, 256 bits); a lower bound
is printed rounded down and an upper bound rounded up.

Printed values of other authors are typed below with their source (they are comparison points, not inputs):
  Page 2013 (arXiv:1301.4995v3, p. 5-6, Eq. (2)): photon power 0.000033638, graviton power 0.000003836, beta 1.48472
  Perez-Gonzalez 2025 (arXiv:2502.04430v3, after Eq. (18)): beta 1.48471
  Newton 2026 (Zenodo 10.5281/zenodo.22800587, Theorem 3, Eq. (47)): 3.8262e-6 < M^2 P_grav < 3.8639e-6
Run from anywhere:  python tools/derived.py [--out FILE]   (default output: results/derived.json)
"""
import json
import os
import sys
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR

from flint import arb, ctx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ctx.prec = 256

PAGE = {'P_1': '0.000033638', 'P_2': '0.000003836', 'beta': '1.48472'}
PEREZ_GONZALEZ_BETA = '1.48471'
NEWTON = ('3.8262e-6', '3.8639e-6')
BLIND_KEYS = {'P_1': 'P1', 'P_2': 'P2', 'alpha': 'alpha', 'Sdot_1': 'Sdot1', 'Sdot_2': 'Sdot2', 'beta': 'beta',
              'page_time': 't_ratio'}


def load(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return json.load(f)


def ends(x):
    """(lower, upper) of a ball as arb points."""
    return x.mid() - x.rad(), x.mid() + x.rad()


def down(x, n=6):
    """a decimal string <= x (n significant digits)."""
    d = Decimal(x.lower().mid().str(40, radius=False))
    e = d.adjusted()
    q = Decimal(1).scaleb(e - n + 1)
    return str(d.quantize(q, rounding=ROUND_FLOOR))


def up(x, n=6):
    d = Decimal(x.upper().mid().str(40, radius=False))
    e = d.adjusted()
    q = Decimal(1).scaleb(e - n + 1)
    return str(d.quantize(q, rounding=ROUND_CEILING))


def rounding_interval(s):
    """numbers that round to the printed decimal s (half a unit in its last digit)."""
    mant = s.lower().split('e')[0]
    ex = int(s.lower().split('e')[1]) if 'e' in s.lower() else 0
    dec = len(mant.split('.')[1]) if '.' in mant else 0
    half = arb(5) * arb(10) ** (ex - dec - 1)
    return arb(s) - half, arb(s) + half


def main():
    r = load('results/hk1b/result_hk1b.json')
    bl = load('results/blind/results.json')
    v = {k: arb(s) for k, s in r['values'].items()}
    cf = {k: arb(s) for k, s in r['closed_forms'].items()}
    out = {'source': 'results/hk1b/result_hk1b.json, results/blind/results.json'}

    # beta against the two printed values (rounding intervals, as AMEND-HK-1-1 reads them)
    lo, hi = ends(v['beta'])
    pg_lo, _ = rounding_interval(PEREZ_GONZALEZ_BETA)
    pa_lo, _ = rounding_interval(PAGE['beta'])
    out['beta_interval'] = [down(lo, 12), up(hi, 12)]
    out['beta_width_upper'] = up(2 * v['beta'].rad(), 3)
    out['beta_gap_below_1.48471_rounding_interval_lower'] = down(pg_lo - hi, 4)
    out['beta_gap_below_1.48472_rounding_interval_lower'] = down(pa_lo - hi, 4)
    out['beta_gap_below_1.48471_rounding_interval_lower_ppm'] = down((pg_lo - hi) / hi * 10 ** 6, 3)
    out['beta_gap_below_1.48472_rounding_interval_lower_ppm'] = down((pa_lo - hi) / hi * 10 ** 6, 3)
    out['rounding_width_over_beta_width_lower'] = down(arb('1e-5') / (2 * v['beta'].rad()), 3)
    out['beta_relative_below_1.48472_lower_ppm'] = down((arb(PAGE['beta']) - hi) / hi * 10 ** 6, 3)
    out['beta_relative_below_1.48471_lower_ppm'] = down((arb(PEREZ_GONZALEZ_BETA) - hi) / hi * 10 ** 6, 3)

    # shares of the energy budget and the entropy budget
    out['photon_share_of_alpha'] = [down(v['P_1'] / v['alpha'], 5), up(v['P_1'] / v['alpha'], 5)]
    out['graviton_share_of_alpha'] = [down(v['P_2'] / v['alpha'], 5), up(v['P_2'] / v['alpha'], 5)]
    s_tot = v['Sdot_1'] + v['Sdot_2']
    out['photon_share_of_entropy_rate'] = [down(v['Sdot_1'] / s_tot, 5), up(v['Sdot_1'] / s_tot, 5)]
    out['page_time_percent'] = [down(v['page_time'] * 100, 6), up(v['page_time'] * 100, 6)]
    out['entropy_lost_by_page_time'] = [down(1 - cf['S_star_over_SBH0'], 6), up(1 - cf['S_star_over_SBH0'], 6)]
    out['mass_left_at_page_time'] = [down(cf['M_star_over_M0'], 6), up(cf['M_star_over_M0'], 6)]

    # per channel, with the factor 2(2l+1)/(2 pi) (both helicities); tails l > 9 per spin
    ch = {}
    sums = {1: [arb(0), arb(0)], 2: [arb(0), arb(0)]}
    for key, row in r['channel_status'].items():
        s, l = (int(x) for x in key.split(','))
        g = arb(2 * (2 * l + 1)) / (2 * arb.pi())
        P, S = g * arb(row['P_mode']), g * arb(row['S_mode'])
        ch[key] = (P, S)
        sums[s][0] += P
        sums[s][1] += S
    for s in (1, 2):
        sums[s][0] += arb(r['tails'][str(s)]['P']).union(arb(0))
        sums[s][1] += arb(r['tails'][str(s)]['S']).union(arb(0))
    out['channel_sum_overlaps'] = {
        'P_1': bool(sums[1][0].overlaps(v['P_1'])), 'P_2': bool(sums[2][0].overlaps(v['P_2'])),
        'Sdot_1': bool(sums[1][1].overlaps(v['Sdot_1'])), 'Sdot_2': bool(sums[2][1].overlaps(v['Sdot_2']))}
    out['share_l1_of_photon_power'] = [down(ch['1,1'][0] / v['P_1'], 5), up(ch['1,1'][0] / v['P_1'], 5)]
    out['share_l2_of_graviton_power'] = [down(ch['2,2'][0] / v['P_2'], 5), up(ch['2,2'][0] / v['P_2'], 5)]
    out['share_l1_of_photon_entropy'] = [down(ch['1,1'][1] / v['Sdot_1'], 5), up(ch['1,1'][1] / v['Sdot_1'], 5)]
    out['share_l2_of_graviton_entropy'] = [down(ch['2,2'][1] / v['Sdot_2'], 5), up(ch['2,2'][1] / v['Sdot_2'], 5)]
    out['relative_widths_upper'] = {k: up(2 * x.rad() / abs(x.mid()), 2) for k, x in v.items()}

    # Newton's certified graviton interval (credited prior work)
    nl, nh = arb(NEWTON[0]), arb(NEWTON[1])
    p2lo, p2hi = ends(v['P_2'])
    out['P_2_inside_newton'] = bool(p2lo > nl and p2hi < nh)
    out['newton_relative_width_upper'] = up((nh - nl) / v['P_2'].mid(), 3)
    out['newton_width_over_our_P_2_width_lower'] = down((nh - nl) / (2 * v['P_2'].rad()), 3)

    # blind second implementation (not rigorous): overlap of value +/- error estimate with the certified ball
    bo = {}
    for k, bk in BLIND_KEYS.items():
        x = bl[bk]
        b = arb(x['value_raw_B'], x['abs_error_estimate'])
        bo[k] = {'blind': x['value_13sig'], 'overlaps_certified': bool(b.overlaps(v[k])),
                 'inside_certified_ball': bool(v[k].contains(arb(x['value_raw_B']))),
                 'relative_difference_of_midpoints_upper': up(abs(arb(x['value_raw_B']) - v[k].mid()) / abs(v[k].mid()), 2)}
    out['blind'] = bo

    # post hoc: Page's printed power values against the certified enclosures (observation, not sealed)
    ph = {}
    for k in ('P_1', 'P_2'):
        a, b = rounding_interval(PAGE[k])
        lo_k, hi_k = ends(v[k])
        ph[k] = {'printed': PAGE[k], 'rounding_interval_disjoint': bool(b < lo_k or a > hi_k),
                 'printed_relative_to_certified_mid': [down((arb(PAGE[k]) - v[k].mid()) / v[k].mid(), 3),
                                                       up((arb(PAGE[k]) - v[k].mid()) / v[k].mid(), 3)]}
    out['page_printed_powers_post_hoc'] = ph

    dst = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(ROOT, 'results', 'derived.json')
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, indent=1)
        f.write('\n')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
