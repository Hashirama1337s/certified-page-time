# REFEREE-HK1b: hostile referee on BAR-HK-1b (seal 2040a9985f), referee-1, 2026-11-17

Disclosure: this seat read the bar values (BAR-HK-1b, result_hk1b.json) before its own checks. Every check below is POST HOC and outside the sealed set; none of it changes the sealed verdict.

## In plain words
The certificate holds up. I read every bound in the engine and re-derived the ones that carry weight. Then I re-ran pieces of it from a copy and got byte-identical output. I also switched each error bound off on purpose: with the bound off the answer moved outside the honest box, and with it on the box still held the honest answer. Finally I recomputed the whole ledger with my own code and a different formulation (floating point, not certified). It agrees on beta to 1.7e-9, so 1.48469169 stands and Page's 1.48472 is excluded. Calling it "proved" still needs four things: the blind second implementation the bar itself requires, a written proof note (some lemmas exist only as code comments), one scorer fix, and more careful wording about Page.

## Verdicts
1. **Horizon Frobenius start and tail majorant: CORRECT.** For n >= N+1, |n+rho| <= n(1+u) and |n-4iw| >= n(1-4wmax/(N+1)), so b_j(n) <= beta_j uniformly. The induction |a_n| <= A zeta^n with sum beta_j zeta^-j <= 1 (checked in arb) is valid. The disk majorant needs |n-4iw| > 0, which holds because Re w >= w0/2 > 0. Teeth (T3, Nh=14): box [0.43622007 +/- 6.38e-9] contains the honest [0.43622007404747669307 +/- 5.08e-21]. With the tail switched off, the box excludes it.
2. **Transfer: CORRECT.** For complex q the log-norm bound |sigma^2-q|/(2 sigma) follows from the Hermitian part [[0, conj z],[z, -p]] with p > 0. Backward it is + sup p. The Cauchy/Gronwall factor is exp(4h sqrt(2Q+P^2)), and its 4^-(N+1)/(3/4) and sigma_c 4^-N/(3/4) tails are right. The disk stays at distance >= (a-2)/4 from the horizon. Midpoints are exact arb midpoints, and every rounding radius enters through crad. Floats only choose positions, N and sigma, and any sigma > 0 is valid. Teeth (T1, every N halved): [0.436220 +/- 5.66e-7] contains the honest value. With the tail off it excludes it.
3. **Far field: CORRECT** (conservative). I re-derived the Volterra equation with integrating factor e^{2iwr*}. It gives q = 2Cf/((M+2)R) + Cf KU/((M+1)M). The code carries an extra factor Cf on the second term, which is safe. The residual powers are complete (k >= M+2), and D >= lambda^2 r^2 for Zerilli. Teeth (T2, M=6): [0.4362201 +/- 7.62e-8] contains the honest value. With the remainder off it excludes it.
4. **Gamma = 1/|A_in|^2: CORRECT.** W_{r*}(u_-,u_+) = 2iw and W(u_+,u_-) = -2iw. |x0^rho| = 1 on the real axis. The RW/Zerilli potentials match the standard forms with M = 1. In PH4, Z and RW overlap and the flux box contains 0.
5. **Taylor models: CORRECT WITH FIXES.** B comes from a complex box that contains the disk, using the Frobenius majorant, the forward log-norm and e^{rho_w r*}. It is rigorous but loose: B = 2.2018e19, while the sampled |A_M| on the circle is 23.8. This is harmless because mu^64 = 5^-64 (about 1.8e-45). eta (Wronskian telescoping of horizon, step and far errors against the exact u_+) is correct and dominates rA, with rA = 9.09e-16 against an actual |A - P| <= 6.8e-20 at 5 exact dyadic points (teeth_t4b_out.json). Q encloses |P|^2, |A| >= 1 from flux, and Gamma/Gamma_P lies in [1-eG, 1+eG]. The degree-16 Lagrange remainder, 2h^{K+2}/(K+2), is right. The v2 point re-centring is exact algebra. Fix F1: the eta telescoping proof exists only in docstrings; write it down. Note: concavity of S gives |dS| <= eG S, so the extra 2 eG^2 N term is unnecessary (it is safe).
6. **Band bounds: CORRECT.** I re-derived the speed bound d|a|^2/dx = (V/w) Re(i conj(a) b e^{2iwx}), which gives |T'| <= V/(2w), and the shoulder integrals. The rotations E_a and E_b keep d(0, .), so the step d(0,N'y) >= l - d(0,y) is valid even though E_b^{-1} M E_a is not a conjugation. r^5 V' = -2Lr^2 + (6L-3c)r + 8c is verified. Fix F2: give a citation for the entrywise comparison of the y'' = Qy fundamental matrix; it is not cited.
7. **High-frequency tail and lemma: CORRECT WITH FIXES.** The Planck tails and S(n) = ln(1+n) + 8 pi w n are exact. V >= (L-3) f/r^2. Using sech^2 <= 4e^{-2T}, sqrt(L') >= l-1 and l-1 >= L_big gives K. int_0^inf w n = 1/384. The int_0^{w*} bound gives w*(2 ln 2 + 1). The ratio of the quadratic in Lg decreases (b^2 > a). I reconstructed the far-cell extension: cells [r_b0 rho^j, r_b0 rho^{j+1}] each add >= 2 sqrt(L') s_far - 2 ln 2 >= 0 (slope_ok), the right shoulder is <= rho/(wt_min r_b0), and the left edge moves to 2 + 9wt^2 (premises checked). It is correct, but the proof exists only in code. Fix F3: write it down. Fix F4: control C9 always prints PASS, so it cannot fail (doctrine #20).
8. **Entropy integrand: CORRECT.** On panels N > 0 and the two terms do not cancel. The band bounds use S increasing and n decreasing. Underflow would only widen a ball or force a fallback.
9. **Skip and fallbacks: CORRECT WITH FIXES.** The ledger has 321 TM panels, 1 skip (s=1 l=9 panel 6, G <= 2.546e-17, IP [+/- 4.48e-23]) and 0 fallbacks. The fallback widths are 0 for both spins. The thresholds were pinned in the instrument hash before main (3aa86d51...). They were set after BAR-HK-1b was sealed, in no sealed amendment, and `within_budget` does not feed any PH outcome. This is immaterial here. Fix F5: put thresholds and budgets in the bar or an amendment.
10. **Propagation and exclusion: CORRECT WITH FIXES.** Re-assembly from the result rows is identical (repro_out.json). The upper end of beta is 1.48469169197808, which is 1.33080e-5 below 1.484705, so the disjointness is real. **Scorer deviation:** ph1() tested overlap with the point values 1.48472 and 1.48471, not with the rounding intervals that AMEND-HK-1-1 specifies. Re-scored POST HOC with [1.484715, 1.484725] and [1.484705, 1.484715]: both are disjoint and PH1 still passes. Fix F6.

## Reproducibility, wrong inputs, independent value (POST HOC)
- The copy in work/repro has instrument sha256 3aa86d51883dfa38af5c0ca84d3d3ddf1479ea79bdc2d2ea9f905191a01ff6fb, equal to the result's. Channels (2,7) and (1,9), panels (1,1,k=10) and (2,2,k=0), and tails l=10 for s=1 and s=2 all reproduce byte-identical strings.
- Wrong physics (T5): Gamma for s=1 l=2 at w=0.37 is [0.043310015777461781212 +/- 6.00e-22]. With the s=2 potential it becomes [0.43622007404747669307 +/- 5.08e-21], which is disjoint.
- Independent float engine: integrated in y = ln(r-2) with phi = dpsi/dr*, with my own far recurrence and Gauss-Legendre quadrature. Per-mode difference from the certified value: s=1 l=1 P -1.38e-12 and S -1.28e-9 (the S gap is the residual cut at w < 1e-3, about 1.5e-12); s=2 l=2 P 1.15e-13 and S -7.1e-12. Float beta is 1.4846916902, which is -1.68e-9 from the certified midpoint. Float Page time is 0.5381024535. This check was not certified and not blind.

## Framing (overclaiming risk)
- Page 2013 (local text, papers/page2013.txt l.140-143) says: "My numerical calculations (with an estimated accuracy of about four or five digits; not all of the digits given below may be significant ...)". So the result settles digits that Page flagged as uncertain. It does not correct an error, and "their 5th-6th digits were off" should be reworded.
- POST HOC: the certified alpha also excludes Page's printed 0.000037474, and the same holds for P_1 = 0.000033638 and P_2 = 0.000003836. Page's figures sit -1.63e-5 and -1.93e-4 (relative) below ours, which accounts for his higher beta. This was not sealed; report it as an observation.
- PH3 is a weak positive control, because Newton's box is about 1% wide. PH6 is also weak, because the s=1 potential misses by a factor of about 5.7.

## Required fixes
F1 write the eta/Wronskian proof; F2 cite the comparison theorem; F3 write the far-cell lemma; F4 make C9 able to fail; F5 seal the skip/budget rules and wire the budget into the verdict; F6 fix ph1() to test rounding intervals; F7 reword the Page claim and declare the trust base (python-flint 0.9.0 / Arb).

## What blocks "proved"
Nothing found so far contradicts the HOLD. Four things block "proved": (a) the blind second implementation that BAR-HK-1b itself requires (mine is not blind and not certified); (b) the written proof note (F1-F3); (c) the scorer fix F6; (d) the Page wording and trust-base statement F7. **Next strike:** a blind certified replicator built from a written spec, using a different formulation (r*-domain transfer, or a Riccati/phase method with a different quadrature), with a target of beta to 1e-9.

Files (work = <LAB>/seats/referee-1/work), sha256:
- indep_float.py 4d40fecfd96856c4016bc3a7baf25135130324b78182d993526e44ba7ee69d63
- run_indep.py 361692055a595cf86eca397940da0d8c84ec1ae0267204332f89bb999fe0e6ae
- indep_float_out.json 5f5ef03bfef51ba5b6efefae248887c8c8f2d76d304ab013edef6161e6d47eca
- indep_float_run.log 319fc41bbd866e48955128edbc9bc416cce82b2aaae3ce97804c67236e8083fd
- compare.py faca6eb4a08fdeec0a690883d944c746e068ed4936895aa423aace21b90416d0
- compare_out.json 7f3a5a9dc15db424f0d8cba6e8d2eeb70d28f41dadff11577b693964f4a8d444
- compare2.py fdc6e0f77bbf594006317fb8ca5fe327f12f29ca88ddcd7d530eb614af85be4b
- compare2_out.json f332153aa989ef2542df370143e9e395c76159a0a7dab84a3f53dce60532a853
- repro_check.py bf2b8d8913d416560e3dee23ffdd093ccbd2fa0e3be6800ea77bd45b12f1716c
- repro_out.json 6f9b1c2feefc8ad5c3cdbbc9ada232a527060ad9b859483bbc4fc9f98c8d1c33
- teeth.py d0aa15092aa49b823b8b66dbbd081a0f30f9108ed11952be31b3c887875e4527
- teeth_out.json a37bf0b79425c97839ba9e2c0f2ebc8af53d966ec828a050486a22627bbf433c
- teeth_t4b.py 987ea616a97e3b5158a6afc6d0632b22f87c6b0eb4aec53eabb8375684403ef9
- teeth_t4b_out.json ff3631771f2b09f6a0debc72c20fb8b74a65679f6a1b2a98ee6a82fabc729a6f
