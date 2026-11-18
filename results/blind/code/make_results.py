import json
import mpmath as mp
mp.mp.dps = 40
c = json.load(open('<LAB>/blind-1/combined.json'))
ctl = json.load(open('<LAB>/blind-1/controls.json'))
tailP = mp.mpf(c['tail_bound_P_per_spin']); tailS = mp.mpf(c['tail_bound_Sdot_per_spin'])
out = {'method': 'MST hypergeometric/Coulomb series solution of the Teukolsky radial equation (s=-1, s=-2), Gauss-Legendre panels; NOT a rigorous enclosure (high precision + convergence study)',
       'units': 'G=c=hbar=k=1, M=1', 'resume_tested': 'not applicable (no checkpoint path)'}
for k in ('P1', 'P2', 'alpha', 'Sdot1', 'Sdot2', 'beta', 't_ratio'):
    b = mp.mpf(c[k]['B_16node']); a = mp.mpf(c[k]['A_12node'])
    err = abs(a - b)
    if k in ('P1', 'P2'):
        err += tailP
    elif k in ('Sdot1', 'Sdot2'):
        err += tailS
    elif k == 'alpha':
        err += 2 * tailP
    elif k in ('beta', 't_ratio'):
        rel = abs(a - b) / b + 2 * tailP / mp.mpf(c['alpha']['B_16node']) + 2 * tailS / (mp.mpf(c['Sdot1']['B_16node']) + mp.mpf(c['Sdot2']['B_16node']))
        err = rel * b
    out[k] = {'value_13sig': mp.nstr(b, 13), 'value_raw_B': c[k]['B_16node'], 'abs_error_estimate': mp.nstr(3 * err, 2),
              'rel_error_estimate': mp.nstr(3 * err / b, 2)}
out['controls'] = {'max_unitarity_residual_all_nodes': c['worst_unitarity'], 'max_rel_Gamma_40_vs_55_digits': ctl['C2_max_rel_40_vs_55'],
                   'max_rel_Gamma_Knu_r0_vs_r1': ctl['C3_max_rel_r0_vs_r1'], 'max_rel_Gamma_series_cutoff': ctl['C4_max_rel_cutoff'],
                   'area_limit_Gamma00_over_16w2': ctl['C1_area_limit_s0_l0'], 'missing_panels': c['missing_panels'],
                   'monotonicity_violations': c['mono_viol']}
json.dump(out, open('<LAB>/blind-1/results.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
