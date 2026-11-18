# GATE-HAWKING - prior-art gate, seat gate-1 (2026-11-17)

Seat: prior-art scout. I read the doctrine (sections 1-5) and SCOPE.md. I saw the recon's floating-point targets in COMPUTING.md; this is not a blind seat.
Files: QUERIES.log, which has 93 logged queries; `lab.py searchcheck` returns "search floor OK". Sources are in `src/` and the helper scripts in `tools/`.
Newest date covered: arXiv/INSPIRE through 2611.15889 (2026-11-11); Zenodo through records dated 2026-11-17.

## (1) In plain words

Someone has already put a computer-proved box around part of this. On 2026-09-16 an independent researcher (Tony Newton, Zenodo 10.5281/zenodo.22800587) posted a certified, ball-arithmetic enclosure of the total graviton Hawking power of a Schwarzschild hole. The interval is 3.8262e-6 < M^2 P_grav < 3.8639e-6, about 1% wide. He also posted certified greybody values at five graviton frequencies and certified interval "atlases" over two frequency bands.

Nobody has certified any of these:
- photons (s = 1);
- the entropy rates;
- beta, or the Page time;
- anything at more than about 2 digits.

Page's beta has been recomputed once in floating point, to 6 digits: Perez-Gonzalez 2025 gives 1.48471. Our recon gets 1.4846917, so the two disagree in the 6th digit, at 12 ppm. That disagreement needs resolving.

## (2) Verdicts

| item | verdict | best source | label | quoted sentence | locator |
|---|---|---|---|---|---|
| O1 certified Gamma_{s,l}(w), s=1,2 | PARTIAL | Newton, Zenodo 10.5281/zenodo.22800587 (2026-09-16) | OPENED | "The five dominant channels have independent pointwise Arb enclosures near their Hawking spectral peaks" (radii 1.98e-8 to 6.26e-7); "consecutive 0.02-wide parent intervals for l = 2 over 0.18 <= x <= 0.50" | src/zenodo_22800587.txt l.326-344 |
| O1 analytic one-sided bounds | (context) | Boonserm-Visser arXiv:0806.2209 | OPENED | "deriving rigourous bounds on the greybody factors as a function of S, L, wave frequency (omega), and the black hole mass" (lower bounds of the form T >= sech^2(...), not enclosures) | src/0806.2209.txt l.11, eqs.(10)-(11) |
| O2 alpha, beta, t_*/t_decay certified | PARTIAL | zenodo.22800587 | OPENED | "Theorem 3 ... 3.8262 x 10^-6 < M^2 P_grav < 3.8639 x 10^-6. The interval width is 3.77 x 10^-8." | l.515-523 |
| O2' photon power, entropy rates, beta, Page time certified | OPEN | (none found) | - | The same paper scopes itself to "the Schwarzschild graviton problem". Its next steps are "compress these residual budgets and extend ... to Kerr rotation, superradiant scattering, and higher resonances". | l.556, l.561-563 |
| O3 non-rigorous beta beyond Page | PARTIAL | Perez-Gonzalez arXiv:2502.04430 | OPENED | "the entropy production ratio drops to beta = 1.48471, with a difference with the value given in Ref. [12] of 6.6 ppm" | src/2502.04430.txt l.341-349 |
| O3 non-rigorous P_grav | PARTIAL | zenodo.22800587 | OPENED | "Two deliberately different numerical configurations give M^2 P_grav = 3.83673992684 x 10^-6 and 3.83673992972 x 10^-6" | l.453-458 |
| O3 alpha at about 5 digits (photon part) | context | Calza-Spina arXiv:2611.15889 | OPENED | Table 1 gives the Schwarzschild s=1 Page factor as "1.6819 x 10^-5" (GrayHawk); GrayHawk's stated accuracy is a "conservative value ... 10^-4" | src/2611.15889.txt l.534, l.587 |
| O3 Gray-Visser product integrals | context | arXiv:1512.05018 | OPENED | Truncation "was found to introduce an error of at worst O(10^-9)"; no Page constants are given. | src/1512.05018.txt l.465 |

