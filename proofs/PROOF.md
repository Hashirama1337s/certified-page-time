# PROOF-HK: the bounds behind the BAR-HK-1b certificate

Build seat build-1, 2026-11-17. Written for referee-1 fixes F1, F2, F3, F5 and F7 (`seats/referee-1/REFEREE-HK1b.md`).

**Scope.** This note writes down the mathematics that the instrument `hk1b_cert.py` (instrument sha256 `3aa86d51…`) implements. It was written after the run. It changes no code and no sealed result. Code locators (`file:function`) point to the pinned files.

**Notation.**
- M = 1 and f = 1 - 2/r. The tortoise coordinate is x = r* = r + 2 ln(r/2 - 1).
- L = l(l+1) and c = 2(1 - s²) for Regge-Wheeler (RW).
- V = f (L/r² + c/r³) ≥ 0 for every channel used (s = 1: c = 0; s = 2: c = -6 and Lr > 6).
- The wave equation is ψ_xx + (w² - V) ψ = 0.
- n(w) = 1/(e^{8πw} - 1), N = Γ n, and S(N) = (1+N) ln(1+N) - N ln N.

## 0. Definitions and the quantity enclosed

- ψ is the ingoing horizon solution, ψ ~ e^{-iwx} (|ψ| → 1) as x → -∞.
- u_± ~ e^{±iwx} as x → +∞, so ψ = A u_- + B u_+ and Γ = 1/|A|².
- The tortoise Wronskian W_x(φ, χ) = f (φ χ' - φ' χ) (prime = d/dr) is constant for any two solutions.
- W_x(u_-, u_+) = 2iw, hence **A = W_x(ψ, u_+)/(2iw)** (`hkcore:point_solve`, `hkcore:_jet_solve_once`).
- Flux gives |A|² - |B|² = 1, so |A| ≥ 1.

**Normalisation check.** Near the horizon, x = r* ≈ 2 + 2 ln((r-2)/2), so e^{-iwx} = e^{-2iw}·2^{2iw}·(r-2)^{-2iw}. The Frobenius solution (r-2)^{-2iw}(1 + …) therefore equals e^{-iwx} times a unimodular constant (real w). This does not change |A|.

## 1. Horizon start: tail majorant (`hkcore:frob_coeffs`, `frob_tail`, `frob_majorant`)

**Series.** With x = r - 2, the ODE in r-form, P2 ψ'' + P1 ψ' + (P0a + w² P0b) ψ = 0, has P2 = x² p2(x) and P1 = x p1(x). The ingoing solution is ψ = x^ρ Σ a_n xⁿ with ρ = -2iw, a_0 = 1 and

  a_n F_0(n+ρ) = -Σ_{j=1}^{J} a_{n-j} F_j(n-j+ρ),   where F_j(σ) = σ(σ-1) p2_j + σ p1_j + p0a_j + w² p0b_j.

The structure p1_0 = p2_0, p0a_0 = 0 and p0b_0 = 4 p2_0 is asserted exactly in `Eq.__init__`. It gives

  F_0(n+ρ) = p2_0 n (n - 4iw)   (sympy check (2) in `sym_checks.py`).

**Claim.** Fix N and wmax ≥ |w|, and put u = 2 wmax/(N+1). Define

  β_j = [ |p2_j|(1+u)² + (|p2_j| + |p1_j|)(1+u)/(N+1) + (|p0a_j| + wmax² |p0b_j|)/(N+1)² ] / [ |p2_0| (1 - 4 wmax/(N+1)) ].

If ζ satisfies Σ_j β_j ζ^{-j} ≤ 1 (checked in arb) and A = max_{N-J<k≤N} |a_k| ζ^{-k}, then |a_n| ≤ A ζⁿ for every n > N.

**Proof.**
1. For n ≥ N+1 and any j ≥ 0: |n - j + ρ| ≤ n + 2wmax ≤ n(1+u).
2. Also |n - 4iw| ≥ n - 4|w|. So |F_j(n-j+ρ)|/|F_0(n+ρ)| ≤ β_j, by dividing numerator and denominator by n².
3. Induction: |a_n| ≤ Σ_j β_j |a_{n-j}| ≤ A ζⁿ Σ_j β_j ζ^{-j} ≤ A ζⁿ.

