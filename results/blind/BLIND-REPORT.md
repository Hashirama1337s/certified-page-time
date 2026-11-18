# BLIND-REPORT: Hawking emission of photons and gravitons from Schwarzschild (blind-1 seat)

## Disclosures (read first)

- **Brief hygiene.** The brief gave the definitions of P_s, Sdot_s, alpha and beta and the formula
  t_page/t_decay = 1 - (beta/(beta+1))^(3/2). That formula is a definition of the output, not a target. The brief gave
  no target numbers, functional forms or leading terms for the constants.
- **Prior recollection.** Before computing, I had an imprecise memory, from training and not from any file opened in
  this session, that Page's published photon+graviton values are about beta ~ 1.4847, t_page ~ 0.538 t_decay and
  alpha ~ 3.747e-5. I did not open or use any literature values. The method has no tunable parameter: every constant is
  either transcribed from a source or fixed by flux conservation. So that memory could not steer the digits, but the
  lead should know it existed.
- **Forbidden paths.** I did not open any of them: build-1/, BAR-*, AMEND-*, RECON-EMERGENT seats/COMPUTING, lab memory
  or LOG files. One Read of a web-fetch cache file under [a session cache folder; path redacted]/... was refused by the guard
  before any content was shown. It held only the arXiv PDF of the review cited below, which I then downloaded into my
  own folder instead.
- **Rigor.** These are **not rigorous enclosures**. They are high-precision values with an explicit convergence study.
  Rounding is tracked by ball arithmetic (python-flint acb at 40 digits). Truncations (continued fractions, f_n series,
  l-sum, omega cutoff, quadrature) are controlled by convergence checks, not proved bounds.

## Method (different from Regge-Wheeler/Zerilli series and Taylor stepping)

**Equation and basis.** I used the Teukolsky radial equation with s = -1 (photons) and s = -2 (gravitons), solved
analytically with the Mano-Suzuki-Takasugi (MST) method: a two-sided series of hypergeometric functions near the
horizon, a series of Coulomb wave functions at infinity, and the renormalized angular momentum nu fixed by a
continued-fraction equation. The asymptotic amplitudes B^trans, B^inc and B^ref come in closed form as gamma-function
sums. There is no radial ODE integration of any kind.

**Source.** All formulas were transcribed from Sasaki & Tagoshi, Living Rev. Relativ. 6 (2003) 6, arXiv:gr-qc/0306120.
I downloaded the LaTeX source to src_dl/lrr/. Locators in livrev4.texin:
- recurrence alpha_n, beta_n, gamma_n: lines 247-266
- continued fractions: lines 296-308
- nu equation (n = 0): lines 414-418
- f_{-n}^{-nu-1} = f_n^nu: lines 460-463
- low-frequency nu: lines 910-918
- A_+, A_-: lines 670-678
- K_nu: lines 755-776
- B^trans, B^inc, B^ref: lines 805-818
- lambda = l(l+1) - s(s+1): line 87

Settings: a = 0, so kappa = 1, q = 0, tau = eps = 2M omega.

**Transmission factors.**
- **s = -2**: Gamma = |A^trans/A^inc|^2, using the Chandrasekhar-transformation relations in livrev2.texin lines
  604-622: B^inc = -A^inc/(4 omega^2), B^ref = -4 omega^2 A^ref/c0, B^trans = A^trans/d. Here
  c0 = (l-1)l(l+1)(l+2) - 12iM omega, and at a = 0, d = 16M^3 (1 - 6iM omega - 8M^2 omega^2).
- **s = -1**: no transcribed relation was available, so I fixed it by flux conservation (derived, not transcribed).
  The ansatz is Gamma = C1 M^4 (1+16M^2 omega^2)/omega^2 |B^trans/B^inc|^2 and Refl = E1 (l(l+1))^2/omega^4 |B^ref/B^inc|^2.
  Solving Gamma + Refl = 1 at two (l, omega) points gave C1 = 4.0000000000000000000000000 and E1 = 0.0625 = 1/16, both
  to 25 digits. With these two constants fixed, Gamma + Refl = 1 then holds to 1e-25 at 19 other points, and to 1e-35 or
  better at every one of about 6000 production nodes. Files: unitarity_fit.py, spin1_constants.json.
- **s = 0** was used only as a control: Gamma = (2M)^2 |B^trans/B^inc|^2 and Refl = |B^ref/B^inc|^2.

**Choosing nu.** The genuine roots of the nu equation form one class {nu + k, -nu - 1 + k}, so any genuine root gives the
same physical solution. The engine (mstf.py) accepts any genuine root at each node. It tries extrapolation from the
previous node first, then a guess grid on the real axis and on the lines Re nu = integer or half-integer. Spurious zeros
that sit exactly on lattice points are deflated. Failed nodes are repaired from neighbours using u = (nu - h)^2.

**Quadrature.** Gauss-Legendre panels on [0, 1.8]: graded edges 0, 0.0125, 0.025, 0.05, 0.1, then steps of 0.1 to 1.8.
- Rule A uses 12 nodes per panel; rule B uses 16.
- If a node fails (very near a nu-collision), that whole panel is recomputed with an (n+1)-point Gauss rule. This
  happened in 2 photon panels: l=1 on [1.5, 1.6] and l=2 on [1.4, 1.5]. No panel was left missing.
- l runs from |s| upward. A node is dropped for higher l once Gamma_l < 1e-24 there; monotone decrease in l was checked
  at every node, with 0 violations. The last l computed is 17 for both spins, and its contribution is about 1e-44.
