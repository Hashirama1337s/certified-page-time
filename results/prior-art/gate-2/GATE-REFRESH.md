# GATE-REFRESH - pre-release prior-art refresh, HAWKING, seat gate-2 (2026-11-17)

Seat: prior-art scout (refresh of seats/gate-1/GATE-HAWKING.md, same day). I read the doctrine (sections 1-5) and the gate-1 report and its QUERIES.log. I also read RESULT-HK1b.md, so this seat saw the certified values. It is not a blind seat.

Files:
- `QUERIES.log`: 87 logged query blocks plus 3 web queries. `lab.py searchcheck QUERIES.log` prints "search floor OK: every database with a zero-hit query has a passing positive control".
- Raw output: `out_batch1.txt`, `out_batch2.txt`, `out_batch3.txt`, and `newton_all.txt` (all 149 records of the Newton author, newest first).
- Helpers: `tools/`.
- Records opened: `src/`.

Newest dates covered:
- arXiv API: through submissions of 2026-11-16 (newest entry 2611.21603, gr-qc, 2026-11-16).
- INSPIRE: through records dated 2026-11-12.
- Zenodo: through records created 2026-11-17.

Instrument note: the Zenodo API returns HTTP 400 when the page size is above 25. Three author queries failed that way and are kept as `# known-bad` comments in the log. They were re-run correctly with tools/newton.py (paged, 25 per page).

## In plain words

Nothing new has appeared since gate-1 that touches the claim:
- Nobody has posted a computer-proved (interval or ball arithmetic) value for the photon power, the entropy rates, Page's beta or the Page time.
- Newton's Zenodo author list is unchanged at 149 records. His newest record (2026-11-16) is about Yamabe geometry, and his only Hawking record is still the 2026-09-16 graviton paper, in a single version.
- The INSPIRE citer counts are unchanged: Page 2013 has 411 citers, Page 1976 has 1544, Perez-Gonzalez 2025 has 14, and Calza-Spina 2611.15889 has 0.

The one new Hawking item is a Zenodo record posted today (Lee, 10.5281/zenodo.24319221). It is a floating-point re-check of a massless **scalar** field only, agreeing with benchmarks to about 1e-4. It is not certified and covers neither photons nor gravitons.

So, as of 2026-11-17:
- "First certified" holds for beta, the Page time, the photon power, alpha and both entropy rates.
- It does **not** hold for the graviton power. Newton certified that first, at about 1% width. Ours is a far tighter, independent enclosure that sits inside his.

Two wording problems need fixing before release:
1. "for a real black hole" overstates the model.
2. "+/- 7.8e-11" rounds the certified radius 7.81e-11 **down**.

## Table

