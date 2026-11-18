# Certified Page evaporation constants for a Schwarzschild black hole emitting photons and gravitons: the entropy ratio β and the Page time

**Moki & Julio**

Version 1.0, 2026. Every number below is traced to a shipped result file in `CLAIMS.md`. Balls are printed as
`[mid ± rad]` exactly as the certifying program stored them.

---

## Abstract

Page's model of an evaporating Schwarzschild black hole that emits only massless photons and gravitons into empty space
is fixed by two constants: the total power α = M²(P₁ + P₂) and the ratio β of the coarse-grained entropy production of
the radiation to the loss of Bekenstein-Hawking entropy. β fixes the Page time, t*/t_decay = 1 − (β/(1 + β))^{3/2}. Page
(2013) gave β = 1.48472 and stated an accuracy of about four or five digits. Using ball arithmetic (Arb), with rigorous
bounds on every truncation of the Regge-Wheeler scattering problem, on all multipoles and on all frequencies, we prove
β ∈ [1.4846916919 ± 7.81e-11] and t*/t_decay ∈ [0.5381024532 ± 8.99e-11], together with enclosures of the photon power
M²P₁ ∈ [3.3638547856e-5 ± 2.57e-16], α ∈ [3.747528778e-5 ± 1.96e-15] and the photon and graviton entropy rates
M·Ṡ₁ ∈ [1.2683659541e-3 ± 2.47e-14], M·Ṡ₂ ∈ [1.300008786e-4 ± 5.55e-14]. To our knowledge (search of arXiv, INSPIRE and
Zenodo to 17 November 2026) these are the first certified enclosures of these quantities. The graviton power, and so
the graviton part of α, was certified earlier by Newton (2026) to 1% width; our independent enclosure M²P₂ ∈ [3.836739925e-6 ± 6.95e-16] lies inside
his interval and is about 2.7 × 10⁷ times narrower. The certified β lies outside the rounding intervals of the published
floating-point values 1.48472 and 1.48471, settling the digits Page flagged as uncertain. The result was obtained in a
sealed (pre-registered) test after one sealed failure, refereed twice by an internal hostile referee seat, and
replicated blind by an independent formulation (Teukolsky equation, Mano-Suzuki-Takasugi series; not rigorous).

## 1. Results

**Theorem (computer-assisted).** Let a Schwarzschild black hole of mass M (G = c = ħ = k_B = 1, M = 1 below) radiate
photons (s = 1) and gravitons (s = 2) into empty space, with greybody factors Γ_{s,l}(ω) from the Regge-Wheeler
equation normalised by |A_in|² − |A_out|² = 1, and with Page's definitions

- P_s = Σ_l 2(2l+1)/(2π) ∫₀^∞ ω Γ_{s,l} n dω, n = 1/(e^{8πω} − 1);
- Ṡ_s = Σ_l 2(2l+1)/(2π) ∫₀^∞ [(1+N) ln(1+N) − N ln N] dω, N = Γ_{s,l} n;
- α = P₁ + P₂, β = (Ṡ₁ + Ṡ₂)/(8πα), t*/t_decay = 1 − (β/(1+β))^{3/2}.

Then

| quantity | certified enclosure | relative width |
|---|---|---|
| β | [1.4846916919 ± 7.81e-11] | ≤ 1.1e-10 |
| t*/t_decay (Page time) | [0.5381024532 ± 8.99e-11] | ≤ 3.4e-10 |
| M²P₁ (photons) | [3.3638547856e-5 ± 2.57e-16] | ≤ 1.6e-11 |
| M²P₂ (gravitons) | [3.836739925e-6 ± 6.95e-16] | ≤ 3.7e-10 |
| α = M²(P₁ + P₂) | [3.747528778e-5 ± 1.96e-15] | ≤ 1.1e-10 |
| M·Ṡ₁ (photons) | [1.2683659541e-3 ± 2.47e-14] | ≤ 3.9e-11 |
| M·Ṡ₂ (gravitons) | [1.300008786e-4 ± 5.55e-14] | ≤ 8.6e-10 |

