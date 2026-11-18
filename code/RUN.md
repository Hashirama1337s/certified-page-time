# BAR-HK-1 instrument - how to run (build seat build-1, 2026-11-17)

Sealed bar: `<LAB>/BAR-HK-1.md` (seal 53d448f307). The build seat has NOT run `--main`.

## Main command (LEAD ONLY)

```
cd <LAB>/build-1
py -3.11 <MEMCAP> 8 py -3.11 hk1_cert.py --main
```

Outputs:
- `result_hk1.json`: keys PH1..PH6, each with an outcome (PASS / FAIL / INCONCLUSIVE + reason), enclosure strings, relative widths, flags and `instrument_sha256`.
- `main_hk1.log`: progress lines.
- `ledger_hk1.jsonl`: the resumable ledger, one line per finished panel / channel / tail.

Resume: if the run is interrupted, rerun the same command. Ledger rows with the same instrument hash are reused. Any edit to the instrument files changes the hash, so the old rows are ignored.

## Projected time

From `--probe` (measured 2026-11-17, `probe_hk1.json`):
- 17 Taylor-model channels: s=1, l=1..9 and s=2, l=2..9. That is about 300 panels at 1.3-2.1 s each.
- Per-l tail bounds for l = 10..60 (both spins), plus the large-l lemma.

Projected total: **about 14 min (839 s)**, on one core, with peak memory 0.02 GB. That is far inside the bar's 3-hour limit, and no single phase exceeds 30 min. The biggest channel is s=1, l=1, at about 137 s.

## Other modes (build seat)

- `--probe`: per-(s,l) panel count and timing, plus the projected main time. Takes about 4 min.
- `--controls`: controls C1-C11 plus the timing probe, written to `controls_hk1.json`. Takes about 8 min.
- `sym_checks.py`: sympy identities used by the code. All print True.

## Configuration (in code)

| setting | value |
|---|---|
| L_T | 9 (Taylor-model channels) |
| L_BIG | 60 (per-l band bounds up to here, lemma beyond) |
| W_HI | 205/128 (Planck tail with Gamma <= 1 above) |
| panels | delta = w0/10, rho_w = w0/2 |
| jets | 64 coefficients |
| precision | 256 bits (jets auto-escalate) |
| IR stop | per-mode IR bound < 1e-17 (P) and < 1e-15 (S) |