- The omega > 1.8 tail is bounded crudely by assuming (6 omega + 12)^2 modes, each with Gamma = 1. This gives at most
  2.8e-19 per spin for P and at most 7.2e-18 for Sdot.
- Integrands: (2l+1)/pi * omega Gamma n for energy, and (2l+1)/pi * [(1+N)ln(1+N) - N ln N] with N = Gamma n for
  entropy, where n = 1/(e^{8 pi M omega} - 1). The factor 2/(2 pi) = 1/pi covers both helicities. M = 1.
- beta = (Sdot_1 + Sdot_2)/(8 pi alpha), and t_page/t_decay = 1 - (beta/(beta+1))^{3/2}.

## Controls (all passed)

| control | result |
|---|---|
| Flux conservation Gamma + Refl = 1, s = 0 and s = -2 (independent of my constants), probes | to 1e-29 (30 digits), 1e-39 (40 digits) |
| Flux conservation on every production node, both spins (combined.json) | max residual 1.2e-35 |
| Low-frequency limit, s = 0, l = 0: Gamma/(16 M^2 omega^2), so sigma_abs -> 16 pi M^2 = horizon area | 1.0064 at omega = 1e-3, 1.00063 at 1e-4, 1.000063 at 1e-5 (goes to 1, linear in omega) |
| K_nu matching index r = 0 vs r = 1 (should be independent of r), 20 samples | max relative difference 5.5e-38 |
| Working precision 40 vs 55 digits, 20 samples (s = -1, -2; l up to 10; omega up to 1.75) | max relative difference 2.1e-36 |
| f_n series cutoff 10^-48 vs 10^-63 | max relative difference 7.4e-40 |
| Spin-1 constants by unitarity | C1 = 4, E1 = 1/16 exactly to 25 digits (clean rationals) |
| Quadrature rule A (12 nodes) vs B (16 nodes) | relative differences 2e-15 to 2.3e-14 (table below) |

A positive control against published Gamma or rate values was **not run**. I did not open Page's papers. The known-limit
control used is the l = 0 area limit.

## Results (rule B values; error = 3 x (|A - B| + tail bound), conservative)

| quantity | value (13 significant digits) | abs. error estimate | raw rule-B value |
|---|---|---|---|
| P_1 (photons) | 3.363854785578e-5 | 1.3e-18 | 0.000033638547855775436585 |
| P_2 (gravitons) | 3.836739924959e-6 | 8.9e-19 | 3.8367399249594510188e-6 |
| alpha = M^2 (P_1+P_2) | 3.747528778073e-5 | 2.2e-18 | 0.000037475287780734887604 |
| Sdot_1 | 0.001268365954077 | 9.8e-17 | 0.0012683659540774391119 |
| Sdot_2 | 0.0001300008786207 | 2.2e-17 | 0.00013000087862073855954 |
| beta | 1.484691691908 | 2.1e-13 | 1.484691691907989846 |
| t_page / t_decay | 0.5381024531598 | 6.0e-14 | 0.538102453159802019 |

**Digits I trust: 12 significant digits for every quantity; the 13th is very likely right.** The limiting error is the
quadrature (rule A vs rule B, up to 2.3e-14 relative for beta) plus the deliberately crude tail bound. The per-node
Gamma values are good to about 1e-35, so they are not the limit.

## Run times (this PC, python-flint 0.9.0, mpmath 1.3.0, Python 3.11, all under memcap 8 GB)

| run | time |
|---|---|
| photon main run (run_spin.py -1 40) | 229 s |
| graviton main run (run_spin.py -2 40), in parallel with the photon run | 170 s |
| controls.py | 13.8 s |
| unitarity_fit.py | 2.4 s |
| development probes in total | about 25-30 min |

Peak memory was 0.03 GB.

## Surprises / waypoints

1. **Spurious zeros.** The n = 0 nu equation has spurious exact zeros on lattice points, for example nu = 3/2 for
   s = 0, l = 2 at every eps. Plain continuation locks onto them and gives garbage; flux conservation exposed this. They
   are removed by deflation.
2. **nu wanders a lot for a = 0.**
   - For s = 0, l = 2: real nu goes 2 -> 1.5; collides and becomes 1.5 + iy; returns to the real axis at omega ~ 0.587;
     collides again at 1.0 and becomes 1 + iy; around omega ~ 1.333 it becomes 2 + iy, then 1.5 + iy.
   - The collision at omega ~ 1.3327 is extremely steep. Neither continuation in nu nor continuation in
     u = (nu - h)^2 passes it, which is why the method accepts any genuine root per node and substitutes panels.
3. **Spin-1 constants.** The constants fixed by unitarity came out as exact rationals (4 and 1/16), matching the spin-2
   pattern |c0|^2/(2 omega)^8 -> (l(l+1))^2/(2 omega)^4. This is a derivation by flux conservation, not a transcribed
   formula. A transcription-based cross-check (for example from Teukolsky-Press 1974) was not done.

## Files (<LAB>/blind-1/)

- Engine and runs:
  - mstf.py: production MST engine, flint ball arithmetic.
  - mst.py: earlier mpmath version, used only for early probes.
  - run_spin.py: main runs.
  - unitarity_fit.py: fixes the spin-1 constants.
  - controls.py: the controls.
  - combine.py and make_results.py: build the final numbers.
- Outputs: main_s1.json/.log, main_s2.json/.log, spin1_constants.json, controls.json/.log, combined.json, results.json.
- probe1-6.py: development probes.
- src_dl/: downloaded source (arXiv:gr-qc/0306120, PDF and LaTeX).
- No checkpoint/resume path exists, so resume_tested does not apply.