| item | verdict | best source | label | quoted sentence | locator |
|---|---|---|---|---|---|
| Certified photon (s=1) greybody / power P_1, Schwarzschild | OPEN (floor 2026-11-17) | none found. The closest is Newton, zenodo.22800587 (graviton only). | OPENED (gate-1 copy) | "A targeted literature search did not identify a published certificate package combining these ingredients for the Schwarzschild graviton problem." His next steps: "carry the architecture to Kerr, superradiance, and additional quasinormal resonances". | gate-1/src/zenodo_22800587.txt l.554-557, l.588-590 |
| Newton photon follow-up since gate-1 | none | Zenodo creators.name:"Newton, Tony", 149 records, newest first | OPENED (metadata list) | Newest is "Exact Three-Pole Yamabe-Eta Exclusion ..." (2026-11-16). Only one Hawking record: "Proof-Carrying Schwarzschild Hawking Spectroscopy: Certified QNM Isolation and a Sub-1% Graviton Luminosity Enclosure" (2026-09-16). The versions endpoint shows 1 version. | gate-2/newton_all.txt l.1; Zenodo API /records/22800587/versions |
| Certified graviton power P_2 | TAKEN (by Newton, at 1% width). Ours is an independent, tighter enclosure. | Newton, zenodo.22800587 | OPENED (gate-1 copy) | "Theorem 3 ... 3.8262 x 10^-6 < M^2 P_grav < 3.8639 x 10^-6. The interval width is 3.77 x 10^-8." | gate-1/src/zenodo_22800587.txt l.515-523 |
| Certified alpha (total power) | OPEN (no enclosure of the total published); its graviton part is PARTIAL (Newton) | zenodo.22800587 | OPENED | as above, graviton term only | same |
| Certified entropy rates Sdot_1, Sdot_2 | OPEN | none found | - | - | QUERIES.log: INSPIRE fulltext "entropy production ratio" and "Hawking" (5 hits, none certified); arXiv `all:"Page time" AND all:certified` 0; Zenodo "Hawking radiation" AND certified 17 (titles read, none relevant) |
| Certified beta and Page time t*/t_decay | OPEN | none found | - | - | INSPIRE fulltext "1.484691" 0, "1.4846917" 0, "0.538102" 0 (control "1.48472" 5); Zenodo "1.48469" / "1.484691" / "1.4846917" / "0.538102" / "0.53810" all 0 (control "1.48472" 1) |
| Non-rigorous beta beyond Page | PARTIAL (unchanged) | Perez-Gonzalez arXiv:2502.04430 | OPENED (gate-1 copy) | "for heavier BHs, the entropy production ratio drops to beta = 1.48471, with a difference with the value given in Ref. [12] of 6.6 ppm" | gate-1/src/2502.04430.txt l.341-349 |
| New since gate-1: scalar Hawking re-verification | not overlapping | Lee, Zenodo 10.5281/zenodo.24319221 (2026-11-17) | ABSTRACT (record description) | "an independent numerical reverification of selected Hawking radiation calculations for a Schwarzschild black hole emitting one real massless scalar field into vacuum ... The computed scalar power coefficient differs from the published benchmark by approximately 0.01736%" | gate-2/src/zenodo_24319221.json, metadata.description |
| New since gate-1: KdV max-entropy greybody | not overlapping (non-rigorous, axial s=2) | arXiv:2611.21043 (2026-11-16) | ABSTRACT | "the resulting reconstruction agrees closely with the fourth-order Wentzel-Kramers-Brillouin (WKB) approximation across several multipoles" | arXiv API abstract |
| Calza-Spina 2611.15889 citers | none | INSPIRE refersto:recid:3228000 | OPENED (API) | TOTAL 0 | out_batch1.txt l.49-50 |
| Page 1976 citers since 2026-11-08 | none new | INSPIRE refersto:recid:113270 and de > 2026-11-08 | OPENED (API) | the only hit is 2611.15889, already read by gate-1 | out_batch3.txt |
| Page 2013 (1301.4995) citers | no new relevant | INSPIRE refersto:recid:1215583, 411 (unchanged) | titles read | newest: 2611.09859, 2611.18705 (2026-11-06). Both are model-specific (noncommutative RN particle production; regular black-hole thermodynamics). | out_batch1.txt l.6-32 |
| Perez-Gonzalez (2502.04430) citers | no new | INSPIRE refersto:recid:2877688, 14 (unchanged) | titles read | newest 2610.23606 (2026-10-16), already in gate-1's list | out_batch1.txt l.33-48 |

## (1) Decisive searches re-run since the gate

Everything below is logged in QUERIES.log.

**arXiv API (newest first).** Queries: greybody (411), graybody (34), "Page time" (194), "Hawking radiation" AND Schwarzschild (475), Regge-Wheeler (359), cat:gr-qc AND Hawking (5996, top 40 read through 2026-11-15), cat:hep-th AND Hawking AND Schwarzschild, PBH evaporation, emission rates. The only items dated after 2611.15889 that touch greybody factors or emission are:
- 2611.16120 (massive spin-3/2 on Kerr);
- 2611.21043 (KdV max-entropy greybody);
- 2611.14563 (BlackHawk BSM spectra).

All are ABSTRACT-read and none is certified or about Page constants. The certification-term queries returned 0 hits:
- `all:"interval arithmetic" AND all:"black hole"`;
- `all:"ball arithmetic" AND all:"black hole"`;
- `all:certified AND all:greybody`;
- `all:"Page time" AND all:certified/rigorous`.

`all:"computer-assisted" AND all:"black hole"` returned 3 hits, all known: 2609.21797, 2212.00194 and 1203.3766.

**INSPIRE.** Each check below gives the query and its hit count; the read-out follows the dash.
- **Citers.**
  - Page 2013 (`refersto:recid:1215583`, 411): no new relevant title.
  - Perez-Gonzalez 2502.04430 (`refersto:recid:2877688`, 14): no new citer.
  - Calza-Spina 2611.15889 (`refersto:recid:3228000`, 0): no citers yet.
  - Page 1976 (`refersto:recid:113270`, 1544 total; since 2026-11-08 only 2611.15889).
- **Full-text constants.**
  - "1.48469" (2): two plasma-photoemission papers, unrelated.
  - "1.484691" (0) and "1.4846917" (0).
  - "0.538102" (0); "0.53810" (3): Page 2013, a 2020 thesis "Aspects of Quantum Black Holes" (not opened, SNIPPET title only; dated 2020-08-28, older than every certification source in this gate) and one astro catalog.
  - "3.36385" (0).
