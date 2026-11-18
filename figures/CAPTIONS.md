# Figures: point, caption source and data

All three are drawn by `figures/make_figures.py` from shipped files only.

| File | The one point | Plotted data (file, field) | Numbers in the caption (file, field) |
|---|---|---|---|
| page-time.svg | The radiation's entropy overtakes the black hole's at 53.81% of its life. | Curves: Page's closed form with β = mid of results/hk1b/result_hk1b.json (values.beta). Dot: values.page_time, closed_forms.S_star_over_SBH0. The "Page curve" band is a schematic (minimum of the two curves), labelled as such. | 0.5381024532 ± 8.99e-11 (values.page_time); 0.5975355803 ± 7.48e-11 (closed_forms.S_star_over_SBH0); β = 1.4847 (values.beta) |
| beta-number-line.svg | The certified β lies clear of both printed values; the blind check lies inside the certified box. | values.beta (box); printed 1.48472 and 1.48471 as rounding intervals (typed in the script with their sources); results/blind/results.json (beta.value_raw_B, abs_error_estimate) | box width 1.6e-10 and gap 1.33e-5 (results/derived.json: beta_width_upper, beta_gap_below_1.48471_rounding_interval_lower); 12 ppm (beta_relative_below_1.48471_lower_ppm; 12 ppm = distance to the printed point); blind 1.484691691908 (results/blind/results.json) |
| ledger-by-mode.svg | The lowest multipole carries almost everything. | channel_status (P_mode, S_mode) × 2(2l+1)/(2π); tails (upper ends) | 98.0% and 99.1% (results/derived.json: share_l1_of_photon_power, share_l2_of_graviton_power) |

Alt texts are in README.md. Style: the lab's neon-charcoal figure style (background #1c2026, categorical #3987e5, #d95926,
#199e70, #c98500, accent #39ff14).
