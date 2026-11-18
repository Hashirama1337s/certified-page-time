#!/usr/bin/env python
"""replay_channels.py -- recompute whole channels of the sealed run and compare them with the shipped result.

Usage:  python tools/replay_channels.py WORK RESULT s,l [s,l ...]
  WORK    a folder holding the restored instrument files (tools/reproduce.py prepares it)
  RESULT  the result file to compare with (results/hk1b/result_hk1b.json)
Each channel (spin s, multipole l) is solved from scratch with the sealed v2 driver (hk1b_channel.run_channel_safe) and
a fresh, temporary ledger; its status, panel counts and the per-mode enclosures P_mode and S_mode must equal the
shipped strings character for character. Exit 0 if all agree.
"""
import json
import os
import sys


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    work, result = os.path.abspath(argv[0]), argv[1]
    sys.path.insert(0, work)
    import hk1b_cert as V2          # noqa: E402  (instrument_sha256; importing runs nothing)
    import hk1b_channel as C2       # noqa: E402
    shipped = json.load(open(result, encoding='utf-8'))['channel_status']
    sha = V2.instrument_sha256()
    print('instrument sha256 %s' % sha)
    bad = 0
    for tok in argv[2:]:
        s, l = (int(x) for x in tok.split(','))
        tmp = os.path.join(work, '_replay_%d_%d.jsonl' % (s, l))
        if os.path.exists(tmp):
            os.remove(tmp)
        row = C2.run_channel_safe(s, l, C2.Ledger(tmp, sha[:16]))
        os.remove(tmp)
        want = shipped['%d,%d' % (s, l)]
        diff = [k for k in ('status', 'panels', 'skipped', 'fallbacks', 'P_mode', 'S_mode') if row.get(k) != want.get(k)]
        bad += bool(diff)
        print('channel s=%d l=%d: P_mode %s S_mode %s panels %d -> %s' % (s, l, row['P_mode'], row['S_mode'], row['panels'],
                                                                      'IDENTICAL' if not diff else 'DIFFERENT %s' % diff))
    print('replay_channels: %s' % ('ALL IDENTICAL' if not bad else '%d channel(s) differ' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