- **Certification terms.**
  - "Page time" + interval arithmetic (0); + certified + greybody (0).
  - photon + greybody + ball arithmetic (0).
  - photon + greybody + interval arithmetic (2): both already screened by gate-1 (2611.03070, charged scalar QNM; recid 3210789).
  - `fulltext:"zenodo.22800587"` (0): nobody on INSPIRE cites Newton's record.

**Zenodo.**
- Newton author query: 149 records, all titles dumped (newton_all.txt). Fourteen match the Hawking / Schwarzschild / photon / entropy keywords. None is a photon greybody, photon luminosity, entropy-rate, beta or Page-time certificate, and none postdates 2026-09-16 (the Hawking-Page AdS "tomography" record of 09-12 is AdS thermodynamics).
- The constant queries are listed in the table above.
- `"greybody"`, newest first (78): the only Schwarzschild Hawking item in the last week is Lee 24319221 (scalar, float). The others:
  - 24186786 is a repost of the scalar-field graybody paper arXiv:2609.30020 (ABSTRACT: "We consider a minimally coupled massless scalar field").
  - 24214997 is a reproducibility package for the dCS analytic greybody paper.
  - 24166093 is a repost of 2611.16120.
  - 24063205 covers Floquet greybody factors for a charged scalar on Reissner-Nordström.
- `"Hawking radiation" AND certified` (17) and `"Hawking radiation" AND "interval arithmetic"` (4): titles read, none relevant. These are framework and theory-of-everything records.

**Web (3 queries).** No certified Page constant and no occurrence of "1.48469" / "1.484691".

## (2) Wording risks in the release claim

1. **"first certified ... Page time / beta / entropy rates / photon power"**: supported, as a search floor dated 2026-11-17. It is not a proof of absence. Keep "to our knowledge" and the date.
2. **"first certified ... graviton power"**: NOT allowed. Newton (Zenodo 10.5281/zenodo.22800587, 2026-09-16) certified it first, at 1% width.
   - Allowed: "an independent certified enclosure of the graviton power, about 2.7e7 times narrower than and contained in Newton's earlier certified interval".
   - Those figures come from our full width 2 x 6.95e-16 = 1.39e-15 against his 3.77e-8, and P_2 = 3.836739925e-6 lies inside [3.8262e-6, 3.8639e-6].
3. **"for a real black hole"**: overstated. The object is Page's idealised model: a Schwarzschild hole emitting only massless photons and gravitons into empty space (no incoming radiation, no neutrinos or massive species). Perez-Gonzalez places the photon-plus-graviton regime at "BH masses" heavier than about 1e26 g: "Neutrino emission is expected to become suppressed when M >~ 10^26 g, assuming the lightest neutrino to have a mass of 0.01 eV" (OPENED, gate-1/src/2502.04430.txt l.344-346). His own figure caption also marks the masses where "the temperature equals the Cosmic Microwave Background" (l.335-336). So "into empty space" is a statement about the model, not about any astrophysical hole; this gate did not open a source comparing the two masses numerically.
   - Allowed: "for a Schwarzschild black hole emitting photons and gravitons into empty space (Page's model)".
   - Not allowed: "for a real black hole" or "for real black holes".
4. **"Hawking entropy ledger"**: the word is free to use, but Newton already uses "certificate ledger" for his error budget (l.518: "the certificate ledger above implies"; also l.159 "Current certificate ledger."). To avoid a "same thing" reading, say "certified entropy rates and entropy ratio beta", or keep "ledger" out of the title.
5. **Error-bar rounding**:
   - beta: the brief's "+/- 7.8e-11" rounds the certified radius 7.81e-11 (RESULT-HK1b.md) **down**, which is not conservative. Write "+/- 7.81e-11" or round up ("+/- 7.9e-11" / "< 8e-11").
   - Page time: "+/- 9e-11" rounds 8.99e-11 up, which is fine.
6. **Page and Perez-Gonzalez**: say "settles the digits Page 2013 flagged as uncertain". Never say "Page was wrong" or "corrects Page". This is referee F7. Page's own words: "the last one or two digits probably are not significant but are given as a challenge for someone to do a higher-precision calculation" (gate-1 OPENED, page2013 l.205-212). The float value beta = 1.48471 (Perez-Gonzalez) lies outside our enclosure. State that neutrally, as a 6-digit float value at about 12 ppm (gate-1 normalisation), with no error claim.
7. **"certified"**: define it once as "interval/ball-arithmetic enclosures with rigorous truncation and tail bounds; computer-assisted proof; trust base python-flint 0.9.0 / Arb".

