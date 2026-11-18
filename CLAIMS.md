# CLAIMS: every claim with its status, and every number with its source

Status labels: **CERTIFIED** = computer-assisted enclosure (outward ball arithmetic) from a sealed run; **PROVED** =
written proof checked by at least one internal hostile referee seat; **CITED** = taken from an opened source (locator in
paper.md, References); **PROBE** = numerical value without an enclosure; **OBSERVATION** = a remark on a printed value
whose cause we did not test; **NOT CLAIMED**. Seal ids are the lab ledger's claim hashes (results/ledger-hawking.json).
Referee seats are named by their report file in results/referee/.

## Claims

| # | Claim (paper section) | Status | Seals | Referee seats, blind seats | Novelty gate (prior-art searches of 17 November 2026: results/prior-art/) |
|---|---|---|---|---|---|
| C1 | β ∈ [1.4846916919 ± 7.81e-11] (§1) | CERTIFIED (PH1 PASS), PROVED (proofs/PROOF.md) | 2040a9985f (+ 48cf09638b) | REFEREE-HK1b, REFEREE-HK1b-2 (all points CORRECT / CORRECT WITH FIXES; fixes applied); blind seat: inside the box | OPEN: no certified β found; "first" only with "to our knowledge" and the date |
| C2 | Page time t*/t_decay ∈ [0.5381024532 ± 8.99e-11] (§1) | CERTIFIED (PH2), PROVED | 2040a9985f | as C1; blind inside | OPEN, as C1 |
| C3 | M²P₁ ∈ [3.3638547856e-5 ± 2.57e-16], α ∈ [3.747528778e-5 ± 1.96e-15], M·Ṡ₁ ∈ [1.2683659541e-3 ± 2.47e-14], M·Ṡ₂ ∈ [1.300008786e-4 ± 5.55e-14] (§1) | CERTIFIED (PH2), PROVED | 2040a9985f | as C1; blind inside for all four | OPEN (photon power, both entropy rates); α OPEN as a total, its graviton part certified earlier by Newton at 1% width |
| C4 | M²P₂ ∈ [3.836739925e-6 ± 6.95e-16], inside Newton's certified [3.8262e-6, 3.8639e-6] (§1, §5) | CERTIFIED (PH3), PROVED | 2040a9985f | as C1; blind inside | TAKEN by Newton 2026 (1% width): ours is independent and about 2.7e7 times narrower; never "first" |
| C5 | Closed forms M*/M₀, S*/S_BH(0), t_decay/M₀³, photon-only and graviton-only ratios (§1) | CERTIFIED (same run, not sealed predictions) | 2040a9985f (run) | - | follows C1-C4 |
| C6 | Regge-Wheeler and Zerilli graviton Γ overlap at l = 2, 3 and Mω = 0.05, 0.2, 0.37, 0.6, 1.0; flux identities contain 0 (§4.2) | CERTIFIED (PH4) | 2040a9985f, 53d448f307 | - | control |
| C7 | l = 0 scalar: Γ₀/(16ω²) within 1e-2 of 1 at Mω = 1e-3 and within 1e-5 at 1e-6 (§4.2) | CERTIFIED (PH5) | 2040a9985f, 53d448f307 | - | control |
| C8 | Null: the graviton sum with the spin-1 potential is disjoint from Newton's interval (§4.2) | CERTIFIED (PH6) | 2040a9985f | REFEREE-HK1b (a weak null: misses by a factor of about 5.7) | null |
| C9 | The first attempt produced no total (quadrature remainder not controlled at s = 1, l = 8) (§4.1) | FAILED (as sealed) | 53d448f307 | - | - |
| C10 | β lies outside the rounding intervals of 1.48472 and 1.48471, by more than 2.33e-5 and 1.33e-5 (§5) | CERTIFIED (PH1 exclusion; rounding-interval re-score after the fact) | 2040a9985f, 48cf09638b | REFEREE-HK1b item 10 (scorer tested points; re-scored with intervals: PASS) | wording: "settles the digits Page flagged as uncertain"; never "wrong" or "corrects" |
| C11 | Page's printed P₁ and P₂ sit 1.6e-5 and 1.9e-4 (relative) below our enclosures (§5) | OBSERVATION (POST HOC, not sealed; cause not tested) | - | REFEREE-HK1b (framing) | fairness note |
| C12 | Blind second implementation (Teukolsky + MST, not rigorous, 12 digits) agrees on all seven quantities, every value inside the certified box (§4.4) | PROBE (blind; overlap checked in ball arithmetic) | - | blind seat (results/blind/) | - |
| C13 | Comparison theorem for y'' = Qy, band bounds, l > 60 lemma with far cells (§3) | PROVED (proofs/PROOF.md §6-8, with the round-2 repair) | pinned instruments of 2040a9985f | REFEREE-HK1b-2 (CORRECT; one sentence repaired, annotation G1) | band-bound idea credited to Newton 2026 |
| C14 | Anything about Kerr or charged holes, other species, massive particles, other perturbation types, or the information paradox beyond Page's definitions | NOT CLAIMED | - | - | - |
| C15 | Machine-checked proof | NOT CLAIMED (refereed, not formalised) | - | - | - |

