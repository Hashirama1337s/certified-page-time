# AMEND-HK-1-1: reading of "containing <value> (rounded to 11 significant digits)" in BAR-HK-1 (seal 53d448f307)

Written 2026-11-17 by the lead BEFORE the main run (`hk1_cert.py --main` has not run). Raised by the build seat
(build-1 report, threat 1): certified widths (~1e-12 relative) are narrower than the 11-significant-digit rounding of the
predicted values, so a literal point-containment test of the printed decimal could fail on rounding alone even when every
printed digit is right.

**Ruling (interpretation only; no prediction value, width cap or kill condition changes).** In PH1, PH2 and PH3, "contains X"
where X is printed to n significant digits means: the certified enclosure overlaps the rounding interval
[X - 0.5 ulp_n(X), X + 0.5 ulp_n(X)], ulp_n the unit in the n-th significant digit. Both flags are recorded in result_hk1.json
(`contains_bar_value_strict`, `overlaps_bar_rounding_interval`); the verdict uses the second. PH1's exclusion clause (1.48472
and 1.48471) is read the same way with their printed digits: the enclosure must be disjoint from [1.484715, 1.484725] and
[1.484705, 1.484715].

## Seal fields
- formula_ref: BAR-HK-1.md:30-40
- calibrated_on: none - no main run; the build seat's probe enclosures of single channels (disclosed in its report) motivated the clarification, not any total
- depends_on: 53d448f307
- null_not_symmetry: not applicable - an interpretation of rounding, no null changed
- target_form: interval overlap with a rounding interval; exclusion as disjointness from the printed values' rounding intervals
- parameters: n = 11 (PH1-PH3 predicted values); n = 6 (the two excluded printed betas)
- tolerances: unchanged (arb enclosures)
- ceiling: unchanged
- positive control: unchanged
- toy_model: unchanged
- files: AMEND-HK-1-1.md
- command: unchanged
