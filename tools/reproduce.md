# Reproduce

Everything runs from the repository root with Python 3.11 and python-flint 0.9.0 (`pip install python-flint==0.9.0`);
the identity check also needs sympy (`pip install sympy`), and the figures need matplotlib. No other dependency, no
network access, no file outside the repository and the work folder.

| Command | What it does | Time (one core) |
|---|---|---|
| `python tools/check_pins.py` | every file the lab ledger pinned (9 instrument files, 3 sealed bar files, 4 result and log files, 2 control files) against its pin, restoring path-patched copies in memory first (PATCHES.md); every file against MANIFEST.sha256 | seconds |
| `python tools/reproduce.py --tier quick` | check_pins; the seven symbolic identities (`code/sym_checks.py`); the post-hoc re-score with rounding intervals (`code/rescore_hk1b.py`); the large-l lemma control with teeth (`code/c9_teeth_hk1b.py`); three whole channels (the cheapest, s,l = 1,9; 2,9; 2,7; the dominant channels are replayed only in the full tier) recomputed from scratch (`tools/replay_channels.py`); the derived numbers (`tools/derived.py`) | about 2 minutes |
| `python tools/reproduce.py --tier full` | the sealed main run itself (`code/hk1b_cert.py --main`) in a fresh work folder, compared with `results/hk1b/result_hk1b.json`, `ledger_hk1b.jsonl` and `main_hk1b.log`; then the quick checks, with the re-score applied to the freshly produced result | about 15 minutes |
| `python tools/reproduce.py --tier blind` | the blind second implementation (`results/blind/code/`: Teukolsky equation by the Mano-Suzuki-Takasugi series; not rigorous): spin-1 constants by flux conservation, the photon and graviton runs, the combination, the controls and the final values, each compared with the shipped output. Needs mpmath. Its scripts name the lab folder in string literals; the work copies are restored and that one folder name is pointed at the work folder (these files are not sealed) | about 5-7 minutes (blind report: 229 s photons, 170 s gravitons, 14 s controls; lab replay 165 s and 114 s) |
| `python tools/make_scorecard.py` | SCORECARD.md and scorecard.svg from the ledger export | seconds |
| `python figures/make_figures.py` | the three figures from the shipped results | seconds |
| `python tools/make_manifest.py` | rewrites MANIFEST.sha256 after any change | seconds |

**How outputs are compared.** By canonical content (`tools/canon.py`): run times, wall-clock stamps, the memory-cap line
and the folder name are removed; every digit of every enclosure, count and hash must agree. The instrument records its own
sha256 (over the eight instrument files) in its result and in every ledger row, so a run from altered files cannot match.

**The work folder.** `--work DIR` (default `./work`, which must not exist or be empty). The code is copied there and the
path-patched copies are restored to their sealed bytes before anything runs; the instrument writes its outputs next to
itself, so nothing outside the work folder is written. Each check's console output is in `WORK/_out/<check>.log`, and a
JSON report in `WORK/_out/reproduce_report.json`. The last line is `[reproduce] ALL CHECKS PASS`.

**Not replayed.** The build seat's controls (`results/hk1b/controls_hk1b.json`, about 16 minutes) are shipped as recorded.
One of them (C6) reads a floating-point reference file from the lab's earlier reconnaissance project, which is not
shipped; running `code/hk1b_cert.py --controls` outside the lab therefore stops at C6. The failed first attempt
(`code/hk1_cert.py --main`) is shipped for the record and not replayed.

**Lab record of the replay** (the lab's own machine, 2026-11-17, Python 3.11.9, python-flint 0.9.0, one core, from a
fresh copy of this repository). Quick tier: ALL CHECKS PASS in about 1 minute (the three channels take about 60 s).
Full tier (run twice, the second time from a fresh copy): the sealed main run finished in 781 s and 777 s (the lab's sealed run took 785 s); its result, all 781 ledger rows and its
log were IDENTICAL in canonical content to the shipped ones, and every quick check passed. Blind tier: ALL CHECKS PASS
in about 5 minutes (photons 165 s, gravitons 114 s); every output identical in canonical content to the shipped one.