## Numbers and their sources

Direction: `ball` = arb ball as stored; `exact` = exact value or value quoted verbatim; `lower` / `upper` = a bound
rounded the safe way by tools/derived.py; `probe` = non-rigorous; `print` = printed in a source.

| Printed | Direction | Source file (field) |
|---|---|---|
| β [1.4846916919 ± 7.81e-11]; t*/t_decay [0.5381024532 ± 8.99e-11]; P₁ [3.3638547856e-5 ± 2.57e-16]; P₂ [3.836739925e-6 ± 6.95e-16]; α [3.747528778e-5 ± 1.96e-15]; Ṡ₁ [1.2683659541e-3 ± 2.47e-14]; Ṡ₂ [1.300008786e-4 ± 5.55e-14] | ball | results/hk1b/result_hk1b.json (values) |
| M*/M₀ [0.7730042563 ± 3.34e-11]; S*/S_BH(0) [0.5975355803 ± 7.48e-11]; t_decay [8894.750463 ± 4.34e-7]; ratios [1.5002632702 ± 4.36e-11], [1.348168161 ± 5.82e-10] | ball | results/hk1b/result_hk1b.json (closed_forms) |
| relative widths 1.1e-10, 3.4e-10, 1.6e-11, 3.7e-10, 1.1e-10, 3.9e-11, 8.6e-10 | upper | results/derived.json (relative_widths_upper) |
| box widths 1.6e-10 (β), 1.8e-10 (Page time); 0.00000000016 | upper | results/derived.json (beta_width_upper); 2 × 8.99e-11 |
| gaps 1.33e-5 and 2.33e-5; 12 and 19 ppm (printed points); 9 and 16 ppm (intervals) | lower | results/derived.json (beta_gap_below_*, beta_relative_below_* for the points, beta_gap_below_*_ppm for the intervals) |
| 53.81%; 77% of the mass; 40% of the entropy | lower / upper | results/derived.json (page_time_percent, mass_left_at_page_time, entropy_lost_by_page_time) |
| l = 1: 98.0% of photon power; l = 2: 99.1% of graviton power | lower | results/derived.json (share_l1_of_photon_power, share_l2_of_graviton_power) |
| 2.7e7 times narrower than Newton's interval; Newton width 0.98% | lower / upper | results/derived.json (newton_width_over_our_P_2_width_lower, newton_relative_width_upper) |
| PH4: 10 points overlap; PH5 [0.006399818824 ± 2.01e-13] at Mω = 1e-3, [6.283403e-6 ± 4.24e-13] at 1e-6; PH6 [6.77474891e-7 ± 5.81e-16] | ball | results/hk1b/result_hk1b.json (PH4, PH5, PH6) |
| 17 channels, 322 panels (321 Taylor-model panels, 1 skipped), 0 fallbacks; 785 s | exact | results/hk1b/result_hk1b.json (channel_status, fallback_widths, sec); results/hk1b/main_hk1b.log |
| per-mode values in the mode figure | ball | results/hk1b/result_hk1b.json (channel_status, tails) |
| HK-1: PH4, PH5 PASS; PH1-PH3, PH6 INCONCLUSIVE at s = 1, l = 8 | exact | results/hk1/result_hk1.json; results/hk1/main_hk1.log; code/RUN-HK1b.md |
| re-score with rounding intervals: PASS, nothing changed | exact | results/hk1b/rescore_hk1b.json |
| referee float β 1.4846916902 (−1.7e-9) | probe | results/referee/REFEREE-HK1b.md |
| blind β 1.484691691908, Page time 0.5381024531598, P₁ 3.363854785578e-5, P₂ 3.836739924959e-6, α 3.747528778073e-5, Ṡ₁ 1.268365954077e-3, Ṡ₂ 1.300008786207e-4; midpoint differences 5.4e-12 to 1.6e-10 | probe / upper | results/blind/results.json; results/derived.json (blind) |
| 1.48472; 0.000033638; 0.000003836; "about four or five digits"; the challenge sentence | print | Page 2013, arXiv:1301.4995v3, p. 5-6, Eq. (2) |
| 1.48471; 1.61862; 1e26 g; 0.01 eV | print | Perez-Gonzalez 2025, arXiv:2502.04430v3, text after Eq. (18) |
| [3.8262e-6, 3.8639e-6]; width 3.77e-8 | print | Newton 2026, Zenodo 10.5281/zenodo.22800587, Theorem 3, Eq. (47) |
| post-hoc offsets 1.6e-5, 1.9e-4 | upper | results/derived.json (page_printed_powers_post_hoc) |
| trust base python-flint 0.9.0, CPython 3.11 | exact | proofs/PROOF.md §12 |

Tokens allowed without a result-file source (definitions and exact constants): s = 1, 2; l(l+1); 2(1 − s²); 8π; 2/3, 3/2,
1/3; 1e-8 (sealed width cap); 60 (large-l lemma threshold); 10²⁶ g (cited); 17 November 2026 (search date).
