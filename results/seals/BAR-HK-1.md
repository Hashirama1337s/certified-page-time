# BAR-HK-1: certified Page evaporation constants of a Schwarzschild black hole (photons + gravitons into empty space)

Written 2026-11-17 by the lead, before any certified code exists. Scope: SCOPE.md (narrowed after seats/gate-1/GATE-HAWKING.md).
Disclosed calibration: the recon computing seat's floating-point values (<RECON>/seats/COMPUTING.md;
140-200-bit floats, two quadratures agreeing to 2.3e-24, six controls; NOT certified) are the source of the predicted values
below. Newton's certified graviton enclosure (Zenodo 10.5281/zenodo.22800587, Theorem 3) is credited prior work.

**Object.** Schwarzschild, M = 1, Planck units. Greybody factors Gamma_{s,l}(w) from the Regge-Wheeler equation (s = 1, 2)
with |A_in|^2 - |A_out|^2 = 1. Page's definitions (Page 2013 arXiv:1301.4995; Page 2005 eq. (18)):
P_s = sum_l 2(2l+1)/(2 pi) int w Gamma n dw, n = 1/(e^{8 pi w} - 1); alpha = P_1 + P_2;
Sdot_s = sum_l 2(2l+1)/(2 pi) int [(1+N)ln(1+N) - N ln N] dw, N = Gamma n; beta = (Sdot_1 + Sdot_2)/(8 pi alpha);
Page time t_*/t_decay = 1 - (beta/(beta+1))^(3/2).

**What is new.** PH1, PH2 (photon power, entropy rates, beta, Page time: certified for the first time per the gate). PH3 is a
positive control against prior certified work; PH4, PH5 are controls; PH6 is a null.

instruments: build-1/

## Predictions
- **PH1 (beta).** A certified enclosure of beta of relative width <= 1e-8 that contains 1.4846916919 (recon float) and
  therefore excludes both printed values 1.48472 (Page 2013) and 1.48471 (Perez-Gonzalez 2025).
- **PH2 (the rest of the ledger).** Certified enclosures of relative width <= 1e-8 for P_1, alpha, Sdot_1, Sdot_2 and the Page
  time t_*/t_decay, containing respectively 3.3638547856e-5, 3.7475287781e-5, 1.2683659541e-3, 1.3000087862e-4 and
  0.5381024532 (recon floats, rounded to 11 significant digits).
- **PH3 (positive control vs prior certified work).** The certified graviton power P_2 lies inside Newton's enclosure
  [3.8262e-6, 3.8639e-6] and has relative width <= 1e-8, containing 3.8367399250e-6.
- **PH4 (formulation control).** Certified graviton greybody factors from the even-parity (Zerilli) equation overlap the
  Regge-Wheeler ones at l = 2, 3 and M w = 0.05, 0.2, 0.37, 0.6, 1.0 (Chandrasekhar duality).
- **PH5 (closed-form control).** For the l = 0 scalar (s = 0), Gamma_0/(16 w^2) is certified within 1e-2 of 1 at M w = 1e-3 and
  within 1e-5 at M w = 1e-6 (absorption cross section -> horizon area).
- **PH6 (null, teeth).** Computing the graviton power with the s = 1 potential in place of s = 2 gives a certified P_2 enclosure
  disjoint from Newton's interval.

## Kill conditions
- An enclosure that excludes the recon float value for any of PH1-PH3: FAILED for that item; the recon numbers are wrong, which
  is a finding (recorded, not hidden), and no Page-time claim is made until a blind second implementation settles it.
- An enclosure wider than the stated width: FAILED for that item (the method is not yet tight enough).
- Any single run over 30 minutes without a 2-minute probe; total main run over 3 hours (an evening run): stop, INCONCLUSIVE.

## Verdict
HOLD if PH1-PH6 all hold. The claim on HOLD: certified photon power, entropy rates, beta and Page time of a Schwarzschild
black hole radiating photons and gravitons (graviton power certified independently of, and inside, Newton 2026); to be
refereed and blind-replicated before it reaches [the lab owner; name redacted] as proved.

## Seal fields
- formula_ref: <RECON>/seats/computing/papers/page2013.txt:200-215
- calibrated_on: none - no certified run exists; predicted values are the recon seat's floats (disclosed above), not tuned thresholds
- depends_on: none - first test of this project
- null_not_symmetry: PH6 changes the spin weight in the potential, which changes the physical greybody factors; it is not a relabelling
- target_form: arb enclosures with relative width bounds; closed-form propagation to beta and the Page time in interval arithmetic
- parameters: s = 1, 2 (and s = 0 control); width cap 1e-8; PH4 frequencies M w = 0.05, 0.2, 0.37, 0.6, 1.0
- tolerances: interval arithmetic (arb); overlap tests for PH3-PH4
- ceiling: the first certified Page constants of a real black hole (reference table; no new law)
- positive control: PH3 (prior certified graviton power), PH5 (closed-form low-frequency limit)
- toy_model: s = 0 scalar low-frequency limit (PH5)
- files: BAR-HK-1.md
- command: the build seat's own (build-1/RUN.md), under memcap 8
