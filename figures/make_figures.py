"""Draw the README figures of certified-page-time from the data the repository ships.

Usage:  python figures/make_figures.py [--png]
Needs Python 3.11, matplotlib 3.11 and python-flint 0.9.0. Writes figures/*.svg next to this script; --png also writes
PNG previews into _preview/ (not shipped).

Every plotted number is read from shipped files:
  results/hk1b/result_hk1b.json   certified values (beta, Page time, P_1, P_2, Sdot_1, Sdot_2), closed forms
                                  (S_star_over_SBH0), per-channel enclosures (channel_status) and the l > 9 tail bounds
  results/blind/results.json      the blind second implementation's beta and its error estimate (not rigorous)
The printed betas of Page 2013 (1.48472) and Perez-Gonzalez 2025 (1.48471) are typed below with their source; they are
drawn as the intervals of numbers that round to them. The curves of the first figure are Page's closed-form model
(S_BH/S_BH(0) = (1 - t/t_decay)^(2/3), S_rad = beta (S_BH(0) - S_BH)) evaluated with the certified beta.
"""
import json
import os
import sys
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from flint import arb, ctx

ctx.prec = 200
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PRINTED = [("Page 2013 printed 1.48472", "1.48472"), ("Perez-Gonzalez 2025 printed 1.48471", "1.48471")]

# ---------------------------------------------------------------- brand style (lab figure style sheet)
BG, BORDER, GRID, AXC, TXT, ACC = "#1c2026", "#2f353d", "#22272e", "#9aa4ae", "#e8edf2", "#39ff14"
CAT = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9", "#e66767"]
W_IN = 12.5

plt.rcParams.update({
    "svg.fonttype": "none", "svg.hashsalt": "moki-julio",
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 16, "axes.labelsize": 17, "xtick.labelsize": 15, "ytick.labelsize": 15,
    "axes.facecolor": BG, "figure.facecolor": "none", "savefig.facecolor": "none",
    "axes.edgecolor": AXC, "axes.labelcolor": TXT, "xtick.color": AXC, "ytick.color": AXC,
    "text.color": TXT, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1.0,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "legend.fontsize": 14, "lines.linewidth": 2.0, "axes.axisbelow": True,
})
PNG = "--png" in sys.argv
SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def new_fig(h_in):
    fig = plt.figure(figsize=(W_IN, h_in))
    fig.patches.append(FancyBboxPatch((0.004, 0.006), 0.992, 0.988, boxstyle="round,pad=0,rounding_size=0.015",
                                      transform=fig.transFigure, facecolor=BG, edgecolor=BORDER, linewidth=1.5,
                                      zorder=-10))
    return fig


def title(fig, main, sub):
    h = fig.get_figheight()
    fig.text(0.035, 1 - 0.42 / h, main, fontsize=21, fontweight="bold", color=TXT, va="top")
    fig.text(0.035, 1 - 0.88 / h, sub, fontsize=15, color=AXC, va="top")


def save(fig, name):
    path = os.path.join(HERE, name)
    fig.savefig(path, format="svg", metadata={"Date": None, "Creator": None})
    with open(path, encoding="utf-8") as fh:
        svg = fh.read().replace("font-family: 'Segoe UI';", "font-family: 'Segoe UI', 'Helvetica', 'Arial', sans-serif;")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    if PNG:
        prev = os.path.join(ROOT, "_preview")
        os.makedirs(prev, exist_ok=True)
        fig.savefig(os.path.join(prev, name.replace(".svg", ".png")), format="png", dpi=144)
    plt.close(fig)
    print("wrote figures/" + name)


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def mid_rad(s):
    x = arb(s)
    return float(x.mid()), float(x.rad())


def sci_up(x, nd=1):
    """radius / width as 'm × 10ᵉ' with the mantissa rounded up (never understated)."""
    d = Decimal(repr(float(x)))
    e = d.adjusted()
    m = (d.scaleb(-e) * 10 ** nd).to_integral_value(rounding=ROUND_CEILING) / Decimal(10 ** nd)
    if m >= 10:
        m, e = m / 10, e + 1
    return "%.*f × 10%s" % (nd, m, str(e).translate(SUP))


def sci_down(x, nd=1):
    """a gap or lower bound as 'm × 10ᵉ' with the mantissa rounded down (never overstated)."""
    d = Decimal(repr(float(x)))
    e = d.adjusted()
    m = (d.scaleb(-e) * 10 ** nd).to_integral_value(rounding=ROUND_FLOOR) / Decimal(10 ** nd)
    return "%.*f × 10%s" % (nd, m, str(e).translate(SUP))


def ball_text(s):
    """'[1.4846916919 +/- 7.81e-11]' -> '1.4846916919 ± 7.81 × 10⁻¹¹' (the stored radius, digits unchanged)."""
    inner = s.strip()[1:-1]
    m, r = [t.strip() for t in inner.split("+/-")]
    rm, re_ = r.lower().split("e")
    return "%s ± %s × 10%s" % (m, rm, str(int(re_)).translate(SUP))