Exact allowed headline wording (as of 2026-11-17):
> "To our knowledge, the first certified (interval-arithmetic, rigorously error-bounded) enclosures of Page's evaporation constants for a Schwarzschild black hole emitting photons and gravitons into empty space: beta = 1.4846916919 +/- 7.81e-11 and Page time t*/t_decay = 0.5381024532 +/- 8.99e-11, together with certified photon power, total power alpha and photon and graviton entropy rates. The graviton power was certified earlier by Newton (Zenodo 10.5281/zenodo.22800587) to 1% width; our independent enclosure lies inside his interval and is about seven orders of magnitude narrower. The result settles the digits Page (2013) flagged as uncertain."

## (3) Did a certified PHOTON greybody or luminosity appear?

No, as of 2026-11-17:
- Newton's author list has no new Hawking record and his graviton record has one version.
- INSPIRE photon + greybody + ball/interval arithmetic gives 0 / 2 hits (both old and irrelevant).
- arXiv `all:certified AND all:greybody` returns 0, `all:"ball arithmetic" AND all:"black hole"` returns 0, and `abs:"photon luminosity" AND abs:Schwarzschild` returns 2 (both accretion-disk papers).
- The Zenodo photon / greybody / Arb, photon-luminosity and electromagnetic greybody Schwarzschild queries return 0, 0 and 7 (none certified).

## Most dangerous neighbour (unchanged)

**Tony Newton** (Zenodo). He has Arb Regge-Wheeler machinery for s = 2, and s = 1 changes one potential term. His stated next steps are compression, Kerr, superradiance and more QNMs, not photons or beta. There has been no Hawking activity from him since 2026-09-16, and his last two months are other topics.

On the float side, the BlackHawk/GrayHawk group: Perez-Gonzalez, and Calza-Spina 2611.15889 (no citers yet).

Not a race: if Newton posts photons, we credit him and narrow to the entropy side, beta and the Page time.

Method worth borrowing: none new beyond gate-1. Lee's record embeds SHA-256 execution receipts in the PDF, which is a packaging idea only.

## Genuinely open gap (one sentence)

As of 2026-11-17, nobody has published certified enclosures of the Schwarzschild photon power, total power alpha, photon and graviton entropy rates, beta or the Page time t*/t_decay (Page's photons-plus-gravitons model). Only the graviton power has been certified before, by Newton, at 1% width.

Suggested alias line (unchanged from gate-1, plus two):
`greybody | graybody | grey-body | gray-body | greybody factor | absorption probability | transmission probability | transmission coefficient | page evaporation factor | page factor | entropy production ratio | evaporation constant | page time | hawking luminosity`

## Gate lines

```
py -3.11 "<MEMCAP>" 1 py -3.11 "<LABTOOL>" gate <LAB> "certified beta and Page time t*/t_decay, Schwarzschild photons+gravitons into empty space (refresh 2026-11-17)" OPEN --file seats/gate-2/GATE-REFRESH.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-2/QUERIES.log
py -3.11 "<MEMCAP>" 1 py -3.11 "<LABTOOL>" gate <LAB> "certified photon (s=1) Hawking power and greybody, Schwarzschild (refresh 2026-11-17)" OPEN --file seats/gate-2/GATE-REFRESH.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-2/QUERIES.log
py -3.11 "<MEMCAP>" 1 py -3.11 "<LABTOOL>" gate <LAB> "certified photon and graviton Hawking entropy rates and total power alpha, Schwarzschild (refresh 2026-11-17)" OPEN --file seats/gate-2/GATE-REFRESH.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-2/QUERIES.log
py -3.11 "<MEMCAP>" 1 py -3.11 "<LABTOOL>" gate <LAB> "certified Schwarzschild graviton Hawking power (first done by Newton at 1% width; ours independent and tighter)" TAKEN --file seats/gate-2/GATE-REFRESH.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-2/QUERIES.log
py -3.11 "<MEMCAP>" 1 py -3.11 "<LABTOOL>" gate <LAB> "higher-precision non-rigorous beta beyond Page (refresh 2026-11-17)" PARTIAL --file seats/gate-2/GATE-REFRESH.md --source "arXiv:2502.04430" --queries <LAB>/seats/gate-2/QUERIES.log
```

Sources (web queries, SNIPPET only, none load-bearing):
- [arXiv 2606.08351](https://arxiv.org/pdf/2606.08351)
- [arXiv 0806.2209](https://ar5iv.arxiv.org/html/0806.2209)
- [arXiv 2605.28917](https://arxiv.org/html/2605.28917v1)
- [arXiv 2107.05218](https://arxiv.org/pdf/2107.05218)
- [arXiv 2003.08095](https://arxiv.org/pdf/2003.08095)
- [arXiv 2609.27908](https://arxiv.org/pdf/2609.27908)
