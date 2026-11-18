# REFEREE-HK1b-2: final hostile pass on the fix set F1-F7, referee-1, 2026-11-17

Inputs (sha256):
- PROOF-HK.md 917a9cabfc31d3b777ae63c645989d25b8c47fa3af3e98a1d8673daa2296cbc6
- rescore_hk1b.py 6ff52b73c5d7b8da7032c3680af6e8de5c8e8cdb26bc8cfb93e5f63f131000c6
- rescore_hk1b.json 485d9e4967b963e30962e4e87338d41383d99606623159b01a13fd86bcb27cf5
- c9_teeth_hk1b.py f591b8e63f9ae4d0793c0b7c6fa03026ab84f82355648a93a363fc07774fee29
- c9_teeth_hk1b.json 208285b8c0c9ab9a5df877629c1373f09caa5f29ffb16d48e176329827ec304e

All checks here are POST HOC. My one new run is work/lemma_edge.py (2cea3323…) → lemma_edge_out.json (9d305429…), run under memcap and using the instrument copy.

## In plain words
The written note matches the mathematics I checked in round 1. The new comparison proof (F2) is right as written. The far-cell lemma (F3) has one written step that does not follow. The code's bound is still valid, and the numbers clear it by a factor of 2. That needs a one-sentence repair, not a rerun. The re-scorer is right. The C9 control now has real but weak teeth. The trust base and the Page wording are right. After the §8 sentence is fixed, nothing I know of blocks "PROVED (computer-assisted, refereed, blind-replicated)". I did not check the blind replication myself.

## Verdicts
1. **§0-§5 (F1: horizon, transfer, far field, eta, Taylor model): CORRECT.**
   - The statements match my round-1 derivations.
   - The far-field error equation (E g)' = E F/f with F = -f'g + Ue - Res is right. The constant q = 2C_f/((M+2)R) + C_f K_U/((M+1)M) is right, and the code's C_f² is correctly called conservative.
   - The RW recurrence 2iw m c_m = [(m-1)m - L]c_{m-1} - 2((m-1)² - s²)c_{m-2} equals my independent one.
   - The eta telescoping identity and its three terms are right.
   - The S-error chain needs -ln(1-e_G) <= 2e_G. That holds because e_G < 0.5, which the code enforces.
   - Cosmetic: §3 uses "F" both for a function and for a constant.

2. **§6 band bounds: CORRECT WITH FIXES (cosmetic).**
   - §6(i) prints d|a|²/dx = -(V/w)Re(i ā b e^{2iwx}). The correct sign is +, as in the hkbounds docstring and in my derivation. Only the modulus is used, so no bound changes.
   - The su(1,1) generator, N' = E_b M E_a^{-1} and the triangle step are right.

3. **§7 (F2) comparison proof: CORRECT as written.**
   - Picard iterates of A_q >= 0 from N^{(0)} = I stay >= 0 for x >= x_0.
   - D' = A_Q D + (A_Q - A_q)N_q holds, and variation of constants with the propagator N_Q(x,s) >= 0 (step 1 from s) gives D >= 0.
   - Products are monotone for nonnegative factors.
   - Hypotheses used: Q >= q >= 0, forward direction, piecewise continuous coefficients. All three hold on the cells.

4. **§8 (F3) l > 60 lemma: CORRECT WITH FIXES.**
   - The band part, the far cells (U >= f0/(r_b0² ρ^{2j+2}), w̃² <= w̃_min² ρ^{-2(j+1)}, h_j >= Δr, s_far), the right shoulder ρ/(w̃_min r_b0), the slope argument and the summation are all right.
   - Minor: arccosh(tr/2) >= ln Π cosh needs both diagonal entries, not only (ΠC)_11. Both hold.
   - **Gap in the written left-edge step:** the note sets r_a(J) = 2 + 9 w̃_hi(J)² and gets the shoulder <= (9/4) ρ w̃_hi. It then claims this is <= max(ρ IL0/w̃_min, (9/4) w̃_min) = NT, which does not follow, because (9/4)ρw̃_min > (9/4)w̃_min. Also, for J = 0, 9w̃_min² <= r_a0 - 2 is not among the stated checks.
   - The code's NT is still valid, on either of two grounds:
     - (a) The comparison is pointwise in w, so the cells may depend on w̃. Take r_a = r_a0 for w̃ in (w̃_min/ρ, w̃_min], which gives shoulder <= ρ IL0/w̃_min. Take r_a = 2 + 9w̃² for w̃ <= w̃_min/ρ, which gives shoulder <= (9/4)w̃ <= (9/4)w̃_min. That is exactly the code's max.
     - (b) Numerically, ρ IL0/w̃_min = [0.181313 +/- 4.14e-7], which is at least (9/4)ρw̃_min = 0.0900. Also 9w̃_min² <= r_a0 - 2 = [0.00727890 +/- 1.44e-9] holds.
   - **Fix G1:** replace the left-edge sentence with (a). This is documentation only: no number and no code change.

5. **rescore_hk1b (F6): CORRECT.**
   - It reads only result_hk1b.json (sha256 cecd313a…) and applies the AMEND-HK-1-1 intervals.
   - Folding the decimal-parse radius into the interval makes the disjointness test stricter, which is safe.
   - Results: PH1-PH3 PASS, PH4-PH6 copied, changed = []. The gaps are 1.33081e-5 to [1.484705, 1.484715] and 2.33081e-5 to Page's interval.
   - Note: rescore widths, e.g. beta 1.052e-10, come from the printed (inflated) radii and are larger than the in-memory 8.82e-11. Both are far below 1e-8. Quote the printed ± 7.81e-11 as the headline, which is conservative.

6. **c9_teeth_hk1b (F4): CORRECT WITH FIXES.**
   - A and C are real.
   - D does show that check B can fail, but only against a gross falsification. The samples sit 70-255 orders below eps; the largest is Γ = 2.11063e-92 at s=1, l=61, w=6. So B catches a falsified Gs only if Gs is inflated by more than about 2.07× (4e^{-x·60} < 2.1e-92 needs x > 3.54). A 10-50% error in Gs would pass B unnoticed.
   - B is a sampled soundness check, not proof. The proof is §8.
   - **Fix G2:** label C9-B/D in the note as "low-power soundness sample (detects lemma errors > ~2× in the exponent)". This does not block, because §8 carries the claim and the whole l > 60 tail is P <= 2.06e-20, S <= 1.75e-15 per spin.

7. **§10 (F5) constants table: CORRECT.** It matches the code, and it honestly states that within_budget is not wired into the verdict.

8. **§12 (F7) trust base and Page wording: CORRECT.**
   - The trust list is complete for this computation: Arb via python-flint 0.9.0, CPython 3.11.9, sympy only for checks, and unformalised written proofs.
   - The Page quotes check out against the local text. At l.140-144 Page estimates "about four or five digits". At l.219-221: "the last one or two digits probably are not significant but are given as a challenge for someone to do a higher-precision calculation to find the error".
   - The wording "settles his flagged-uncertain last digits", not "wrong", is right.
   - Remaining: LOG.md 17:45 still says "their 5th-6th digits were off". That is history and may stand, but no release text may copy it.

## Does anything block "PROVED (computer-assisted, refereed, blind-replicated)"?
Only G1, the one-sentence §8 repair, which is documentation. G2 and the two cosmetic items should be fixed but do not block. "Blind-replicated" rests on the lead's LOG entry at 18:28 (blind-1, Teukolsky + MST: beta 1.484691691908 +/- 2.1e-13, overlapping all 7 enclosures). I have NOT CHECKED that seat's files. Once G1 is applied, I have no objection to the status.