The same run encloses the other closed forms of Page's model: M*/M₀ = (β/(1+β))^{1/2} ∈ [0.7730042563 ± 3.34e-11];
S*/S_BH(0) = β/(1+β) ∈ [0.5975355803 ± 7.48e-11]; t_decay = M₀³/(3α) ∈ [8894.750463 ± 4.34e-7] M₀³; the photon-only and
graviton-only ratios Ṡ_s/(8πP_s) ∈ [1.5002632702 ± 4.36e-11] and [1.348168161 ± 5.82e-10]. These were computed in the
sealed run but were not sealed predictions.

**Status.** Computer-assisted proof. The written proof (proofs/PROOF.md) was checked in two rounds by an internal hostile
referee seat (Section 4.3; not external peer review). An independent blind implementation agrees on all seven quantities
(Section 4.4).

## 2. Background and conventions

Page's model (Page 1976; Page 2013) treats a black hole heavy enough that only massless particles are emitted. Page argues
that photons and gravitons are then the only relevant species; Perez-Gonzalez (2025) places the end of neutrino emission
at about 10²⁶ g for a lightest neutrino mass of 0.01 eV. While only these two species are emitted, α and β do not depend on
the mass, so dM/dt = −α/M², M(t) = M₀(1 − t/t_decay)^{1/3} with t_decay = M₀³/(3α), and the Bekenstein-Hawking entropy
S_BH = 4πM² falls as (1 − t/t_decay)^{2/3}. The coarse-grained radiation entropy rises as β(S_BH(0) − S_BH(t)). The Page
time is when the two are equal: S_BH/S_BH(0) = β/(1 + β), which gives the formula above.

Page (2013, the paragraph before Eq. (1)) states an estimated accuracy of "about four or five digits" for his
emission rates and prints β = 1.48472 (the sentence after Eq. (2)), giving its last digits "as a challenge for someone to do a higher-precision
calculation". Perez-Gonzalez (2025) recomputed β in floating point as 1.48471.

The wave equation is ψ'' + (ω² − V)ψ = 0 in the tortoise coordinate x = r + 2 ln(r/2 − 1), with
V = (1 − 2/r)(L/r² + c/r³), L = l(l+1), c = 2(1 − s²).

## 3. Method

The full argument, with every bound and its code location, is proofs/PROOF.md; the summary:

1. **Horizon start (PROOF §1).** The ingoing solution is a Frobenius series in r − 2; a geometric majorant of the
   recurrence, proved by induction, bounds its tail uniformly on complex frequency disks.
2. **Transfer (§2).** Exact dyadic Taylor steps; truncation bounded by Cauchy's estimate on a disk with a Gronwall bound;
   growth on the real segment bounded by a logarithmic norm, so oscillation costs nothing. The state is kept at exact
   midpoints and the error is carried separately.
