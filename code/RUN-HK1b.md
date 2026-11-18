# BAR-HK-1b instrument (v2): how to run (build seat build-1, 2026-11-17)

The build seat has NOT run `--main`. The pinned v1 files are untouched: hkcore, hkquad, hkbounds, hkchannel, hk1_cert, sym_checks.

## Main command (LEAD ONLY)

```
cd <LAB>/build-1
py -3.11 <MEMCAP> 8 py -3.11 hk1b_cert.py --main
```

It writes three files:
- `result_hk1b.json`: PH1-PH6, each PASS, FAIL or INCONCLUSIVE with its reason. It also holds per-channel status (OK or INCONCLUSIVE-LOCAL), fallback widths against the budget, enclosures and the instrument sha256.
- `main_hk1b.log`: the run log.
- `ledger_hk1b.jsonl`: resumable. To resume, rerun the same command.

No v1 ledger row is reused, because the v1 panels went through a different quadrature code path.

## Projected time

The full probe (`--probe`, 2026-11-17) is the main's own work. It solves every panel of all 17 Taylor-model channels: 327 panels, 1 skipped, 0 fallbacks. It also evaluates all 102 tail channels (s=1,2, l=10..60) and the l>60 lemma, with no failures.

| item | time |
|---|---|
| Full probe wall time | 798 s |
| Projected main | about 13.5 min (808 s) |
| Largest channel (s=1, l=1, 55 panels) | 118 s |
| Slowest single panel | 2.5 s |

Peak memory is 0.02 GB. This is well inside the 3 h limit, and no single phase comes near 30 min.

## What changed from v1

v1 failed at `main_hk1.log` l.180, at channel s=1 l=8, panel 0, w in [1.31, 1.60].

- **Re-centred quadrature (`hk1b_quad`).** Q(u)=|P(u)|^2 is shifted exactly to each sub-interval centre before the ball remainder is taken. v1 shifted the degree-126 polynomial directly to a ball. On turn-on panels Q falls about 10^4-fold (4.8e4 to 3.5), so the ball enclosure contained 0 at every halving depth.
- **Absolute skip (`hk1b_channel`).** If a panel's certified band bound is at most 1e-22 (P) and at most 1e-20 (S) per mode, the panel contributes [0, bound] and is not solved.
- **Fallbacks.** A panel failure falls back to [0, band bound]. A channel failure falls back to [0, channel_tail_bound]. Both are recorded as INCONCLUSIVE-LOCAL, and the totals stay rigorous.
- **Fallback budget (stated in advance).** The summed fallback widths, after the 2(2l+1)/(2pi) factor, must be at most 1e-15 (P) and 1e-13 (S) per spin. Any excess is reported in `result_hk1b.json`.

Predictions, bar values and PASS logic are unchanged from hk1_cert.py and imported from it. The rounding-interval reading follows AMEND-HK-1-1 (seal 48cf09638b).

## Other modes (build seat)

- `--controls` (about 16 min, including the full probe) writes `controls_hk1b.json`.
- `--probe` (about 13 min) writes `probe_hk1b.json`. It keeps only status and timing; its temporary ledger is deleted.