**Tails.** With y = ζ x0 < 1 (checked):
- Σ_{n>N} |a_n| x0ⁿ ≤ A y^{N+1}/(1-y).
- Σ_{n>N} |n+ρ| |a_n| x0ⁿ ≤ A [ y^{N+1}((N+1) - N y)/(1-y)² + 2wmax y^{N+1}/(1-y) ].
- Both are multiplied by |x0^ρ| = e^{2 Im(w) ln x0}, and the second also by 1/x0.

**Uniform version over a w-set** (`frob_majorant`). |a_n| ≤ A_n, where A_n solves the absolute recurrence with |σ| ≤ n - j + 2wmax and

  |n - 4iw| ≥ sqrt( max(0, n - 4 Im_max)² + 16 Re_min² ).

This bound is positive because the disk |w - w0| ≤ w0/2 has Re w ≥ w0/2 > 0. It is the same induction, applied term by term.

## 2. Transfer to R: one Taylor step (`hkcore:taylor_step`, `step_tail_factors`, `seg_sigma_rate`)

**Step data.** A step runs on [a, a+h] with exact dyadic a and h. The disk radius is ρ1 = 4h ≤ (3/4)(a-2), so every r in the disk has |r - 2| ≥ (a-2)/4 > 0. Write the system as Y = (ψ, ψ'/σ) for any σ > 0:

  Y' = 𝒜 Y,   𝒜 = [[0, σ], [-q/σ, -p]],   p = P1/P2,   q = P0/P2.

**(a) Cauchy/Gronwall truncation bound.**
1. On the complex disk |t| ≤ ρ1, use the 2-norm and the Frobenius norm ‖𝒜‖_2 ≤ ‖𝒜‖_F ≤ sqrt(2Q + P²), with σ_c = sqrt(Q), Q ≥ sup|q| and P ≥ sup|p|. The sups are bounded factor by factor: |r| ≥ Re r ≥ a - ρ1, |r-2| ≥ a - 2 - ρ1 and |r| ≤ a + ρ1 (`Eq.pq_sup`).
2. Gronwall along each ray from a gives |Y(t)| ≤ |Y(a)| e^{ρ1 sqrt(2Q+P²)} =: M on the disk.
3. Cauchy's estimate then gives |ψ_k| ≤ M ρ1^{-k} and |ψ'_k| ≤ σ_c M ρ1^{-k}.
4. Truncating after the u^N term at |t| ≤ h = ρ1/4 leaves:
   - |δψ| ≤ M 4^{-(N+1)}/(3/4)
   - |δψ'| ≤ σ_c M 4^{-N}/(3/4)

   The derivative series stops at index N-1.

**(b) Growth on the real segment: log-norm.**
- Forward (increasing r): d|Y|²/dr = 2 Re(Y* 𝒜 Y) ≤ 2 μ |Y|², with μ = λ_max((𝒜+𝒜*)/2).
- Here (𝒜+𝒜*)/2 = [[0, b̄], [b, -p]] with |b| = |σ² - q|/(2σ). Since p > 0 on real r > 2, μ = (-p + sqrt(p² + 4|b|²))/2 ≤ |b|.
- Backward (decreasing r): μ ≤ |b| + p.
- So the growth over the step is at most exp(h · sup|σ² - q|/(2σ)), plus p when going backward.
- With q = w² g1 - g2: |σ² - q| ≤ |σ² - (w0² g1 - g2)| + |w² - w0²| g1. Here |w² - w0²| ≤ δ(2w0 + δ) on the real panel and ρ_w(2w0 + ρ_w) on the disk.
- Changing basis between steps costs a factor max(1, σ_i/σ_{i+1}) forward, or its reciprocal backward.

Any σ > 0 is valid; the code only chooses σ for tightness.

**(c) Point mode.** The state is kept at exact midpoints. The error E (in the σ_i 2-norm) is carried through the **exact** step map:

  E_{i+1} ≤ e^{h·rate} E_i + (rounding radius + truncation bound)

Rounding enters through `crad`. This avoids the wrapping blow-up of naive ball stepping. Teeth: referee-1 T1.

## 3. Far field: Volterra bound with the re-derived constant (`hkcore:far_coeffs`, `far_residual_bound`)

**Setup.** Write u_+ = e^{iwr*} h. Then h satisfies

  Op h := f h'' + (f' + 2iw) h' - U h = 0,   U = V/f = N_U/(r³ D)

(sympy check (3)). Multiplying by r³D gives polynomial coefficients. Inserting h = Σ c_m r^{-m} gives the exact recurrence of `far_coeffs`; for RW it is 2iw m c_m = [(m-1)m - L] c_{m-1} - 2((m-1)² - s²) c_{m-2} (sympy check (5)).

**Residual.** For the truncation h_M, Res = Op h_M is a finite Laurent sum, computed exactly from the c_m, with powers t^{-k}, k ≥ M+2. With D(t) ≥ lead(D) t^{deg D} for t ≥ R:

  |Res(t)| ≤ Σ_k ρ̂_k t^{-k}.

**The error equation.** Let e = h - h_M and g = e'. Then

  (E g)' = E · F/f,   E = e^{2iwr*},   F = -f' g + U e - Res,

and |E(t)/E(r)| = 1 for real w. Put α = M+1, C_f = 1/(1 - 2/R) ≥ 1/f, and K_U ≥ sup_{t≥R} t²|U(t)|. On the space ‖g‖ = sup_{t≥R} t^α |g(t)|, with e(r) = -∫_r^∞ g so that |e(t)| ≤ ‖g‖ t^{1-α}/(α-1):

  |T g(r)| ≤ C_f ∫_r^∞ [ (2/t²) ‖g‖ t^{-α} + K_U t^{-2} ‖g‖ t^{1-α}/(α-1) + |Res(t)| ] dt.

So, with the referee's re-derived constant,

  **q = 2 C_f/((α+1) R) + C_f K_U/(α(α-1)) = 2 C_f/((M+2)R) + C_f K_U/((M+1)M)**

  F = C_f Σ_k ρ̂_k R^{α+1-k}/(k-1).

When q < 1 (checked):
- γ = F/(1-q)
- |e(R)| ≤ γ R^{-M}/M
- |e'(R)| ≤ γ R^{-(M+1)}

**Constant in the code.** The code uses q_code = 2C_f/((α+1)R) + **C_f²** K_U/(α(α-1)) ≥ q. A larger q gives a larger γ, so the code's bound is valid and conservative. (In the code's derivation, U e/f was bounded with a second 1/f ≤ C_f that the integrating factor does not need.)

**Uniqueness.** The fixed point gives an exact solution e^{iwr*}(h_M + e) with h → 1. On the real axis this is u_+: any other solution with h → 1 differs by a multiple of u_-, whose h-ratio e^{-2iwr*} does not converge.

Teeth: referee-1 T2.

## 4. η: Wronskian telescoping (`hkcore:uniform_bounds`, F1)

**What is computed.** The algorithm computes ψ_N(R) = T̃_n ⋯ T̃_1 ψ_N(r_0). Here T̃_i are the truncated step maps and ψ_N(r_0) is the truncated Frobenius start. A_M = W_x(ψ_N, u_M)(R)/(2iw), with u_M the truncated far solution. The true value is A = W_x(ψ, u_+)/(2iw).

**Telescoping identity.**

  ψ(R) - ψ_N(R) = Σ_i T_n⋯T_{i+1} δ_i + T_n⋯T_1 (ψ - ψ_N)(r_0),   δ_i = (T_i - T̃_i) ψ_N(r_{i-1}).

Each T_n⋯T_{i+1} δ_i is an exact solution through r_i. Because W_x is constant for exact solutions:

  W_x(T_n⋯T_{i+1} δ_i, u_+)(R) = W_x(δ_i, u_+)(r_i).

Hence

  2iw (A - A_M) = Σ_i W_x(δ_i, u_+)(r_i) + W_x(ψ - ψ_N, u_+)(r_0) + W_x(ψ_N, u_+ - u_M)(R).

**Bounds on each term.**
- |W_x(δ, u)| ≤ f (|δψ| |u'| + |δψ'| |u|).
- |δψ_i| and |δψ'_i| come from §2(a), with |Y_N(r_{i-1})| bounded by a forward product of (e^{h·rate} + truncation).
- |u_+(r_i)| and |u_+'(r_i)| come from a backward log-norm product (§2b) started at R with |u_+(R)| ≤ |h_M| + |e| and |u_+'(R)| ≤ |w|(|h_M| + |e|)/f + |h_M'| + |e'| (§3).
- The far term uses |u_+ - u_M| ≤ |e| and |(u_+ - u_M)'| ≤ |w||e|/f + |e'|.
- All bounds are taken uniformly over the real panel [w0 - δ, w0 + δ] (w as a real ball).
- Dividing by 2 min|w| gives η.

Empirical check: referee-1 found η ≫ |A - P| (9e-16 against 7e-20).

## 5. Taylor model on a panel (`hkcore:jet_solve`, `uniform_bounds`; `hk1b_quad:panel_integrals`)

**Taylor model of A.**
- A_M(w) is a fixed composition of polynomials in w, w², 1/w and exp. It is analytic on the closed disk |w - w0| ≤ ρ_w = w0/2, which stays clear of w = 0 and of the Frobenius poles w = -in/4, because Re w ≥ w0/2.
- Its Taylor coefficients at w0 (`acb_series`, length 64 = ctx.cap; longer requests are refused) are enclosures A_k.
- With B ≥ sup_{|w-w0|=ρ_w} |A_M| (from §1-2 uniform bounds on the complex disk box, plus |e^{iwr*}| ≤ e^{ρ_w r*}) and μ = δ/ρ_w = 1/5, Cauchy gives:

  A(w0 + ε) ∈ Σ_{k<64} A_k ε^k + disc(r_A),   r_A = B μ^64/(1-μ) + η,   for real |ε| ≤ δ.

**Γ.**
- With P(ε) = Σ A_k ε^k and Q = |P|² (exact real convolution, scaled u = ε/δ): Γ = 1/|A|².
- Because |A| ≥ max(1, sqrt(Q_min) - r_A) =: ℓ and ||P| - |A|| ≤ r_A:

  Γ/Γ_P ∈ [1 - e_G, 1 + e_G],   e_G = ((ℓ + r_A)/ℓ)² - 1.

**Integrands (all real-analytic where Q > 0 and N > 0).** F_P = w n Γ_P, F_S = S(n Γ_P) and F_N = n Γ_P.
- On each sub-interval c ± h (in u), F = Σ_{k≤16} F_k t^k + R_16(t), with |R_16(t)| ≤ sup_ξ |F^{(17)}(ξ)|/17! · |t|^17 (Lagrange).
- The integral is Σ_{k even} F_k · 2h^{k+1}/(k+1) ± |F_17 enclosure| · 2h^18/18, times δ.

**v2 re-centring.** Q is first shifted to the exact point c: Q_c(t) = Q(c + t), using all coefficients, with rounding radii only. The ball t ∈ [-h, h] is then evaluated on Q_c. This is the same polynomial (exact algebra). It removes the cancellation that made the v1 ball enclosure of Q contain 0 on turn-on panels. A sub-interval is halved until its remainder is ≤ 1e-15 of its value; depth ≥ 9 means refusal.

**Error from r_A.**
- P: ∫ F_P(true) ∈ ∫ F_P (1 ± e_G).
- S: S is increasing, with S'(N) = ln(1 + 1/N). For N ∈ N_P [1 - e_G, 1 + e_G], |S(N) - S(N_P)| ≤ e_G N_P (ln(1 + 1/N_P) + 2 e_G) ≤ e_G S(N_P) + 2 e_G² N_P, using N ln(1 + 1/N) ≤ S(N).
- Referee note: concavity of S gives the sharper e_G S(N_P). The extra term is safe.

## 6. Band bounds: sech², speed bound, triangle step (`hkbounds:gamma_band_bound`)

**Representation.** Write ψ = a e^{-iwx} + b e^{iwx}, ψ_x = -iw a e^{-iwx} + iw b e^{iwx}. Then

  a_x = -(V/(2iw)) e^{iwx} ψ,   b_x = (V/(2iw)) e^{-iwx} ψ,

and |a|² - |b|² = 1. Put |a| = cosh T and |b| = sinh T, with z = b/a in the unit disk and d(0, z) = 2 artanh|z| = 2T. Then Γ = 1/|a(∞)|² = sech² T(∞).

**(i) Speed bound.**
- d|a|²/dx = 2 Re(ā a_x) = -(V/w) Re(i ā b e^{2iwx}), since Re(i|a|²) = 0.
- So |d|a|²/dx| ≤ (V/w) |a||b|, that is, 2 cosh T sinh T |T'| ≤ (V/w) cosh T sinh T.
- Hence |T'| ≤ V/(2w), and 2T moves by at most ∫ V/w.

**(ii) Transfer and triangle step.**
- The (a, b) transfer over [x_a, x_b] is M = P(x_b)^{-1} N_x P(x_a), where P(x) = P0 E(x), P0 = [[1, 1], [-iw, iw]] and E = diag(e^{-iwx}, e^{iwx}).
- N_x is the real fundamental matrix of y'' = (V - w²) y in the (y, y_x) basis, with det 1.
- The generator [[iV/2w, iVe^{2iwx}/2w], [conj, conj]] lies in su(1,1), so M ∈ SU(1,1) acts on z as a disk automorphism.
- Write N' = P0^{-1} N_x P0 = E_b M E_a^{-1}. It is in SU(1,1) with tr N' = tr N_x.
- E_a and E_b are rotations about 0, so d(0, ·) is invariant under them.
- A hyperbolic isometry moves every point by at least its translation length ℓ = 2 arccosh(|tr|/2). Therefore, with y = E_a z_a:

  2T_b = d(0, N' y) ≥ d(y, N' y) - d(0, y) ≥ ℓ - 2T_a.

- Combining with (i):

  **2T(∞) ≥ 2 arccosh(tr N_x / 2) - (1/w)[ ∫_{-∞}^{x_a} V dx + ∫_{x_b}^{∞} V dx ]**

- The shoulder integrals are exact: ∫_{-∞}^{x_a} V dx = L d/(2r_a) + c d (r_a + 2)/(8 r_a²) with d = r_a - 2, and ∫_{x_b}^{∞} V dx = L/r_b + c/(2r_b²).
- In the (y, y_x) basis, tr N_x = N_11 + (f_b/f_a) N_22 when computed from an r-basis matrix. The cells are built directly in x.

**(iii) Comparison.** On each core cell j (exact tortoise length h_j), V - w² ≥ q_j ≥ 0. Here q_j comes from a certified monotone or interval lower bound of V and is checked ≥ 0; the sign of r⁵V' = -2Lr² + (6L - 3c)r + 8c is checked in arb (sympy check (1)). Then

  N_x ≥ Π_j C_j entrywise, with C_j = [[cosh a_j, sinh a_j/√q_j], [√q_j sinh a_j, cosh a_j]] and a_j = √q_j h_j.

The C_j are nonnegative (q_j = 0 gives [[1, h], [0, 1]]), so tr N_x ≥ tr Π C_j (§7). For a band [w_lo, w_hi], q_j uses w_hi (V - w² decreases in w) and the shoulders use 1/w_lo.

## 7. F2: comparison theorem for y'' = Q y, self-contained proof

**Lemma.** Let Q ≥ q ≥ 0 be piecewise continuous on [x_0, x_1]. Let N_Q and N_q be the fundamental matrices of Y' = A_Q Y, with A_Q = [[0, 1], [Q, 0]], Y = (y, y'), and N(x_0) = I. Then N_Q(x) ≥ N_q(x) ≥ 0 entrywise. Consequently, for nonnegative matrices, products are monotone in each factor and tr N_Q ≥ tr N_q.

