# PATCHES: lab paths and redactions in the shipped copies

The lab's files name lab folders in a few places: docstrings and usage lines, one data-file literal used only by a
control (C6), recorded tracebacks and source paths in result files, the blind seat's scripts, the prior-art gate
reports and the lab ledger rows. Every shipped copy has had those folder names replaced by placeholders from one
fixed table, `tools/path_patch.json`, applied in the order below. This substitution is exactly reversible.

- `tools/check_pins.py` restores every patched file in memory and checks that the restored bytes have the listed
  original sha256 (for pinned files: the lab ledger pin, `tools/pins.json`), and that the shipped file has the patched
  sha256 listed here.
- `tools/reproduce.py` restores the originals inside its work folder before running anything, so every run sees the
  sealed bytes (and the sealed run's instrument hash).
- The original folder names are stored in the table hex-encoded (encoded, not hidden: anyone can decode them). They
  are lab folder names only; `tools/privacy_scan.txt` records a scan of every encoded string in the repository.

## Redacted (irreversible)

Personal details are not encoded anywhere; they were removed, and the removed text cannot be recovered from this
repository. Both sealed bar files also named the lab owner, and the blind seat's report named a home-folder cache
path. Each is replaced by a bracketed note. The two bars are pinned by the lab ledger: their pins are listed in
`tools/pins.json` with the note "verifiable against the lab ledger only (redacted for privacy)", and check_pins
reports them as REDACTED. One more file was corrected for release, not redacted: in `proofs/PROOF.md` the β radius
is printed as stored (7.81e-11) instead of the rounded-down 7.8e-11.

| File | Pinned | What was removed or changed | Lab-original sha256 (lab ledger) | sha256 after redaction, before path patch |
|---|---|---|---|---|
| proofs/PROOF.md | no | release fix: the stored radius 7.81e-11, not the rounded-down 7.8e-11 | `c61a8edae641ff9523993d5fa1b45770631309791924945a52e5c1e167786fb6` | `df013d34fb60989155f4d5385c58b9ff730c9be8bd4e61c72ed75200c7d4eb7e` |
| results/blind/BLIND-REPORT.md | no | home-folder cache path | `a957d2745efa7bc5bb5f2c0f3cca99a42d490904ccca7ce570818dcd5d05a25f` | `84c6c8f85d844e7efe1f8d57cc9d41ec2979283b028ed5fc59e588fa8b7cef16` |
| results/seals/BAR-HK-1.md | yes | owner name | `b777b10bd12e08166ed3e693f518b67ae225c7a3faf1e25b4e7fb926d5fd865a` | `76f20554e96093f273ecfca5656887248616e56229f6bd47d853ead9e08b95ed` |
| results/seals/BAR-HK-1b.md | yes | owner name | `8fc850c00365791dac9a0e0a97dfda1bbfa5258f6db237fe6d5eebf13a17d208` | `312d2a3c0b58e318c07cbc9274ff4608ead05a13efdd5008e6488645a2201b27` |

## Substitution table (applied in this order; restored in reverse order)

| Entry | Placeholder | What the original names |
|---|---|---|
| R1 | `<LAB-JSON>` | lab project root, JSON-escaped Windows form (18 characters) |
| R2 | `<MEMCAP>` | the lab's memory-cap launcher (38 characters) |
| R3 | `<RECON>` | the lab's earlier reconnaissance project folder (23 characters) |
| R4 | `<LAB>` | lab project root, forward-slash form (16 characters) |
| R5 | `<lab>` | lab project root, lower-case form (ledger rows) (16 characters) |
| R6 | `<recon>` | reconnaissance folder, lower-case form (ledger rows) (23 characters) |
| R9 | `<LABTOOL>` | the lab's own command-line tool (gate lines) (35 characters) |

Entries R7 and R8 of earlier drafts were removed (now redacted, above).

## Patched files

For a redacted file, "Original sha256" is the sha256 after redaction (the bytes the restore step gives back).

| File | Pinned | Original sha256 | Patched sha256 | Entries (count) |
|---|---|---|---|---|
| code/RUN-HK1b.md | no | `fead7afd031b0c60e5244ae424143fec8d9b47f0bc0d097691168150124ef00b` | `142427d6a22757e2af2ed8cea5d6d166decaf4ced79ba8737d0a45c1e48745c6` | R2 x1, R4 x1 |
| code/RUN.md | no | `3fa3b5f0be0b71150ad9140864c1bc2db5ef2e47d192c52c6cf2dd3d3553f5d9` | `5c827cd3cd18162cecd7092ee0724e2dbbbbe11d653713ca4b5645b52c85f0ac` | R2 x1, R4 x2 |
| code/hk1_cert.py | yes | `8fc13b9fb3528ad4777f16eb41b0366ea4d51a5d79569ab9f48943a1a520a5d7` | `6dabec4c2a62819678bc36566f7686c266505976b81c2d148c4503de7b53f39c` | R3 x1, R4 x1 |
| code/hk1b_cert.py | yes | `b3eaf122527162edb97f6b94c58ed9fb443e6237b17acefe8f25c35c314c0bfd` | `2d29efb06573d7adbb11667ca1fa9daa08dfcef30d9f06bb08e61b0f83995526` | R3 x1 |
| code/hkcore.py | yes | `67cde61d4c629f59c1c64bc76f1389c577c210062fd7d157416ac57e6397665b` | `25318849f28f3c5253f9721afbf01dab88f650232c521710cfc4c0d888f36726` | R3 x1 |
| proofs/PROOF.md | no | `df013d34fb60989155f4d5385c58b9ff730c9be8bd4e61c72ed75200c7d4eb7e` | `ef6d9a7048315ae20f87ea1138a775b9f717f29ecfe0ba8ca2acb73186b3c5b6` | R3 x1 |
| results/blind/BLIND-REPORT.md | no | `84c6c8f85d844e7efe1f8d57cc9d41ec2979283b028ed5fc59e588fa8b7cef16` | `4107b1373d0b480c33dc79d311340b77f9353f3407ad003fe81a8028bda99a78` | R4 x1 |
| results/blind/code/combine.py | no | `afcfb835858e0952465f89944a3786edc7ff563b33eb32e90f7396b6907ac8af` | `ff741af0d5844a09400afea1fca8aa69aff8595b7e3636020ac9de35f53bfb11` | R4 x1 |
| results/blind/code/controls.py | no | `2b31a7f82b29b3915119da515708c83e3de2038803c4f50d5e01e66cff90d5a4` | `8a1578a30233550eabcb1dabd0cb693af91515e85c5f9fb0e34359dafb819685` | R4 x2 |
| results/blind/code/make_results.py | no | `d65527e3c217c9282158d644e74c592126021c5ff5bf797f4bc3f466708bd91c` | `8a3f838deba0e3244c3c54936d8b2f183438bc4d6e0131e2e755fee94d0c7d53` | R4 x3 |
| results/blind/code/run_spin.py | no | `27e9fef1b35e2ce43ec740b6418b9d536065740442c191db336f6fd242903283` | `81577c31a5502edd46e74bcc47cd8f4e4765db501147b68d307c72ed8606ecd8` | R4 x1 |
| results/blind/code/unitarity_fit.py | no | `21fb3ac040ccfe192915c96b85714689f2069481c89e6b89671d65dee6fe6bba` | `0095500f5be1b2a539f31969d5a58c1df34e1b300c71288d199700fca254558a` | R4 x2 |
| results/hk1/result_hk1.json | yes | `9334782d4b55c4c179f1db07831364a416c722671faeaec22f57bfba22f4d66d` | `4b408872aad3031f5ad78997a03b987201631f400b64eea7fc431fae053bebc4` | R1 x13 |
| results/hk1b/rescore_hk1b.json | no | `485d9e4967b963e30962e4e87338d41383d99606623159b01a13fd86bcb27cf5` | `174e7cd456d1c4a4c7ee659c9b0c865495ddea7510197b4493191d83b0f114bc` | R1 x1 |
| results/ledger-hawking.json | no | `9de626bd1f71ab4d08c1605a0ff9f737c8a5bb64b1108907b521d30cd64860b6` | `51af1179f82088a8f6d515eaaa9c501e0181a97c5c8be1d90e583e2e981225ca` | R5 x41, R6 x2 |
| results/prior-art/gate-1/GATE-HAWKING.md | no | `c0ec7194bf56996f536f55b9727b92f8d9063131d4e9221eab68dcb57e5c3406` | `d5eef828de3c239d6434359d907346afe47f74849e02db5503b3c6c67cb8d71c` | R2 x4, R4 x8, R9 x4 |
| results/prior-art/gate-2/GATE-REFRESH.md | no | `3ff93203f4b952fe65dad7c5a3d93e46853357d779a57786020649f391bd0114` | `bc76f5bbf6a832b2978fa627dcbb0de948c9e559e307a93b1948d846c2476e3e` | R2 x5, R4 x10, R9 x5 |
| results/referee/REFEREE-HK1b.md | no | `3144832d100f81dfde1607a423bd57970858c8d2170bd19651147fe1fe66ae32` | `dc615343595f6ee52a1b1abcc02a431309e698c1fffbbedc6aa9b9fc101c3d77` | R4 x1 |
| results/seals/BAR-HK-1.md | yes | `76f20554e96093f273ecfca5656887248616e56229f6bd47d853ead9e08b95ed` | `058e72d623ab4f380c416529474cbd2bf6ca17306defa1f51dfc67111e04ae9e` | R3 x2 |
| results/seals/BAR-HK-1b.md | yes | `312d2a3c0b58e318c07cbc9274ff4608ead05a13efdd5008e6488645a2201b27` | `eb402592d943ec855048305b51c6d23182962f83bb365e8a59eefbc12eeaa659` | R3 x2 |