**Normalisations** (converted to Page's convention: M = 1, all helicities, both parities):
- **Newton's graviton enclosure.** It contains Page's 3.836e-6 and the recon's 3.83673992496e-6. His two float configurations differ from the recon by 4.9e-10 and 1.24e-9 relative. The graviton term is 10.24% of alpha.
- **GrayHawk photon value.** The s=1 value is per degree of freedom. Doubled, it is 3.3638e-5, which is -1.6e-5 relative to the recon's 3.36385e-5.
- **beta.** Perez-Gonzalez's 1.48471 is +12.3 ppm from the recon's 1.4846917, and Page's 1.48472 is +19.1 ppm.
- **Perez-Gonzalez's per-dof entropy coefficients.** These are his eq.(18): 0.6338e-3 (s=1) and 0.0651e-3 (s=2). They are -6.0e-4 and +1.5e-3 relative to the recon's values. So his 4-digit components cannot by themselves secure his 6th digit.

The size of this tension makes it a vein, not a verdict (UNTESTED).

## (3) Classical mechanism and what certification adds

Every published Schwarzschild value comes from the same pipeline:
- the Regge-Wheeler ODE;
- flux conservation |A_in|^2 - |A_out|^2 = 1;
- the Chandrasekhar axial/polar duality (Newton reuses it, l.259-268);
- numerical quadrature of the Planck-weighted integrals.

That pipeline goes back to Page 1976, PRD 13, 198 (DOI 10.1103/PhysRevD.13.198; paywalled, read only through the lab's OCR of the thesis). Page's own accuracy statement (page2013.txt l.205-212) is that "the last one or two digits probably are not significant but are given as a challenge for someone to do a higher-precision calculation to find the error."

Certification would add four things:
- outward-rounded enclosures of every Gamma;
- rigorous l- and frequency-tail bounds;
- an enclosure of the entropy integrand (1+N)ln(1+N) - N ln N, which Newton never touches;
- a closed-form propagation to beta and t_*/t_decay = 1 - (beta/(1+beta))^{3/2}.

Newton shows the architecture works for s = 2. He uses Arb and the Riccati/Jost charts, and closes the infinite tails with comparison bounds of the form Gamma = sech^2(rapidity) (l.394-447). His width, though, is set by one-sided infrared and high-l allowances (l.559-561).

Method worth borrowing: his compactified high-l tail certificates, eqs.(37)-(38). These are 31,309 and 13,234 Arb leaf boxes, which close the l >= 20 sector independently of the ODE. Also reusable: Goldstein-Jejjala arXiv:2609.21797 (ABSTRACT: "a compact core enclosed by a parameter dependent Taylor model with directed rounding"), which treats the horizon series plus the asymptotic tail as a fixed-point problem.

## (4) Most dangerous neighbour

**Tony Newton**, Zenodo 22800587 (2026-09-16). He already has Arb Regge-Wheeler machinery for s = 2. Photons use the same equation with a different potential term, so a certified photon luminosity is one step away for him. His stated next steps, however, are compression plus Kerr, not photons or beta.

His author query on Zenodo returns 149 records. Twelve of them match Hawking/Schwarzschild/photon terms (titles read). None of those 12 is a photon or Page-constant certificate.

Non-rigorous side: the BlackHawk/GrayHawk group (Arbey, Calza, Perez-Gonzalez) is most likely to publish further digits:
- 2502.04430 (beta 1.48471);
- 2611.15889 (Page factors, 2026-11-11).

Their codes run at about 1e-4 accuracy (2606.06339 l.835: "order of 10^-4 in all the cases").

Not a race: if the lead feels that Newton is "one step" from photons, the lab's distinct edge is the entropy side and beta.

## (5) One open edge and ceiling

**Open edge.** Certified, tight (10+ digit) enclosures are still missing for:
- the photon power;
- both entropy rates;
- beta, and with it the Page time t_*/t_decay.

Settling the 6th digit of beta (Page 1.48472 / Perez-Gonzalez 1.48471 / recon 1.48469) with a proof is part of the same edge.

**Ceiling.** The first certified Page constants of a real black hole: a reference table that closes Page's 2013 "challenge". It changes no physics, and the graviton half of the engine is no longer first.

## Search floor (summary)

INSPIRE:
- titles, abstracts and full text for interval/rigorous/certified x greybody/Regge-Wheeler/Hawking;
- full text "1.48469", "1.4846", "3.7475", "0.538102", "1.48471";
- every citer of 1301.4995 (411), Page 1976 (1544), hep-th/0409024 (408) and 0806.2209 (164), keyword-screened;
- citers of 2502.04430 and 2502.17240.

arXiv API: 26 queries. Zenodo: 26 queries, including author queries. Web: 2 queries.

Instrument note: INSPIRE fulltext:"1.4847" (32 hits) does not return 2502.04430. Only the exact token "1.48471" finds it, so the recon's floor missed it.

Not opened:
- Page 1977 (PRD 16, 2402);
- MacGibbon-Webber;
- Teukolsky-Press;
- any rigorous-MST work (none found: arXiv abs:"greybody" AND abs:"Mano" returned 0);
- Mezzarobba's rigorous D-finite continuation, arXiv:1407.2802 (SNIPPET, title only).

Alias line suggested for selfcite-aliases.txt:
`greybody | graybody | grey-body | gray-body | greybody factor | absorption probability | transmission probability | transmission coefficient | page evaporation factor | page factor | entropy production ratio | evaporation constant`

## (6) Gate lines

```
python "<MEMCAP>" 1 python "<LABTOOL>" gate <LAB> "O1 certified Schwarzschild greybody factors s=1,2 at arbitrary frequency" PARTIAL --file seats/gate-1/GATE-HAWKING.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-1/QUERIES.log
python "<MEMCAP>" 1 python "<LABTOOL>" gate <LAB> "O2 certified Page constants alpha, beta, Page time (graviton luminosity already certified at 1% width)" PARTIAL --file seats/gate-1/GATE-HAWKING.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-1/QUERIES.log
python "<MEMCAP>" 1 python "<LABTOOL>" gate <LAB> "O2' certified photon power, entropy rates, beta and Page time t*/t_decay for Schwarzschild" OPEN --file seats/gate-1/GATE-HAWKING.md --source "zenodo:10.5281/zenodo.22800587" --queries <LAB>/seats/gate-1/QUERIES.log
python "<MEMCAP>" 1 python "<LABTOOL>" gate <LAB> "O3 higher-precision non-rigorous recomputation of alpha and beta" PARTIAL --file seats/gate-1/GATE-HAWKING.md --source "arXiv:2502.04430" --queries <LAB>/seats/gate-1/QUERIES.log
```