**Proof.**
1. *Nonnegativity.* N_q is the limit of the Picard iterates N^{(k+1)}(x) = I + ∫_{x_0}^x A_q N^{(k)}. Since A_q ≥ 0 entrywise and N^{(0)} = I ≥ 0, every iterate is ≥ 0, so the limit is too. The Peano-Baker series converges absolutely for bounded A.
2. *Difference.* D = N_Q - N_q satisfies D' = A_Q D + (A_Q - A_q) N_q with D(x_0) = 0. By variation of constants, D(x) = ∫_{x_0}^x N_Q(x, s) (A_Q - A_q)(s) N_q(s) ds. Here N_Q(x, s) ≥ 0 (step 1 applied from s), A_Q - A_q = [[0, 0], [Q - q, 0]] ≥ 0, and N_q ≥ 0. So D ≥ 0.
3. *Cells.* For piecewise-constant q (cells), N_q = Π C_j with the cell matrices C_j of §6(iii). If 0 ≤ A ≤ A' and 0 ≤ B ≤ B', then AB ≤ A'B'.

∎

Standard Sturm-type comparison; this proof is self-contained, so no external citation is relied on.

## 8. The l > 60 lemma and the far-cell extension (`hkbounds:lemma_band`, `large_l_lemma`, `large_l_tail_sum`; F3)