# ---------------------------------------------------------------- figure 1 (hero): the entropy ledger over a lifetime
def fig_page(r):
    beta_s, tstar_s = r["values"]["beta"], r["values"]["page_time"]
    sstar_s = r["closed_forms"]["S_star_over_SBH0"]
    beta = float(arb(beta_s).mid())
    tstar, sstar = float(arb(tstar_s).mid()), float(arb(sstar_s).mid())
    n = 600
    xs = [i / n for i in range(n + 1)]
    sbh = [(1 - x) ** (2 / 3) for x in xs]
    srad = [beta * (1 - y) for y in sbh]
    page = [min(a, b) for a, b in zip(sbh, srad)]

    fig = new_fig(8.6)
    title(fig, "When does a black hole stop being a one-way door?",
          "Schwarzschild black hole emitting photons and gravitons into empty space (Page's model), with our certified β")
    ax = fig.add_axes([0.085, 0.13, 0.86, 0.68])
    ax.plot(xs, page, color=CAT[2], lw=9, alpha=0.30, solid_capstyle="round", zorder=1)
    ax.plot(xs, sbh, color=CAT[0], lw=2.5, zorder=3)
    ax.plot(xs, srad, color=CAT[1], lw=2.5, zorder=3)
    ax.plot([tstar, tstar], [0.2, sstar], color=AXC, lw=1, ls=(0, (3, 3)), zorder=2)
    ax.plot([tstar], [sstar], "o", ms=12, mfc=ACC, mec=BG, mew=2, zorder=5)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.62)
    ax.set_xlabel("time since the start, as a fraction of the black hole's lifetime  t / t_decay")
    ax.set_ylabel("entropy  /  the black hole's starting entropy")
    ax.text(0.02, 1.07, "black hole (Bekenstein-Hawking entropy)", color=CAT[0], fontsize=15, va="center")
    ax.text(0.56, 1.47, "radiation (coarse-grained entropy)\nends at β = %.4f times the start" % beta,
            color=CAT[1], fontsize=15, ha="left", va="center")
    ax.text(0.44, 0.10, "Page curve if no information is lost\n(schematic: Page's assumption, not computed)",
            color=CAT[2], fontsize=14, ha="center", va="center")
    ax.annotate("Page time: t*/t_decay = %s\nentropy then %s of the start"
                % (ball_text(tstar_s), ball_text(sstar_s)),
                xy=(tstar, sstar), xytext=(0.02, 0.80), textcoords="axes fraction", fontsize=14, color=TXT,
                arrowprops=dict(arrowstyle="-", color=AXC, lw=1.2, relpos=(0.85, 0.0)))
    save(fig, "page-time.svg")


# ---------------------------------------------------------------- figure 2: beta against the printed values
def fig_beta(r, blind):
    bs = r["values"]["beta"]
    bm, br = mid_rad(bs)
    lo, hi = bm - br, bm + br
    fig = new_fig(8.4)
    title(fig, "Settling the digits Page flagged as uncertain",
          "β = entropy carried away by the radiation ÷ entropy lost by the black hole")
    ax = fig.add_axes([0.06, 0.53, 0.90, 0.25])
    ax2 = fig.add_axes([0.06, 0.12, 0.90, 0.22])
    x0, x1 = 1.484684, 1.484730
    rows = []
    for i, (lab, s) in enumerate(PRINTED):
        d = Decimal(s)
        h = Decimal(1).scaleb(d.as_tuple().exponent) / 2
        a, b = float(d - h), float(d + h)
        y = 1.55 - i * 1.0
        ax.add_patch(Rectangle((a, y - 0.2), b - a, 0.4, facecolor=CAT[1 + 2 * i], alpha=0.30,
                               edgecolor=CAT[1 + 2 * i], lw=1))
        if i == 0:
            ax.text(b, y + 0.38, lab + " (every number that rounds to it)", color=CAT[1], fontsize=13,
                    ha="right", va="center")
        else:
            ax.text(a, y + 0.38, lab + " (every number that rounds to it)", color=CAT[3], fontsize=13,
                    ha="left", va="center")
        rows.append((a, b))
    ax.axvline(bm, color=ACC, lw=2.5)
    ax.text(bm - 0.0000006, 1.15, "certified β\n" + ball_text(bs) + "\n(a box %s wide,\nthinner than this line)"
            % sci_up(2 * br), color=ACC, fontsize=13, ha="right", va="center")
    gap = rows[1][0] - hi
    ax.annotate("", xy=(rows[1][0], -0.05), xytext=(hi, -0.05),
                arrowprops=dict(arrowstyle="<->", color=AXC, lw=1.2))
    ax.text((hi + rows[1][0]) / 2, -0.38, "gap more than %s" % sci_down(gap, 2), color=AXC, fontsize=13,
            ha="center", va="center")
    ax.set_xlim(x0, x1)
    ax.set_ylim(-0.65, 2.15)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ticks = [1.484690, 1.484700, 1.484710, 1.484720, 1.484730]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["%.6f" % t for t in ticks])
    ax.set_xlabel("β", labelpad=2)

    # zoom: the certified box and the blind value
    c = float(Decimal(bs.strip()[1:-1].split("+/-")[0].strip()))
    sc = 1e10
    ax2.add_patch(Rectangle(((lo - c) * sc, 0.25), (hi - lo) * sc, 0.5, facecolor=ACC, alpha=0.30, edgecolor=ACC, lw=1))
    ax2.text((hi - c) * sc + 0.05, 0.62, "certified box (computer proof)", color=ACC, fontsize=13, va="center")
    b = blind["beta"]
    bv, be = float(Decimal(b["value_raw_B"])), float(b["abs_error_estimate"])
    ax2.errorbar([(bv - c) * sc], [0.38], xerr=[[be * sc], [be * sc]], fmt="D", ms=9, color=CAT[0], mec=BG, capsize=4)
    ax2.text((hi - c) * sc + 0.05, 0.36, "blind independent check (different method, not rigorous): %s"
             % b["value_13sig"], color=CAT[0], fontsize=13, va="center")
    ax2.set_xlim(-1.4, 3.6)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    ax2.set_xlabel("zoom ×100,000:  (β − %s) in units of 10⁻¹⁰" % bs.strip()[1:-1].split("+/-")[0].strip())
    fig.text(0.06, 0.405, "Zoomed in", color=AXC, fontsize=14)
    save(fig, "beta-number-line.svg")