3. **Far field (§3).** u₊ = e^{iωr*}h with h an asymptotic series; the remainder solves a Volterra equation and is bounded
   by a contraction with an explicit constant (the code's constant is larger than needed, which is safe).
4. **Total error in A (§4).** A Wronskian-telescoping identity sums the horizon, step and far errors into one bound η.
5. **Frequency panels (§5).** On 321 panels A(ω) is a degree-64 Taylor model with a Cauchy remainder plus η; Γ, the power
   integrand and the entropy integrand are integrated by degree-16 local expansions with Lagrange remainders. The
   polynomial |P|² is re-centred exactly at each sub-interval before the ball step (the fix that turned the failed first
   attempt into the held second, Section 4.1).
6. **Band bounds (§6-7).** Where Γ is tiny, a hyperbolic transfer-matrix argument gives Γ ≤ sech² T with T bounded below
   by constant comparison cells; the comparison theorem for y'' = Qy with Q ≥ q ≥ 0 is proved in §7.
7. **All l > 60 at once (§8)** by a lemma with far cells, and Planck tails above the frequency cut-off (§9).
8. **Propagation.** α, β and the Page time follow in interval arithmetic.

The run used 17 Taylor-model channels (s = 1, l = 1..9; s = 2, l = 2..9), 322 panels (321 with a Taylor model, 1
discarded by a certified absolute bound), 0 fallbacks, per-l band bounds for 10 ≤ l ≤ 60 and the lemma beyond; it took 785 s on one core.

## 4. Sealed tests and verification

All test files are shipped in `results/`; seal identifiers are listed in SCORECARD.md and CLAIMS.md.

### 4.1 The failed first attempt

The first sealed test (results/seals/BAR-HK-1.md) made six predictions: (PH1) a β enclosure of relative width ≤ 1e-8
excluding both printed values; (PH2) enclosures of P₁, α, Ṡ₁, Ṡ₂ and the Page time; (PH3) a graviton power inside
Newton's certified interval; (PH4) Regge-Wheeler and Zerilli greybody factors overlapping at ten points; (PH5) the
low-frequency limit of the l = 0 scalar; (PH6) a null: the graviton sum with the spin-1 potential must miss Newton's
interval. The predicted values were floating-point values from an earlier reconnaissance computation, disclosed in the
bar. An amendment sealed before the run (results/seals/AMEND-HK-1-1.md) fixed how a predicted value printed to n digits is
compared with an enclosure: overlap with its rounding interval; exclusion means disjointness.

PH4 and PH5 passed. PH1-PH3 and PH6 were INCONCLUSIVE: in the channel s = 1, l = 8 one quadrature sub-interval could not be
closed at the depth limit, because the ball evaluation of |P|² on a shifted interval contained 0 (the value falls about
10⁴-fold across a panel there). The bar gives no claim in that case, so the test was scored FAILED as sealed
(results/hk1/).

### 4.2 The held re-test

The second sealed test (results/seals/BAR-HK-1b.md) repeated the same predictions and disclosed what the failed run had
shown. Its instrument re-centres the polynomial exactly before the ball step, discards a panel only when a certified bound
is below a fixed absolute threshold, and falls back to a rigorous crude bound for any piece that fails (none did). All six
predictions passed (results/hk1b/result_hk1b.json). PH4: Regge-Wheeler and Zerilli overlap at all ten points. PH5:
Γ₀/(16ω²) − 1 ∈ [0.006399818824 ± 2.01e-13] at Mω = 10⁻³. PH6: the spin-1 potential gives [6.77474891e-7 ± 5.81e-16],
disjoint from Newton's interval.

### 4.3 Referee rounds

An internal hostile referee seat (results/referee/REFEREE-HK1b.md) re-derived every bound that carries weight, switched
each error bound off to confirm that the box then misses an honest value, reproduced parts of the run byte for byte, and
recomputed all seven quantities in floating point with its own formulation (β agrees to 1.7e-9). It required seven fixes: a written
proof note, a self-contained comparison theorem, the large-l far-cell lemma written out, a control that can fail,
explicit skip and fallback constants, a scorer that tests rounding intervals (the sealed scorer tested the printed points;
the re-score with intervals still passes, results/hk1b/rescore_hk1b.json), and careful wording. A second round
(REFEREE-HK1b-2.md) found the fixes correct and one sentence of the far-cell lemma that did not follow as written; the
repaired argument is annotated in proofs/PROOF.md (no number or code changed). Both rounds are after the sealed run and
change no sealed outcome.

### 4.4 Blind replication

A separate seat, without access to our code, numbers or bars, solved the Teukolsky radial equation (s = −1, −2) by the
Mano-Suzuki-Takasugi series (Sasaki and Tagoshi 2003) with Gauss-Legendre quadrature, fixing the photon normalisation by
flux conservation. Its values are high-precision estimates with a convergence study, not enclosures; it disclosed a
rough recollection of β ≈ 1.4847, t* ≈ 0.538 t_decay and α ≈ 3.747e-5 from general knowledge (results/blind/BLIND-REPORT.md). Its code and outputs are
shipped in results/blind/code/ and can be re-run (tools/reproduce.py --tier blind). All seven values lie inside our
boxes; the midpoints differ by 5.4e-12 (β) to 1.6e-10 (Ṡ₂) relative (results/derived.json).

## 5. Comparison with printed values

- **β.** The certified upper end lies more than 1.33 × 10⁻⁵ below the rounding interval of 1.48471 (Perez-Gonzalez 2025) <!-- numcheck: ignore (a cited printed value, not a bound) -->
  and more than 2.33 × 10⁻⁵ below that of 1.48472 (Page 2013), about 9 and 16 parts per million; the printed values themselves lie about 12 and
  19 ppm above the certified β. Both are floating-point
  values; Page states four to five reliable digits. This settles the digits he flagged as uncertain.
- **Powers (POST HOC observation, not sealed).** Page's printed photon and graviton powers, 0.000033638 and 0.000003836, sit
  1.6 × 10⁻⁵ and 1.9 × 10⁻⁴ (relative) below our enclosures, and their rounding intervals are disjoint from them. A slightly
  low total power is consistent with a slightly high β; we did not test the cause.
- **Graviton power.** Our P₂ lies inside Newton's certified [3.8262e-6, 3.8639e-6].

## 6. Limitations (what we do not claim)

Only Page's model: non-rotating, uncharged, photons and gravitons, empty space, no massive species and no neutrinos; only
the Regge-Wheeler greybody factors of spins 1 and 2. The Page time is Page's closed-form definition; nothing is claimed
about whether or how information leaves a black hole. The proofs are refereed by internal seats but not machine-checked;
the trust base is Arb through python-flint 0.9.0 and CPython 3.11 (proofs/PROOF.md §12). The blind agreement, the re-score
and the comparison of Page's printed powers were done after the sealed run.

## 7. Related work and credit

Page (1976) computed the emission rates of photons and gravitons from a Schwarzschild black hole; Page (2013) gave β and
the time dependence of the radiation entropy in this model, and invited the higher-precision recomputation done
here. Perez-Gonzalez (2025) recomputed β in floating point, including other species and masses. Newton (2026) gave the
first certified Schwarzschild graviton luminosity, with ball arithmetic, transfer-matrix comparison cells and a sech²
bound on tiny transmission factors (his Eqs. (35)-(38)); our band bounds follow that idea, with our own proofs and code.
Boonserm and Visser (2008) gave rigorous one-sided bounds on greybody factors of a related form. Calza and Spina (2026)
compare numerical greybody methods at about four-digit accuracy. Our two dated prior-art searches (17 November
2026: arXiv, INSPIRE, Zenodo, with query logs) are shipped in results/prior-art/. A floating-point re-verification of the scalar case
appeared while this work was being prepared (Lee 2026); it does not treat photons or gravitons.

## 8. Open doors

- **Spinning black holes.** Certified emission constants and Page time for Kerr black holes. Newton names Kerr rotation as
  the next step of his certified graviton work. Our engine and the Teukolsky route of the blind check are starting points.
- **Neutrinos and lighter black holes.** Below about 10²⁶ g neutrinos are emitted and β changes (Perez-Gonzalez 2025:
  1.61862 with neutrinos, float). Our engine treats integer spins only; the panel quadrature carries over; for spin-1/2 the wave equation, the thermal factor (Fermi-Dirac), the entropy function and the tail bounds all change. Untested.
- **Machine-checking the finite inequalities** of the large-l and comparison steps (proofs/PROOF.md §7-8, §10) in a proof
  assistant. Untested.

## References

- D. N. Page, Phys. Rev. D 13, 198 (1976), doi:10.1103/PhysRevD.13.198.
- D. N. Page, arXiv:hep-th/0409024 (2004), Eqs. (13), (16)-(17) (definitions of the rates).
- D. N. Page, "Time Dependence of Hawking Radiation Entropy", arXiv:1301.4995v3 (2013), Eq. (2) and the paragraphs around it.
- Y. F. Perez-Gonzalez, "Page Time of Primordial Black Holes in the Standard Model and Beyond", arXiv:2502.04430v3 (2025), Eq. (18) and the text after it.
- T. Newton, "Proof-Carrying Schwarzschild Hawking Spectroscopy: Certified QNM Isolation and a Sub-1% Graviton Luminosity Enclosure", Zenodo (2026-09-16), doi:10.5281/zenodo.22800587, Theorem 3 (Eq. (47)), Eqs. (35)-(38).
- P. Boonserm and M. Visser, arXiv:0806.2209 (2008).
- M. Sasaki and H. Tagoshi, Living Rev. Relativ. 6 (2003) 6, arXiv:gr-qc/0306120.
- M. Calzà and A. Spina, "Gray-body factors: Method matters II, WKB vs GrayHawk", arXiv:2611.15889 (2026).
- Lee, "Independent Numerical Reverification of Schwarzschild Hawking Radiation Using the EV424 π Reference", Zenodo (2026-11-17), doi:10.5281/zenodo.24319221.
- F. Johansson, Arb ball arithmetic library, used through python-flint 0.9.0.

---

*Prepared with AI assistance; what was checked, and by what, is stated above.*