**Setting.** s = 1 and 2 (c ≤ 0). Let U = f/r² and L' = L - 3. Since c/r³ ≥ -6/r³ ≥ -3/r² for r ≥ 2, V ≥ L' U. With w = w̃ √L', V - w² ≥ L'(U - w̃²).

**Band [w̃_lo, w̃_hi].**
- Use cells with U - w̃_hi² ≥ q̃_j ≥ 0 between r_a and r_b.
- Comparison with constant cells, using (ΠC)_11 ≥ Π cosh a_j for nonnegative matrices and cosh a ≥ e^a/2, gives

  arccosh(tr/2) ≥ ln Π cosh(√(L' q̃_j) h_j) ≥ √L' S̃ - n ln 2,   S̃ = Σ √q̃_j h_j.

- Shoulders (c ≤ 0, V ≥ 0): ∫ V ≤ L [(1/2 - 1/r_a) + 1/r_b], and w ≥ w̃_lo √L'. With L/√L' ≤ √L' (1 + 3/L'_min):

  2T ≥ √L' G - 2n ln 2,   G = 2S̃ - (1 + 3/L'_min) [(1/2 - 1/r_a) + 1/r_b]/w̃_lo.

- Then Γ ≤ sech² T ≤ 4 e^{-2T}.

**Bands.** Bands run from w̃_max = 0.1 down to w̃_min = 0.02 with ratio 1.05, each certified G_k > 0.