# ---------------------------------------------------------------- figure 3: where the power and the entropy come from
def fig_modes(r):
    ch = r["channel_status"]
    ls = list(range(1, 10))
    data = {}
    for key, row in ch.items():
        s, l = (int(x) for x in key.split(","))
        g = arb(2 * (2 * l + 1)) / (2 * arb.pi())
        P, S = g * arb(row["P_mode"]), g * arb(row["S_mode"])
        data[(s, l)] = ((float(P.mid()), float(P.rad())), (float(S.mid()), float(S.rad())))
    tails = {s: (float(arb(r["tails"][str(s)]["P"]).upper().mid()), float(arb(r["tails"][str(s)]["S"]).upper().mid()))
             for s in (1, 2)}
    v = r["values"]
    fig = new_fig(8.0)
    title(fig, "Where the energy and the entropy come from",
          "Each angular mode l, both polarisations. Filled: certified value. Hatched: proved upper bound only.")
    axes = [fig.add_axes([0.085, 0.16, 0.41, 0.60]), fig.add_axes([0.575, 0.16, 0.41, 0.60])]
    names = ["power (energy per time, × M²)", "entropy per time (× M)"]
    xs = ls + [10.6]
    w = 0.38
    for k, ax in enumerate(axes):
        for j, (s, colr, lab) in enumerate(((1, CAT[0], "photons (spin 1)"), (2, CAT[1], "gravitons (spin 2)"))):
            xv, yv, er, xb, yb = [], [], [], [], []
            for l in ls:
                if (s, l) in data:
                    m, rad = data[(s, l)][k]
                    if m - rad > 0:          # a real two-sided enclosure
                        xv.append(l + (j - 0.5) * w)
                        yv.append(m)
                        er.append(rad)
                    else:                    # the enclosure contains 0: only its upper end is informative
                        xb.append(l + (j - 0.5) * w)
                        yb.append(m + rad)
            xb.append(10.6 + (j - 0.5) * w)
            yb.append(tails[s][k])
            ax.bar(xv, yv, width=w * 0.92, color=colr, label=lab, log=True)
            ax.errorbar(xv, yv, yerr=er, fmt="none", ecolor=TXT, elinewidth=1)
            ax.bar(xb, yb, width=w * 0.92, facecolor="none", edgecolor=colr, hatch="///", lw=1.5, log=True)
        ax.set_yscale("log")
        ax.set_xticks(xs)
        ax.set_xticklabels([str(l) for l in ls] + ["≥10"])
        ax.set_xlabel("angular mode l")
        ax.set_title(names[k], fontsize=16, color=TXT, loc="left")
        ax.set_ylim(1e-20 if k == 0 else 1e-18, 1e-3 if k == 0 else 1e-1)
    axes[1].legend(loc="upper right", fontsize=13)
    p11 = data[(1, 1)][0][0] / float(arb(v["P_1"]).mid())
    p22 = data[(2, 2)][0][0] / float(arb(v["P_2"]).mid())
    axes[0].text(1.3, data[(1, 1)][0][0] * 0.9, "l = 1 photons: %.1f%% of the photon power" % (100 * p11),
                 color=CAT[0], fontsize=13, va="center")
    axes[0].text(2.85, data[(2, 2)][0][0] * 0.5, "l = 2 gravitons: %.1f%%\nof the graviton power" % (100 * p22),
                 color=CAT[1], fontsize=13, va="center")
    save(fig, "ledger-by-mode.svg")


def main():
    r = load("results/hk1b/result_hk1b.json")
    blind = load("results/blind/results.json")
    fig_page(r)
    fig_beta(r, blind)
    fig_modes(r)


if __name__ == "__main__":
    main()
