#!/usr/bin/env python
"""reproduce.py -- re-run the certificate of this repository in a clean work folder and compare with results/.

Tiers (tools/reproduce.md has the table with commands and run times):
    python tools/reproduce.py --tier quick   pins and manifest; the seven symbolic identities; the post-hoc re-score and
                                             the C9 lemma control re-run; three whole channels of the sealed run
                                             recomputed and compared; the derived numbers   (about 2 minutes on one core)
    python tools/reproduce.py --tier full    the sealed main run itself (hk1b_cert.py --main, about 13 minutes on one
                                             core), compared with the shipped result, ledger and log; then the quick
                                             checks, with the re-score applied to the freshly produced result
    python tools/reproduce.py --tier blind   the blind second implementation (results/blind/code/: Teukolsky + MST
                                             series, not rigorous): spin-1 constants, both spin runs, combination,
                                             controls, final values, each compared with the shipped outputs
                                             (about 7 minutes on one core; needs mpmath)
Options: --work DIR (default ./work; must not exist or be empty); --python "CMD" (default: this interpreter);
         --list (print the checks and exit).

What it does
  1. tools/check_pins.py: every file the lab ledger pinned (instruments, sealed bars, results) against its pin, with
     path-patched copies restored in memory first (PATCHES.md), and every file against MANIFEST.sha256.
  2. Work folder: every code/*.py is copied into WORK and restored to its sealed bytes (the restored instrument files
     have the pinned sha256, and therefore the instrument hash the sealed run recorded). The instruments write their
     outputs next to themselves, so every output lands in WORK.
  3. Each check runs `python <script> <args>` with WORK as the current folder; its console output goes to
     WORK/_out/<check>.log. Produced files are compared with the shipped ones by canonical content (tools/canon.py:
     run times, wall-clock stamps, the memory-cap line and the folder name removed; every digit of every enclosure
     must agree). The main log is compared up to its first `MAIN v2 done` line (the shipped copy also carries the
     console lines the lab's launcher appended after the run).
Last line: [reproduce] ALL CHECKS PASS (or the list of failures). Exit code 0 on success. A JSON report is written to
WORK/_out/reproduce_report.json.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
import pathpatch  # noqa: E402
import canon  # noqa: E402

R = os.path.join(ROOT, 'results')
CHANNELS = ['1,9', '2,9', '2,7']


def lab_root():
    """the lab folder the sealed run used (stored as hex in the patch table), so its name can be canonicalised."""
    tab = pathpatch.load()
    ent = {e['id']: bytes.fromhex(e['original_hex']).decode('utf-8') for e in tab['table']}
    return ent['R4'] + '/build-1'


def read_restored(rel):
    with open(os.path.join(ROOT, rel), 'rb') as f:
        return pathpatch.restore_bytes(f.read())


def main(argv):
    tier, work, py = None, os.path.join(ROOT, 'work'), [sys.executable]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--tier':
            tier = argv[i + 1]; i += 2
        elif a == '--work':
            work = os.path.abspath(argv[i + 1]); i += 2
        elif a == '--python':
            py = shlex.split(argv[i + 1]); i += 2
        elif a == '--list':
            print(__doc__); return 0
        else:
            sys.exit(__doc__)
    if tier not in ('quick', 'full', 'blind'):
        sys.exit(__doc__)
    if os.path.exists(work) and os.listdir(work):
        sys.exit('reproduce: work folder %s exists and is not empty' % work)
    out = os.path.join(work, '_out')
    os.makedirs(out, exist_ok=True)
    roots = [lab_root(), lab_root()[:-len('/build-1')] + '/blind-1', os.path.join(work, 'blind'), work]
    report, fails = [], []

    def say(msg):
        print('[reproduce] ' + msg, flush=True)

    def run(name, args, cwd=work):
        t0 = time.time()
        with open(os.path.join(out, name + '.log'), 'wb') as fh:
            rc = subprocess.call(py + args, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT,
                                 env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1'))
        dt = time.time() - t0
        say('%s: exit %d (%.0f s)' % (name, rc, dt))
        return rc

    def record(name, ok, detail):
        report.append({'check': name, 'ok': bool(ok), 'detail': detail})
        if not ok:
            fails.append(name)
        say('%s: %s%s' % (name, 'PASS' if ok else 'FAIL', (' - ' + detail) if detail else ''))

    def compare(name, kind, produced, expected_rel, cut=None, ignore=()):
        if not os.path.exists(produced):
            record(name, False, 'no output %s' % produced)
            return
        p = open(produced, 'rb').read()
        e = read_restored(expected_rel)
        if ignore:  # keys that name the input file itself (its path and sha256), not a result
            p, e = (json.dumps({k: v for k, v in json.loads(x).items() if k not in ignore}).encode() for x in (p, e))
        if cut:
            p, e = (x[:x.index(cut) + len(cut)] if cut in x else x for x in (p, e))
        st, hp, he, diffs = canon.compare(kind, p, e, roots)
        record(name, st.startswith('IDENTICAL'), '%s vs %s: %s' % (os.path.relpath(produced, work), expected_rel, st)
               + ('; ' + ' | '.join(diffs) if diffs else ''))

    # 1. pins and manifest
    record('check_pins', run('check_pins', [os.path.join(TOOLS, 'check_pins.py')], cwd=ROOT) == 0, '')

    if tier == 'blind':
        return blind(work, out, run, record, compare, say, report, fails)

    # 2. work folder with the sealed bytes
    for f in sorted(os.listdir(os.path.join(ROOT, 'code'))):
        if f.endswith('.py'):
            with open(os.path.join(work, f), 'wb') as fh:
                fh.write(read_restored('code/' + f))
    say('work folder %s prepared (%d code files restored)' % (work, len([f for f in os.listdir(work) if f.endswith('.py')])))

    # 3. full tier: the sealed main run
    if tier == 'full':
        rc = run('main', ['hk1b_cert.py', '--main'])
        record('main_exit', rc == 0, '')
        compare('main_result', 'json', os.path.join(work, 'result_hk1b.json'), 'results/hk1b/result_hk1b.json')
        compare('main_ledger', 'jsonl', os.path.join(work, 'ledger_hk1b.jsonl'), 'results/hk1b/ledger_hk1b.jsonl')
        compare('main_log', 'log', os.path.join(work, 'main_hk1b.log'), 'results/hk1b/main_hk1b.log',
                cut=b'MAIN v2 done')
    else:
        with open(os.path.join(work, 'result_hk1b.json'), 'wb') as fh:
            fh.write(read_restored('results/hk1b/result_hk1b.json'))

    # 4. quick checks
    rc = run('sym_checks', ['sym_checks.py'])
    lines = [l.strip() for l in open(os.path.join(out, 'sym_checks.log'), encoding='utf-8', errors='replace')
             if l.strip() and not l.startswith('memcap')]
    record('sym_checks', rc == 0 and lines and all(l == 'True' for l in lines),
           '%d identities printed True' % sum(l == 'True' for l in lines))
    rc = run('rescore', ['rescore_hk1b.py'])
    record('rescore_exit', rc == 0, '')
    # in the full tier the re-score reads the freshly produced result, whose bytes differ from the shipped one only in its
    # run time ("sec"), so the recorded sha256 of the input file differs; everything the re-score concludes must agree
    compare('rescore', 'json', os.path.join(work, 'rescore_hk1b.json'), 'results/hk1b/rescore_hk1b.json',
            ignore=('source', 'source_sha256') if tier == 'full' else ())
    rc = run('c9_teeth', ['c9_teeth_hk1b.py'])
    record('c9_teeth_exit', rc == 0, '')
    compare('c9_teeth', 'json', os.path.join(work, 'c9_teeth_hk1b.json'), 'results/hk1b/c9_teeth_hk1b.json')
    rc = run('replay_channels', [os.path.join(TOOLS, 'replay_channels.py'), work,
                                 os.path.join(R, 'hk1b', 'result_hk1b.json')] + CHANNELS)
    record('replay_channels', rc == 0, 'channels ' + ' '.join(CHANNELS))
    rc = run('derived', [os.path.join(TOOLS, 'derived.py'), '--out', os.path.join(out, 'derived.json')], cwd=ROOT)
    record('derived_exit', rc == 0, '')
    compare('derived', 'json', os.path.join(out, 'derived.json'), 'results/derived.json')

    with open(os.path.join(out, 'reproduce_report.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'tier': tier, 'checks': report, 'failures': fails}, fh, indent=1)
    if fails:
        say('FAILED: ' + ', '.join(fails))
        return 1
    say('ALL CHECKS PASS')
    return 0


def blind(work, out, run, record, compare, say, report, fails):
    """The blind seat's scripts name their lab folder in string literals (sys.path inserts, output files). Their work
    copies are restored (PATCHES.md) and that one folder name is then pointed at WORK/blind; these files are not sealed."""
    bw = os.path.join(work, 'blind')
    os.makedirs(bw)
    src = os.path.join(ROOT, 'results', 'blind', 'code')
    labdir = (lab_root()[:-len('/build-1')] + '/blind-1').encode()
    for f in sorted(os.listdir(src)):
        if f.endswith('.py'):
            data = read_restored('results/blind/code/' + f).replace(labdir, bw.replace(os.sep, '/').encode())
            with open(os.path.join(bw, f), 'wb') as fh:
                fh.write(data)
    say('blind work folder %s prepared' % bw)
    B = 'results/blind/code/'
    steps = [('blind_unitarity', ['unitarity_fit.py'], [('spin1_constants.json', B + 'spin1_constants.json', 'json')]),
             ('blind_s1', ['run_spin.py', '-1', '40', os.path.join(bw, 'main_s1.json')],
              [('main_s1.json', B + 'main_s1.json', 'json')]),
             ('blind_s2', ['run_spin.py', '-2', '40', os.path.join(bw, 'main_s2.json')],
              [('main_s2.json', B + 'main_s2.json', 'json')]),
             ('blind_combine', ['combine.py'], [('combined.json', B + 'combined.json', 'json')]),
             ('blind_controls', ['controls.py'], [('controls.json', B + 'controls.json', 'json')]),
             ('blind_results', ['make_results.py'], [('results.json', 'results/blind/results.json', 'json')])]
    for name, args, cmp in steps:
        rc = run(name, args, cwd=bw)
        record(name + '_exit', rc == 0, '')
        for produced, shipped, kind in cmp:
            compare(name, kind, os.path.join(bw, produced), shipped)
    compare('blind_s1_log', 'log', os.path.join(out, 'blind_s1.log'), B + 'main_s1.log')
    compare('blind_s2_log', 'log', os.path.join(out, 'blind_s2.log'), B + 'main_s2.log')
    with open(os.path.join(out, 'reproduce_report.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'tier': 'blind', 'checks': report, 'failures': fails}, fh, indent=1)
    if fails:
        say('FAILED: ' + ', '.join(fails))
        return 1
    say('ALL CHECKS PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