**Far-cell extension (w̃ ≤ w̃_min).**
- *Base cells.* Take the base cells where U ≥ (1.5 w̃_min)² on [r_a0, r_b0]. They remain valid for every w̃ ≤ w̃_min, since q̃ only grows as w̃ falls.
- *Sub-band J ≥ 0.* For w̃ ∈ (w̃_min ρ^{-(J+1)}, w̃_min ρ^{-J}] with ρ = 2, add far cells j = 0, …, J-1 on [r_b0 ρ^j, r_b0 ρ^{j+1}].
  - On cell j, U ≥ f(r_b0)/(r_b0² ρ^{2j+2}), because f increases and r ≤ r_b0 ρ^{j+1}.
  - Also w̃² ≤ w̃_min² ρ^{-2(j+1)}.
  - So U - w̃² ≥ (f0 - (w̃_min r_b0)²)/(r_b0² ρ^{2j+2}) with f0 = f(r_b0); the discriminant is checked > 0.
  - Since h_j ≥ Δr (dx/dr = 1/f ≥ 1), each far cell contributes √q̃_j h_j ≥ s_far = ((ρ-1)/ρ) sqrt(f0 - (w̃_min r_b0)²).
- *Right shoulder* starts at r_b(J) = r_b0 ρ^J, so (1/r_b(J))/w̃_lo(J) ≤ ρ/(w̃_min r_b0), independent of J.
- *Left edge* moves to r_a(J) = 2 + 9 w̃_hi(J)². The region [r_a(J), r_a0] is one q = 0 cell (factor [[1, h], [0, 1]] ≥ 0). It is valid because U is increasing on (2, 3], (2 + 9w̃²)³ ≤ 9 implies U(r_a(J)) ≥ w̃², and 9(w̃_min/ρ)² ≤ r_a0 - 2 with r_a0 ≤ 3 (all checked).
- Its shoulder is (1/2 - 1/r_a(J))/w̃_lo ≤ (9/4) ρ w̃_hi ≤ max(ρ IL0/w̃_min, (9/4) w̃_min) =: NT.
- *Exponent.* E(J) = [√L' G0 - 2 n_base ln 2] + J [2√L' s_far - 2 ln 2], with G0 = 2S̃_base - (1 + 3/L'_min)(NT + ρ/(w̃_min r_b0)).
- slope_ok means √L'_min s_far ≥ ln 2, checked. Then E(J) ≥ E(0) for every J ≥ 0, and the J = 0 bound covers all w̃ ≤ w̃_min.

**Summation.**
- Let Gs = min_k G_k and m* = min_k [L_big (G_k - Gs) - 2 n_k ln 2]. Since √L' ≥ l - 1 ≥ L_big:

  Γ_l(w) ≤ K e^{-Gs (l-1)},   K = 4 e^{-m*},   for w ≤ w̃_max √L'.

- Planck tails cover w ≥ w̃_max √L'.
- Per-mode integrals:
  - ∫_0^∞ w n = 1/384.
  - ∫_0^W S(ε n) dw ≤ w*(2 ln 2 + 1) + w*((1 + ln 2) Λ + Λ²/2), with w* = ε/(8π) and Λ = ln(W/w*), using n ≤ 1/(8πw), S(x) ≤ ln(1+x) + 1, ∫_0^1 ln(1 + 1/u) du = 2 ln 2, and S(x) ≤ x(1 + ln 2 + ln(1/x)) for x ≤ 1.
- Each series in l is bounded by its first term over (1 - ratio), with explicit ratio bounds that decrease in l.

Certified values: Gs = 1.7142737 and K = 7.74e25. The tails are P ≤ 2.06e-20 and S ≤ 1.75e-15 summed over both helicities, per spin. Teeth: `c9_teeth_hk1b.py` (F4, §11).

## 9. Planck tails and entropy monotonicity (`hkbounds`)

- 1 + 1/n = e^{8πw} exactly. So S(n) = ln(1+n) + 8πw n (sympy checks (6)-(7)).
- With N ≤ n and S increasing (S'(N) = ln(1 + 1/N) > 0):
  - ∫_W^∞ S(N) ≤ e^{-8πW}(W + 2/(8π))/(1 - e^{-8πW})
  - ∫_W^∞ w N ≤ e^{-8πW}(W/(8π) + 1/(8π)²)/(1 - e^{-8πW})
  - ∫_0^ε S(n) ≤ ε(2 + ln(1 + 1/(8πε)))
- Band contributions: w n(w) is decreasing, so P_band ≤ G_max · width · w_lo n(w_lo). Also S_band ≤ width · S(G_max n(w_lo)).
- On Taylor-model panels N > 0, and the two terms of S are evaluated as series with no cancellation issue. Underflow would only widen a ball or force a refusal or fallback.

## 10. F5: stated constants of the v2 instrument (as used in the HOLD run, instrument sha256 3aa86d51…)

| constant | value | where |
|---|---|---|
| SKIP_P / SKIP_S (absolute panel skip, per mode, before g) | 1e-22 / 1e-20 | hk1b_channel.py |
| FALLBACK_BUDGET_P / _S (summed fallback width, per spin, after g = 2(2l+1)/(2π)) | 1e-15 / 1e-13 | hk1b_cert.py |
| IR stop (per-mode IR bound of (0, E]) | P < 1e-17, S < 1e-15 | hk1b_channel.run_channel |
| zero region | [0, 1e-20], Γ ≤ 1 | hkbounds.ir_region |
| W_HI (Planck tail above, Γ ≤ 1) | 205/128 | hkchannel.W_HI |
| L_T / L_BIG | 9 / 60 | hk1_cert.py |
| panels | δ = w0/10 (edges × 9/11, dyadic), ρ_w = 5δ, μ = 1/5, jets 64 | hkchannel, hkcore |
| quadrature | K = 16, REL_REM = 1e-15, MAX_DEPTH = 9, ≥ 8 sub-intervals and h ≤ 0.08/(8π δ) | hk1b_quad |
| ODE | x0 = 0.25, κ = 4 (ρ1 = 4h ≤ 0.75(r-2)), step tol_rel 1e-24, wR = 25, prec 256 bits (jets double on demand) | hkcore |
| band bounds | cell ratio 1.08, band ratio 2 below 0.05 and 1.05 above | hkbounds |
| lemma | w̃_max = 0.1, w̃_min = 0.02, band ratio 1.05, ρ = 2, cell ratio 1.1, base core U ≥ (1.5 w̃_min)² | hkbounds |

**HOLD run usage.** The run used 321 Taylor-model panels, 1 skip and 0 fallbacks, with fallback widths 0 and 0. In `hk1b_cert.py` the field `within_budget` is recorded but does **not** feed any PH outcome. A future run could sealed-amend a rule such as: "if within_budget is false for a spin, PH1-PH3 and PH6 are INCONCLUSIVE". That would need a code change and is not done here.

## 11. F4: C9 with teeth (`c9_teeth_hk1b.py` → `c9_teeth_hk1b.json`)

The outcome is PASS only if all four checks hold:
- **A.** The honest lemma (L_big = 60) certifies.
- **B.** Certified point solves Γ_l(w) at 7 samples with l = 61-80 and w ≤ 0.1√L' are ≤ K e^{-Gs(l-1)}. Observed: Γ ≤ 2e-92 against ε ≥ 1e-33. The bound is loose but sound.
- **C.** An impossible configuration (w̃_max = 0.19) is refused.
- **D.** A falsified certificate (Gs × 4, K = 4) is caught by check B at 5 of the 7 points. This shows check B can fail.

Result: PASS (1.8 s).

## 12. F7: trust base and wording

**Trusted.**
- **Arb ball arithmetic** through **python-flint 0.9.0** (`arb`, `acb`, `acb_series`, `arb_series`; installed at `…/Python311/site-packages/flint`): correct rounding of +, -, ×, ÷, exp, log, sqrt, cosh, sinh and acosh. Also correct series truncation at `ctx.cap` = 64; longer jets are refused by `require_cap`, not truncated.
- **CPython 3.11.9** (MSC v.1938, 64-bit) executing the code as written. Python integers are exact (polynomial coefficients); floats are used only to *choose* positions, step sizes, N, σ and turning points. Every bound that matters is recomputed in arb.
- **sympy 1.14.0**, only for the identity checks in `sym_checks.py`, which are not inputs.
- The written proofs in this note. They are refereed by referee-1 (all CORRECT or CORRECT WITH FIXES) but not formally verified, for example not in Lean.

**Not trusted, and not used as input.** These enter only as controls:
- recon floats (positive control);
- Newton's interval (PH3 control);
- the referee's float engine;
- the blind MST seat.

**Page wording (referee framing).** Page 2013 itself estimates "about four or five digits" of accuracy and invites a higher-precision recomputation (<RECON>/seats/computing/papers/page2013.txt l.140-144 and l.219). The certified values settle his flagged-uncertain last digits:
- β ∈ 1.4846916919 ± 7.81e-11 excludes the printed 1.48472 and its rounding interval.
- Post hoc, not sealed: α, P_1 and P_2 also exclude Page's printed 3.7474e-5, 3.3638e-5 and 3.836e-6.

These should be reported as "Page's last digits, which he flagged as uncertain, are now settled", **not** as "Page's digits were wrong".

## Files

New in this pass: `PROOF-HK.md`, `c9_teeth_hk1b.py`, `c9_teeth_hk1b.json`, `rescore_hk1b.py`, `rescore_hk1b.json`. The pinned files are untouched.

## Annotations 2026-11-17 (lead, from seats/referee-1/REFEREE-HK1b-2.md; documentation only - no number or code changes)
- G1 (replaces the §8 left-edge sentence). The comparison is pointwise in w, so the cells may depend on w~. For w~ in
  (w~_min/rho, w~_min] take r_a = r_a0, giving left shoulder <= rho*IL0/w~_min; for w~ <= w~_min/rho take r_a = 2 + 9 w~^2,
  giving left shoulder <= (9/4) w~ <= (9/4) w~_min. Hence NT = max(rho*IL0/w~_min, (9/4) w~_min), exactly the code's value.
  Premise for J = 0: 9 w~_min^2 <= r_a0 - 2 holds (r_a0 - 2 = [0.00727890 +/- 1.44e-9]; referee lemma_edge_out.json). Numerically
  rho*IL0/w~_min = [0.181313 +/- 4.14e-7] >= (9/4) rho w~_min = 0.0900.
- G2. Control C9 parts B/D are a low-power soundness sample (they detect lemma errors larger than about 2x in the exponent); the
  l > 60 claim rests on the §8 proof, not on C9.
- Cosmetic: §6(i) sign should read d|a|^2/dx = +(V/w) Re(i conj(a) b e^{2iwx}) (only the modulus is used); §3 uses "F" for both a
  function and a constant; arccosh(tr/2) >= ln prod cosh uses both diagonal entries (both hold).
- Headline widths: quote the printed radii (beta +/- 7.81e-11), which are conservative.
