#!/usr/bin/env python
"""canon.py -- canonical content of a run log or result file, so that a re-run can be compared with the shipped one.

A log carries the mathematics (verdict lines, enclosures, counts, parity, sha256 provenance lines) and the run record
(elapsed-time stamps, peak memory, the folder it ran in, the shell's own wrapper lines). The canonical form keeps the
first and removes only the second:
  - text is decoded (UTF-8, byte-order mark dropped) and split into lines (CR LF or LF);
  - dropped lines: the memory-cap wrapper's exit line (`memcap: exit ...`), the shell's appended `rc=N` line and the
    PowerShell error block that wrapper line produced in some lab logs (`At line:...`, `+ ...`, `CategoryInfo`,
    `FullyQualifiedErrorId`, blank), and the launcher's own `[run_sealed]` lines;
  - in every other line: the leading elapsed-time stamp `[  12.3s]` or wall-clock stamp `17:32:14` is removed; every
    elapsed-time value of the form
    `<number>s` (e.g. `(117s)`, `total 853s`, `in 1.4s`, `t=374.6s`) becomes `<T>s`; the project folder (the lab
    root, or the work folder of the re-run) becomes `<ROOT>`;
  - a summary line that prints a Python dict (`DONE {...}`, the last line of b5/close_b5.py) is re-printed with sorted
    keys: close_b5.py keeps the key order of the result file it found on disk, so the order records which mode ran
    first in that folder, not a result.
Nothing else is touched: every digit of every enclosure, count and hash must agree.
JSON / JSON-lines: parsed, then the run-record keys (VOLATILE_KEYS) are removed at any depth, re-serialised with sorted
keys.

Library: canon_text(data, roots) -> list of lines; canon_json(data) -> str; canon_jsonl(data) -> list of str;
         compare(kind, produced_bytes, expected_bytes, roots) -> (status, sha_p, sha_e, first_differences)
Command line:  python tools/canon.py FILE [ROOT ...]   prints the canonical form.
"""
import ast
import hashlib
import json
import re
import sys

VOLATILE_KEYS = {'seconds', 'sec', 'secs', 'runtime_s', 'elapsed', 'time_s', 'panel_sec_total', 'panel_sec_max', 'total_time_s'}
DROP = [re.compile(p) for p in (
    r'^(py : )?memcap: exit', r'^rc=-?\d+\s*$', r'^At line:\d+ char:\d+', r'^\+ ', r'^\s+\+ (CategoryInfo|FullyQualifiedErrorId)',
    r'^\s+\+\s+~+', r'^\s*$', r'^\[run_sealed\]',
    r'^\s*"(seconds|sec|secs|runtime_s|elapsed|time_s)": -?\d+(\.\d+)?,?$')]  # run-time lines of a printed JSON dump
# leading elapsed-time stamp `[  12.3s]`, or the wall-clock stamp `17:32:14 ` that this project's logs carry
STAMP = re.compile(r'^(\[\s*\d+(\.\d+)?s\]|\d{2}:\d{2}:\d{2})\s?')
VKEY = re.compile(r'"(seconds|sec|secs|runtime_s|elapsed|time_s)": -?\d+(\.\d+)?')
SECS = re.compile(r'(?<![\w.])\d+(\.\d+)?s\b')


def _roots(roots):
    out = []
    for r in roots:
        if not r:
            continue
        for v in {r, r.replace('/', '\\'), r.replace('\\', '/'), r.lower(), r.replace('\\', '/').lower(),
                  r.replace('/', '\\\\')}:
            out.append(v)
    return sorted(set(out), key=len, reverse=True)


def canon_text(data, roots=()):
    if isinstance(data, bytes):
        data = data.decode('utf-8-sig', errors='replace')
    rs = _roots(roots)
    out = []
    for line in data.splitlines():
        line = line.lstrip('﻿').rstrip()
        if any(p.search(line) for p in DROP):
            continue
        line = STAMP.sub('', line)
        for r in rs:
            line = line.replace(r, '<ROOT>')
        line = SECS.sub('<T>s', line)
        line = VKEY.sub(r'"\1": <T>', line)  # a run-time field inside a printed record (b5g background lines)
        if line.startswith('{') and line.endswith('}'):
            try:  # a whole-line JSON record (b5g/refine_*.log): drop its run-time fields, as for JSON files
                line = json.dumps(_strip(json.loads(line)), sort_keys=True)
            except ValueError:
                pass
        if line.startswith('DONE {'):
            try:
                line = 'DONE ' + json.dumps(ast.literal_eval(line[5:]), sort_keys=True)
            except (ValueError, SyntaxError):
                pass
        out.append(line)
    return out


def _strip(x):
    if isinstance(x, dict):
        return {k: _strip(v) for k, v in x.items() if k not in VOLATILE_KEYS}
    if isinstance(x, list):
        return [_strip(v) for v in x]
    return x


def canon_json(data, roots=()):
    if isinstance(data, bytes):
        data = data.decode('utf-8-sig')
    for r in _roots(roots):
        data = data.replace(r.replace('\\', '\\\\'), '<ROOT>').replace(r, '<ROOT>')
    return json.dumps(_strip(json.loads(data)), sort_keys=True, separators=(',', ':'))


def canon_jsonl(data, roots=()):
    if isinstance(data, bytes):
        data = data.decode('utf-8-sig')
    return [canon_json(l, roots) for l in data.splitlines() if l.strip()]


def _sha(lines):
    return hashlib.sha256(('\n'.join(lines) + '\n').encode('utf-8')).hexdigest()


def compare(kind, produced, expected, roots=()):
    """kind: 'log', 'json', 'jsonl' or 'bytes'. Returns (status, sha_produced, sha_expected, differences)."""
    if kind == 'bytes' or produced == expected:
        hp, he = hashlib.sha256(produced).hexdigest(), hashlib.sha256(expected).hexdigest()
        return ('IDENTICAL' if hp == he else 'DIFFERENT'), hp, he, []
    if kind == 'json':
        a, b = [canon_json(produced, roots)], [canon_json(expected, roots)]
    elif kind == 'jsonl':
        a, b = canon_jsonl(produced, roots), canon_jsonl(expected, roots)
    else:
        a, b = canon_text(produced, roots), canon_text(expected, roots)
    if a == b:
        return 'IDENTICAL-CANONICAL', _sha(a), _sha(b), []
    diffs = []
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else '<missing>'
        y = b[i] if i < len(b) else '<missing>'
        if x != y:
            diffs.append('line %d: produced %r | expected %r' % (i + 1, x[:300], y[:300]))
            if len(diffs) >= 6:
                break
    return 'DIFFERENT (%d vs %d canonical lines)' % (len(a), len(b)), _sha(a), _sha(b), diffs


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raw = open(sys.argv[1], 'rb').read()
    if sys.argv[1].endswith('.jsonl'):
        print('\n'.join(canon_jsonl(raw, sys.argv[2:])))
    elif sys.argv[1].endswith('.json'):
        print(canon_json(raw, sys.argv[2:]))
    else:
        print('\n'.join(canon_text(raw, sys.argv[2:])))
