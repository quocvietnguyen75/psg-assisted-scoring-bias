"""Amendment 003 simulation of assisted-reference bias (two-label latent-class model).

Exact large-sample expectations of the study's measures when experts edit an
algorithm's pre-scoring. The steps are:
- calibration to PSG-IPA sleep staging;
- validation against the observed signatures;
- a Monte Carlo check through the study's own estimators;
- a grid of consequences with the truth known.

Labels are coded by correctness: every rater gives either the true label or
the epoch's competing label.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from statistics import NormalDist
from typing import Any, Callable, Mapping, Sequence

from careport.psg_assist_bias import (
    AnalysisError,
    _mean,
    _recordings,
    lights_window,
    pairwise_agreement,
    read_annotations,
    stage_epochs,
    verify_checksums,
)
from careport.psg_assist_mechanisms import _levels, ambiguity_lift, error_following

_NORMAL = NormalDist()
# (weight, difficulty, tails given a correct pre-fill, tails given a wrong pre-fill); a tail pair is
# (P(consensus = true label), P(consensus = competing label)).
Row = tuple[float, "float | None", tuple[float, float], tuple[float, float]]


@dataclass(frozen=True)
class Model:
    """Parameters on the logit scale; the mean human ability is 0."""

    clear: float                  # share of clear epochs
    mean: float                   # location of the other epochs' difficulty before folding
    sd: float                     # its SD before folding
    prefill: float = 0.0          # pre-fill ability offset (delta_A)
    alpha: float = 0.0            # anchoring strength
    spread: float = 0.0           # scorer ability spread (tau)
    consistency: float = 0.0      # chance the assisted judgment repeats the manual label (c)
    idiosyncratic: float = 0.0    # pre-fill error rate independent of difficulty (epsilon)
    independent: float = 0.0      # independent algorithm ability offset (delta_B)
    nodes: int = 400
    alphas: tuple[float, ...] | None = None  # scorer-specific anchoring (S4)


def logistic(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    z = math.exp(x)
    return z / (1.0 + z)


def poisson_binomial(probs: Sequence[float]) -> list[float]:
    """Distribution of the number of successes among independent trials."""
    dist = [1.0]
    for p in probs:
        nxt = [0.0] * (len(dist) + 1)
        for k, d in enumerate(dist):
            nxt[k] += d * (1 - p)
            nxt[k + 1] += d * p
        dist = nxt
    return dist


def _count_dist(probs: Sequence[float]) -> list[float]:
    n = len(probs)
    if n and all(p == probs[0] for p in probs):
        p = probs[0]
        return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
    return poisson_binomial(probs)


def threshold(n: int, rule: str, fraction: float = 0.75) -> int:
    if rule == "majority":
        return n // 2 + 1
    if rule == "supermajority":
        return max(1, math.ceil(fraction * n - 1e-9))
    raise AnalysisError(f"unknown consensus rule: {rule}")


def abilities(n: int, spread: float) -> list[float]:
    return [spread * _NORMAL.inv_cdf((j + 0.5) / n) for j in range(n)]


def difficulty_nodes(model: Model) -> list[tuple[float, float | None]]:
    """(weight, difficulty) pairs; None marks the clear share.

    Difficulty is folded, b = -|x| with x ~ Normal(mean, sd), so the average expert is right at least half
    the time on every epoch (amendment 003, note 1: the true label is the one experts give more often).
    """
    out: list[tuple[float, float | None]] = [(model.clear, None)] if model.clear > 0 else []
    if model.clear < 1:
        w = (1 - model.clear) / model.nodes
        out += [(w, -abs(model.mean + model.sd * _NORMAL.inv_cdf((k + 0.5) / model.nodes)))
                for k in range(model.nodes)]
    return out


def _correct(ability: float, b: float | None) -> float:
    return 1.0 if b is None else logistic(ability - b)


def _prefill(model: Model, b: float | None) -> float:
    return (1 - model.idiosyncratic) * _correct(model.prefill, b)


def _alphas(model: Model, n: int) -> list[float]:
    if model.alphas is None:
        return [model.alpha] * n
    if len(model.alphas) != n:
        raise AnalysisError(f"scorer-specific anchoring is defined for {len(model.alphas)} scorers, not {n}")
    return list(model.alphas)


def _agree_prob(p: float, a: float) -> float:
    return p * a + (1 - p) * (1 - a)


def _assisted(p: Sequence[float], alphas: Sequence[float], prefill_correct: bool) -> list[float]:
    """P(assisted label = true label) per scorer, given whether the pre-fill is correct."""
    if prefill_correct:
        return [x + al * (1 - x) for x, al in zip(p, alphas)]
    return [x * (1 - al) for x, al in zip(p, alphas)]


def _tails(dist: Sequence[float], n: int, m: int) -> tuple[float, float]:
    """(P(consensus = true label), P(consensus = competing label)) from the count of true labels (m > n/2)."""
    return sum(dist[m:]), sum(dist[: n - m + 1])


def _bisect(f: Callable[[float], float], lo: float, hi: float, iterations: int = 100) -> float | None:
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if (flo < 0) == (fhi < 0):
        return None
    for _ in range(iterations):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def nelder_mead(f: Callable[[Sequence[float]], float], x0: Sequence[float], step: float = 0.5,
                max_iterations: int = 400, tolerance: float = 1e-14) -> tuple[list[float], float]:
    """Deterministic Nelder-Mead minimisation (standard coefficients)."""
    dim = len(x0)
    simplex = [list(x0)] + [[x0[i] + (step if i == j else 0.0) for i in range(dim)] for j in range(dim)]
    values = [f(x) for x in simplex]
    for _ in range(max_iterations):
        order = sorted(range(dim + 1), key=lambda i: values[i])
        simplex, values = [simplex[i] for i in order], [values[i] for i in order]
        if values[-1] - values[0] < tolerance:
            break
        centroid = [sum(s[d] for s in simplex[:-1]) / dim for d in range(dim)]
        worst = simplex[-1]
        refl = [c + (c - w) for c, w in zip(centroid, worst)]
        fr = f(refl)
        if fr < values[0]:
            expd = [c + 2 * (c - w) for c, w in zip(centroid, worst)]
            fe = f(expd)
            simplex[-1], values[-1] = (expd, fe) if fe < fr else (refl, fr)
        elif fr < values[-2]:
            simplex[-1], values[-1] = refl, fr
        else:
            if fr < values[-1]:
                contr = [c + 0.5 * (r - c) for c, r in zip(centroid, refl)]
                fc = f(contr)
                accept = fc <= fr
            else:
                contr = [c + 0.5 * (w - c) for c, w in zip(centroid, worst)]
                fc = f(contr)
                accept = fc < values[-1]
            if accept:
                simplex[-1], values[-1] = contr, fc
            else:
                best = simplex[0]
                simplex = [best] + [[b + 0.5 * (x - b) for b, x in zip(best, s)] for s in simplex[1:]]
                values = [values[0]] + [f(s) for s in simplex[1:]]
    i = min(range(dim + 1), key=lambda k: values[k])
    return simplex[i], values[i]


# ---------------------------------------------------------------------------
# References: consensus of manual or assisted scorings, measured and true accuracy
# ---------------------------------------------------------------------------

def _rows(model: Model, n: int, m: int, assisted: bool) -> list[Row]:
    z, al = abilities(n, model.spread), _alphas(model, n)
    rows: list[Row] = []
    for w, b in difficulty_nodes(model):
        p = [_correct(x, b) for x in z]
        if assisted:
            rows.append((w, b, _tails(_count_dist(_assisted(p, al, True)), n, m),
                         _tails(_count_dist(_assisted(p, al, False)), n, m)))
        else:
            t = _tails(_count_dist(p), n, m)
            rows.append((w, b, t, t))
    return rows


def _b_agree(a: float, pb: float, given_t: tuple[float, float], given_c: tuple[float, float]) -> float:
    (tt, ct), (tc, cc) = given_t, given_c
    return a * (pb * tt + (1 - pb) * ct) + (1 - a) * (pb * tc + (1 - pb) * cc)


def _summarise(model: Model, rows: Sequence[Row], bracket: Sequence[float] | None) -> dict[str, Any]:
    inc = ref = ma = mb = ta = tb = 0.0
    for w, b, given_t, given_c in rows:
        a, pb = _prefill(model, b), _correct(model.independent, b)
        it, ic = sum(given_t), sum(given_c)
        inc += w * (a * it + (1 - a) * ic)
        ref += w * (a * given_t[0] + (1 - a) * given_c[0])
        ma += w * (a * given_t[0] + (1 - a) * given_c[1])
        mb += w * _b_agree(a, pb, given_t, given_c)
        ta += w * a * it
        tb += w * pb * (a * it + (1 - a) * ic)
    if inc <= 0:
        raise AnalysisError("no epoch reaches the consensus threshold")
    out: dict[str, Any] = {"included": inc, "reference_accuracy": ref / inc, "measured_a": ma / inc,
                           "measured_b": mb / inc, "true_a": ta / inc, "true_b": tb / inc}
    out["bias_a"] = out["measured_a"] - out["true_a"]
    out["bias_b"] = out["measured_b"] - out["true_b"]
    out["handicap"] = out["bias_a"] - out["bias_b"]
    if bracket is not None:
        out["breakeven"] = _breakeven(model, rows, out["measured_a"], inc, bracket)
    return out


def _breakeven(model: Model, rows: Sequence[Row], target: float, inc: float,
               bracket: Sequence[float]) -> float | None:
    """True-accuracy advantage over the pre-fill that a human-like competitor needs to tie its measured accuracy."""
    def gap(ability: float) -> float:
        return sum(w * _b_agree(_prefill(model, b), _correct(ability, b), gt, gc) for w, b, gt, gc in rows) / inc - target
    root = _bisect(gap, bracket[0], bracket[1])
    if root is None:
        return None
    nodes = difficulty_nodes(model)
    return sum(w * _correct(root, b) for w, b in nodes) - sum(w * _prefill(model, b) for w, b in nodes)


def _delta_human(model: Model, n: int, m: int) -> float:
    """Mean over scorers: manual agreement with the others' assisted consensus minus with their manual consensus."""
    z, al = abilities(n, model.spread), _alphas(model, n)
    homogeneous = len(set(z)) == 1 and len(set(al)) == 1
    values = []
    for j in ([0] if homogeneous else range(n)):
        oz, oal = z[:j] + z[j + 1:], al[:j] + al[j + 1:]
        num_s = den_s = num_m = den_m = 0.0
        for w, b in difficulty_nodes(model):
            p = [_correct(x, b) for x in oz]
            pj, a = _correct(z[j], b), _prefill(model, b)
            mt, mc = _tails(_count_dist(p), n - 1, m)
            num_m += w * (pj * mt + (1 - pj) * mc)
            den_m += w * (mt + mc)
            st, sc = _tails(_count_dist(_assisted(p, oal, True)), n - 1, m)
            ft, fc = _tails(_count_dist(_assisted(p, oal, False)), n - 1, m)
            num_s += w * (a * (pj * st + (1 - pj) * sc) + (1 - a) * (pj * ft + (1 - pj) * fc))
            den_s += w * (a * (st + sc) + (1 - a) * (ft + fc))
        values.append(num_s / den_s - num_m / den_m)
    return _mean(values)


def _comparison(model: Model, n: int, rule: str, fraction: float, manual: Mapping[str, Any],
                assisted: Mapping[str, Any]) -> dict[str, Any]:
    nodes = difficulty_nodes(model)
    z, al = abilities(n, model.spread), _alphas(model, n)
    m1 = _mean([sum(w * al[j] * (1 - _agree_prob(_correct(z[j], b), _prefill(model, b))) for w, b in nodes)
                for j in range(n)])
    return {
        "true_accuracy": {"prefill": sum(w * _prefill(model, b) for w, b in nodes),
                          "independent": sum(w * _correct(model.independent, b) for w, b in nodes)},
        "manual": dict(manual),
        "assisted": dict(assisted),
        "signatures": {
            "M1": m1,
            "delta_auto": assisted["measured_a"] - manual["measured_a"],
            "delta_b": assisted["measured_b"] - manual["measured_b"],
            "delta_human": _delta_human(model, n, threshold(n - 1, rule, fraction)) if n >= 3 else None,
        },
    }


def compare_references(model: Model, n: int, rule: str, fraction: float = 0.75,
                       bracket: Sequence[float] = (-8.0, 12.0)) -> dict[str, Any]:
    """Manual versus assisted n-scorer reference for the pre-fill and a human-like independent algorithm."""
    m = threshold(n, rule, fraction)
    manual = _summarise(model, _rows(model, n, m, False), bracket)
    assisted = _summarise(model, _rows(model, n, m, True), bracket)
    return _comparison(model, n, rule, fraction, manual, assisted)


# ---------------------------------------------------------------------------
# The study's measures: analytic (model) and estimated (sequences)
# ---------------------------------------------------------------------------

def _bin_keys(bins: Sequence[Sequence[int]]) -> list[str]:
    return [f"{lo}-{hi}" for lo, hi in bins]


def _bin_of(level: int, bins: Sequence[Sequence[int]]) -> str | None:
    for lo, hi in bins:
        if lo <= level <= hi:
            return f"{lo}-{hi}"
    return None


def manual_shares(model: Model, n: int, bins: Sequence[Sequence[int]]) -> tuple[dict[str, float], float]:
    """C1 (shares of epochs by manual agreement level) and C2 (mean pairwise manual agreement)."""
    z = abilities(n, model.spread)
    homogeneous = len(set(z)) == 1
    pairs = [(0, 1)] if homogeneous else [(j, k) for j in range(n) for k in range(j + 1, n)]
    c1 = dict.fromkeys(_bin_keys(bins), 0.0)
    c2 = 0.0
    for w, b in difficulty_nodes(model):
        p = [_correct(x, b) for x in z]
        for k, d in enumerate(_count_dist(p)):
            key = _bin_of(max(k, n - k), bins)
            if key:
                c1[key] += w * d
        c2 += w * _mean([p[j] * p[k] + (1 - p[j]) * (1 - p[k]) for j, k in pairs])
    return c1, c2


def _mean_agree(model: Model, n: int) -> float:
    z = abilities(n, model.spread)
    nodes = difficulty_nodes(model)
    return _mean([sum(w * _agree_prob(_correct(x, b), _prefill(model, b)) for w, b in nodes) for x in z])


def _ratio(num: float, den: float) -> float | None:
    return num / den if den > 0 else None


def model_targets(model: Model, n: int, full: int, loo: int, strong: int,
                  bins: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Large-sample values of the calibration (C) and validation (V) targets under the model."""
    z, al, c = abilities(n, model.spread), _alphas(model, n), model.consistency
    homogeneous = len(set(z)) == 1 and len(set(al)) == 1
    scorers = [0] if homogeneous else list(range(n))
    pairs = [(0, 1)] if homogeneous else [(j, k) for j in range(n) for k in range(j + 1, n)]
    keys = _bin_keys(bins)
    c3, c4 = [0.0] * n, [0.0] * n
    r3 = {j: {k: [0.0, 0.0, 0.0] for k in keys} for j in scorers}  # weight, assisted = pre-fill, manual = pre-fill
    r4 = {j: [0.0, 0.0, 0.0] for j in scorers}
    m3 = {r: [0.0, 0.0, 0.0] for r in ("agree", "disagree")}       # weight, manual pair agrees, assisted pair agrees
    r4_share = r4_wrong = 0.0
    for w, b in difficulty_nodes(model):
        p = [_correct(x, b) for x in z]
        a = _prefill(model, b)
        states = ((True, a), (False, 1 - a))
        for k, d in enumerate(_count_dist(p)):
            r4_share += w * d * (a * ((n - k) >= strong) + (1 - a) * (k >= strong))
            r4_wrong += w * d * (1 - a) * (k >= strong)
        for j in range(n):
            agree = _agree_prob(p[j], a)
            c3[j] += w * agree
            c4[j] += w * al[j] * (1 - agree)

        def u(j: int, x: bool, correct: bool) -> float:
            """P(assisted label = true label | own manual label correct = x, pre-fill correct)."""
            fresh = p[j] + al[j] * (1 - p[j]) if correct else p[j] * (1 - al[j])
            repeat = (1.0 if x else al[j]) if correct else ((1 - al[j]) if x else 0.0)
            return c * repeat + (1 - c) * fresh

        for j in scorers:
            others = _count_dist(p[:j] + p[j + 1:])
            for correct, pst in states:
                for x, px in ((True, p[j]), (False, 1 - p[j])):
                    uj = u(j, x, correct)
                    s_eq = uj if correct else 1 - uj
                    m_eq = 1.0 if x == correct else 0.0
                    for k_o, d in enumerate(others):
                        wt = w * pst * px * d
                        if wt == 0:
                            continue
                        k = k_o + x
                        key = _bin_of(max(k, n - k), bins)
                        if key:
                            cell = r3[j][key]
                            cell[0] += wt
                            cell[1] += wt * s_eq
                            cell[2] += wt * m_eq
                        if ((n - k) if correct else k) >= strong:
                            cell = r4[j]
                            cell[0] += wt
                            cell[1] += wt * s_eq
                            cell[2] += wt * m_eq
        for j, k2 in pairs:
            others = _count_dist([p[i] for i in range(n) if i not in (j, k2)])
            for correct, pst in states:
                for xj, pxj in ((True, p[j]), (False, 1 - p[j])):
                    for xk, pxk in ((True, p[k2]), (False, 1 - p[k2])):
                        uj, uk = u(j, xj, correct), u(k2, xk, correct)
                        semi_agree = uj * uk + (1 - uj) * (1 - uk)
                        man_agree = 1.0 if xj == xk else 0.0
                        for k_o, d in enumerate(others):
                            k = k_o + xj + xk
                            if k >= full:
                                consensus_true = True
                            elif n - k >= full:
                                consensus_true = False
                            else:
                                continue
                            wt = w * pst * pxj * pxk * d
                            cell = m3["agree" if consensus_true == correct else "disagree"]
                            cell[0] += wt
                            cell[1] += wt * man_agree
                            cell[2] += wt * semi_agree
    c1, c2 = manual_shares(model, n, bins)
    manual = _summarise(model, _rows(model, n, full, False), None)
    assisted = _summarise(model, _rows(model, n, full, True), None)
    v1 = assisted["measured_a"] - manual["measured_a"]
    v2 = _delta_human(model, n, loo)
    v9 = assisted["measured_b"] - manual["measured_b"]

    def mean_lift(cells: list[list[float]]) -> float | None:
        vals = [(cell[1] - cell[2]) / cell[0] for cell in cells if cell[0] > 0]
        return _mean(vals) if vals else None

    return {
        "C1": c1, "C2": c2, "C3": _mean(c3), "C3_by_scorer": c3, "C4": _mean(c4), "C4_by_scorer": c4,
        "V1": v1, "V2": v2, "V3": v1 - v2,
        "V4": {"agree_manual": _ratio(m3["agree"][1], m3["agree"][0]),
               "agree_semi": _ratio(m3["agree"][2], m3["agree"][0]),
               "disagree_manual": _ratio(m3["disagree"][1], m3["disagree"][0]),
               "disagree_semi": _ratio(m3["disagree"][2], m3["disagree"][0])},
        "V5": {key: mean_lift([r3[j][key] for j in scorers]) for key in keys},
        "V6": mean_lift([r4[j] for j in scorers]),
        "V7": r4_share,
        "V8": manual["measured_a"],
        "V9": v9,
        "V10": v1 - v9,
        "prefill_wrong_given_R4": _ratio(r4_wrong, r4_share),
    }


def _agree(x: Sequence[Any], y: Sequence[Any]) -> float:
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    return sum(a == b for a, b in pairs) / len(pairs) if pairs else float("nan")


def _vote_counts(seqs: Sequence[Sequence[Any]]) -> list[dict[Any, int]]:
    out = []
    for unit in zip(*seqs):
        counts: dict[Any, int] = {}
        for v in unit:
            counts[v] = counts.get(v, 0) + 1
        out.append(counts)
    return out


def _consensus(counts: Sequence[Mapping[Any, int]], m: int, leave_out: Sequence[Any] | None = None) -> list[Any]:
    """Most frequent label per unit if it has at least m votes (after removing one scoring's vote), else None."""
    out = []
    for i, cnt in enumerate(counts):
        drop = leave_out[i] if leave_out is not None else object()
        best, best_c = None, -1
        for label, c in cnt.items():
            c -= label == drop
            if c > best_c:
                best, best_c = label, c
        out.append(best if best_c >= m else None)
    return out


def sequence_targets(auto: Sequence[Any], manual: Sequence[Sequence[Any]], semi: Sequence[Sequence[Any]],
                     full: int, loo: int, strong: int, bins: Sequence[Sequence[int]],
                     independent: Sequence[Any] | None = None) -> dict[str, Any]:
    """The C and V targets estimated from labelled units with the study's estimators, pooled over units."""
    n, total = len(manual), len(auto)
    levels = _levels(manual)
    c3 = [sum(x == y for x, y in zip(m, auto)) / total for m in manual]
    c4 = [sum(x == y for x, y in zip(s, auto)) / total - c3[j] for j, s in enumerate(semi)]
    man_counts, semi_counts = _vote_counts(manual), _vote_counts(semi)
    cons_m, cons_s = _consensus(man_counts, full), _consensus(semi_counts, full)
    v8 = _agree(auto, cons_m)
    v1 = _agree(auto, cons_s) - v8
    v2 = _mean([_agree(manual[j], _consensus(semi_counts, loo, semi[j]))
                - _agree(manual[j], _consensus(man_counts, loo, manual[j])) for j in range(n)])
    keys = [i for i in range(total) if cons_m[i] is not None]
    regions = {"agree": [i for i in keys if auto[i] == cons_m[i]], "disagree": [i for i in keys if auto[i] != cons_m[i]]}
    v4 = {}
    for region, idx in regions.items():
        for cond, seqs in (("manual", manual), ("semi", semi)):
            v4[f"{region}_{cond}"] = pairwise_agreement([[s[i] for i in idx] for s in seqs]) if idx else None
    lifts = ambiguity_lift(auto, manual, semi, bins)
    per_scorer, units = error_following(auto, manual, semi, strong)
    r4 = [v for v in per_scorer if v is not None]
    v9 = _agree(independent, cons_s) - _agree(independent, cons_m) if independent is not None else None
    return {
        "n_units": total,
        "C1": {f"{lo}-{hi}": sum(lo <= lv <= hi for lv in levels) / total for lo, hi in bins},
        "C2": pairwise_agreement(manual), "C3": _mean(c3), "C3_by_scorer": c3, "C4": _mean(c4), "C4_by_scorer": c4,
        "V1": v1, "V2": v2, "V3": v1 - v2, "V4": v4,
        "V5": {key: v["lift"] for key, v in lifts.items()},
        "V6": _mean(r4) if r4 else None, "V7": units / total, "V8": v8,
        "V9": v9, "V10": v1 - v9 if v9 is not None else None,
    }


def simulate(model: Model, n_epochs: int, n_scorers: int, seed: int) -> tuple[list[str], list[list[str]], list[list[str]], list[str]]:
    """Epochs drawn from the model: pre-fill, manual and assisted scorings, independent algorithm ("T" = true label)."""
    rng = random.Random(seed)
    z, al = abilities(n_scorers, model.spread), _alphas(model, n_scorers)
    auto: list[str] = []
    indep: list[str] = []
    manual: list[list[str]] = [[] for _ in range(n_scorers)]
    semi: list[list[str]] = [[] for _ in range(n_scorers)]
    for _ in range(n_epochs):
        b = None if rng.random() < model.clear else -abs(rng.gauss(model.mean, model.sd))
        a = "T" if rng.random() < _prefill(model, b) else "C"
        auto.append(a)
        indep.append("T" if rng.random() < _correct(model.independent, b) else "C")
        for j in range(n_scorers):
            pj = _correct(z[j], b)
            m = "T" if rng.random() < pj else "C"
            judgment = m if rng.random() < model.consistency else ("T" if rng.random() < pj else "C")
            s = judgment if judgment == a or rng.random() >= al[j] else a
            manual[j].append(m)
            semi[j].append(s)
    return auto, manual, semi, indep


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

def _r4_share(model: Model, n: int, strong: int) -> float:
    z = abilities(n, model.spread)
    total = 0.0
    for w, b in difficulty_nodes(model):
        a = _prefill(model, b)
        for k, d in enumerate(_count_dist([_correct(x, b) for x in z])):
            total += w * d * (a * ((n - k) >= strong) + (1 - a) * (k >= strong))
    return total


def calibrate(targets: Mapping[str, Any], n: int, bins: Sequence[Sequence[int]], cfg: Mapping[str, Any],
              spread: float = 0.0, consistency: float = 0.0, fit_idiosyncratic: bool = False,
              scorer_alphas: bool = False) -> tuple[Model, dict[str, Any]]:
    """Fit the difficulty to C1 and C2, the pre-fill ability to C3, and set alpha = C4 / (1 - C3)."""
    cal = cfg["calibration"]
    nodes = int(cfg["difficulty_nodes"])
    fit_keys = _bin_keys(bins)[:-1]

    def unpack(u: Sequence[float]) -> Model:
        return Model(clear=logistic(u[0]), mean=u[1], sd=math.exp(u[2]), spread=spread, nodes=nodes)

    def loss(u: Sequence[float]) -> float:
        c1, c2 = manual_shares(unpack(u), n, bins)
        return sum((c1[k] - targets["C1"][k]) ** 2 for k in fit_keys) + (c2 - targets["C2"]) ** 2

    start = cal["start"]
    x = [math.log(start["clear"] / (1 - start["clear"])), start["mean"], math.log(start["sd"])]
    value = float("inf")
    for _ in range(1 + int(cal["restarts"])):
        x, value = nelder_mead(loss, x, max_iterations=int(cal["max_iterations"]))
    lo, hi = cal["ability_bracket"]

    def fit_prefill(model: Model) -> Model:
        root = _bisect(lambda d: _mean_agree(replace(model, prefill=d), n) - targets["C3"], lo, hi, 80)
        if root is None:
            raise AnalysisError("pre-fill ability is not bracketed by the calibration range")
        return replace(model, prefill=root)

    model = fit_prefill(replace(unpack(x), consistency=consistency))
    info: dict[str, Any] = {"loss": value}
    if fit_idiosyncratic:
        strong, target = int(cfg["strong_consensus"]), targets["V7"]
        e_lo, e_hi = cal["idiosyncratic_bracket"]

        def share(eps: float) -> float:
            return _r4_share(fit_prefill(replace(model, idiosyncratic=eps)), n, strong)

        if share(e_lo) >= target:
            eps, reached = e_lo, True
        else:
            while True:
                try:
                    s_hi = share(e_hi)
                    break
                except AnalysisError:
                    e_hi = (e_lo + e_hi) / 2
                    if e_hi - e_lo < 1e-6:
                        raise
            if s_hi < target:
                eps, reached = e_hi, False
            else:
                eps, reached = _bisect(lambda e: share(e) - target, e_lo, e_hi, 40), True
        model = fit_prefill(replace(model, idiosyncratic=eps))
        info["idiosyncratic_target_reached"] = reached
    c3, c4 = targets["C3"], targets["C4"]
    alpha = c4 / (1 - c3)
    if not 0 <= alpha <= 1:
        raise AnalysisError(f"anchoring strength {alpha:.3f} is outside [0, 1]")
    model = replace(model, alpha=alpha)
    if scorer_alphas:
        model = replace(model, alphas=tuple(min(1.0, max(0.0, c4j / (1 - c3j)))
                                            for c3j, c4j in zip(targets["C3_by_scorer"], targets["C4_by_scorer"])))
    c1, c2 = manual_shares(model, n, bins)
    info.update({"fitted_C1": c1, "fitted_C2": c2, "fitted_C3": _mean_agree(model, n)})
    return model, info


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def empirical_sequences(root: Path, config1: Mapping[str, Any], task: str) -> tuple[list[str], list[list[str]], list[list[str]]]:
    """Pooled stage sequences over epochs where the pre-fill and every scoring are labelled (the R3 set)."""
    spec = config1["tasks"][task]
    if spec["kind"] != "stages":
        raise AnalysisError(f"{task} is not a staging task")
    token, n_sc = spec["file_token"], int(config1["n_scorers"])
    ann = root / task / "Annotations"
    auto_all: list[str] = []
    man_all: list[list[str]] = [[] for _ in range(n_sc)]
    semi_all: list[list[str]] = [[] for _ in range(n_sc)]
    for rec in _recordings(root, task, token):
        auto_rows = read_annotations(ann / "auto" / f"SN{rec}_{token}_auto.txt")
        window = lights_window(auto_rows, config1["window"]["start_label"], config1["window"]["end_label"])
        ex = lambda r: stage_epochs(r, spec["labels"], spec["label_prefix"], window, config1["epoch_seconds"])
        auto = ex(auto_rows)
        man = [ex(read_annotations(ann / "manual" / f"SN{rec}_{token}_manual_scorer{s}.txt")) for s in range(1, n_sc + 1)]
        semi = [ex(read_annotations(ann / "semiauto" / f"SN{rec}_{token}_semiauto_scorer{s}.txt"))
                for s in range(1, n_sc + 1)]
        keys = sorted(k for k, v in auto.items() if v is not None
                      and all(m.get(k) is not None for m in man) and all(x.get(k) is not None for x in semi))
        auto_all += [auto[k] for k in keys]
        for j in range(n_sc):
            man_all[j] += [man[j][k] for k in keys]
            semi_all[j] += [semi[j][k] for k in keys]
    return auto_all, man_all, semi_all


def _flat(t: Mapping[str, Any]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for key in ("C1", "V4", "V5"):
        for k, v in t[key].items():
            out[f"{key}:{k}"] = v
    for key in ("C2", "C3", "C4", "V1", "V2", "V3", "V6", "V7", "V8", "V9", "V10"):
        out[key] = t[key]
    return out


def _sign(x: float | None) -> int | None:
    return None if x is None else (x > 0) - (x < 0)


def _validation(model_t: Mapping[str, Any], emp: Mapping[str, Any], yard: Mapping[str, Any]) -> dict[str, Any]:
    rows = []
    mf, ef = _flat(model_t), _flat(emp)
    for key in ("V1", "V2", "V3", "V4:agree_manual", "V4:agree_semi", "V4:disagree_manual", "V4:disagree_semi",
                *[f"V5:{k}" for k in model_t["V5"]], "V6", "V7", "V8", "V9", "V10"):
        mv, ev = mf[key], ef[key]
        ci = yard["R3_ci95"].get(key[3:]) if key.startswith("V5:") else yard["R4_ci95"] if key == "V6" else None
        rows.append({"target": key, "model": mv, "empirical": ev,
                     "difference": mv - ev if mv is not None and ev is not None else None,
                     "yardstick_ci95": ci,
                     "within_yardstick": (ci[0] <= mv <= ci[1]) if ci and mv is not None else None})
    def change(v4: Mapping[str, float | None], region: str) -> float | None:
        semi, manual = v4.get(f"{region}_semi"), v4.get(f"{region}_manual")
        return None if semi is None or manual is None else semi - manual

    signs = {
        "V1": _sign(model_t["V1"]) == _sign(emp["V1"]),
        "V2": _sign(model_t["V2"]) == _sign(emp["V2"]),
        "V3": _sign(model_t["V3"]) == _sign(emp["V3"]),
        "V4_agree": _sign(change(model_t["V4"], "agree")) == _sign(change(emp["V4"], "agree")),
        "V4_disagree": _sign(change(model_t["V4"], "disagree")) == _sign(change(emp["V4"], "disagree")),
        "V5_pattern": _r3_pattern(model_t["V5"]),
        "V6": _sign(model_t["V6"]) == _sign(emp["V6"]),
        "V9": _sign(model_t["V9"]) == _sign(yard["M5_independent_change_kappa"]),
        "V10": _sign(model_t["V10"]) == _sign(yard["ranking_gap_growth_kappa"]),
    }
    return {"targets": rows, "signs_match": signs, "empirical_V5_pattern": _r3_pattern(emp["V5"]),
            "all_signs_match": all(signs.values())}


def _r3_pattern(lifts: Mapping[str, float | None]) -> bool:
    vals = list(lifts.values())
    if any(v is None for v in vals):
        return False
    return abs(vals[0]) < 0.01 and all(b > a for a, b in zip(vals, vals[1:]))


def _model_dict(model: Model) -> dict[str, Any]:
    d = asdict(model)
    d["alphas"] = list(model.alphas) if model.alphas is not None else None
    return d


def _points(model: Model, scorers: Sequence[int], rules: Sequence[str], fraction: float,
            bracket: Sequence[float]) -> list[dict[str, Any]]:
    return [{"n": n, "rule": rule, **compare_references(model, n, rule, fraction, bracket)}
            for n in scorers for rule in rules]


CSV_FIELDS = ["alpha", "prefill_offset", "scorers", "rule", "true_acc_prefill", "true_acc_independent"] + [
    f"{ref}_{k}" for ref in ("manual", "assisted") for k in
    ("included", "reference_accuracy", "measured_a", "measured_b", "true_a", "true_b", "bias_a", "handicap",
     "breakeven")] + ["M1", "delta_auto", "delta_b", "delta_human"]


def run_grid(base: Model, alphas: Sequence[float], offsets: Sequence[float], scorers: Sequence[int],
             rules: Sequence[str], fraction: float, bracket: Sequence[float]) -> list[dict[str, Any]]:
    out = []
    for n in scorers:
        for rule in rules:
            m = threshold(n, rule, fraction)
            manual_rows = _rows(base, n, m, False)
            for alpha in alphas:
                assisted_rows = _rows(replace(base, alpha=alpha), n, m, True)
                for offset in offsets:
                    model = replace(base, alpha=alpha, prefill=offset)
                    res = _comparison(model, n, rule, fraction, _summarise(model, manual_rows, bracket),
                                      _summarise(model, assisted_rows, bracket))
                    row: dict[str, Any] = {"alpha": alpha, "prefill_offset": offset, "scorers": n, "rule": rule,
                                           "true_acc_prefill": res["true_accuracy"]["prefill"],
                                           "true_acc_independent": res["true_accuracy"]["independent"]}
                    for ref in ("manual", "assisted"):
                        for k in ("included", "reference_accuracy", "measured_a", "measured_b", "true_a", "true_b",
                                  "bias_a", "handicap", "breakeven"):
                            row[f"{ref}_{k}"] = res[ref][k]
                    row.update(res["signatures"])
                    out.append(row)
    return out


def _predictions(n: int, points: Sequence[Mapping[str, Any]], grid_rows: Sequence[Mapping[str, Any]],
                 ident: Sequence[Mapping[str, Any]], validation: Mapping[str, Any]) -> dict[str, Any]:
    at = {(p["n"], p["rule"]): p for p in points}
    ref = at[(n, "majority")]
    ns = sorted({p["n"] for p in points})
    small, large = at[(ns[0], "majority")], at[(ns[-1], "majority")]
    majority = [r for r in grid_rows if r["rule"] == "majority" and r["alpha"] > 0]
    violations = [r for r in majority if not r["assisted_handicap"] > r["manual_handicap"]]
    lowest, highest = ident[0], ident[-1]
    signatures_hold = all(r["M1"] > 0 and r["delta_auto"] > 0 and r["delta_human"] < 0 and r["delta_b"] < 0
                          for r in ident)
    return {
        "P1": {"supported": validation["all_signs_match"], "signs_match": validation["signs_match"]},
        "P2": {"supported": ref["assisted"]["bias_a"] > 0 and ref["assisted"]["bias_a"] > ref["manual"]["bias_a"],
               "assisted_bias": ref["assisted"]["bias_a"], "manual_bias": ref["manual"]["bias_a"]},
        "P3": {"supported": large["assisted"]["bias_a"] > small["assisted"]["bias_a"] and large["assisted"]["bias_a"] > 0,
               "assisted_bias_by_n": {p["n"]: p["assisted"]["bias_a"] for p in points if p["rule"] == "majority"},
               "manual_bias_by_n": {p["n"]: p["manual"]["bias_a"] for p in points if p["rule"] == "majority"}},
        "P4": {"supported": not violations and ref["assisted"]["handicap"] > 0,
               "cells_checked": len(majority), "violations": len(violations),
               "assisted_handicap": ref["assisted"]["handicap"], "manual_handicap": ref["manual"]["handicap"]},
        "P5": {"supported": signatures_hold and lowest["accuracy_gain"] < 0 < highest["accuracy_gain"],
               "signatures_hold": signatures_hold,
               "accuracy_gain_at_lowest_offset": lowest["accuracy_gain"],
               "accuracy_gain_at_highest_offset": highest["accuracy_gain"]},
    }


def run_simulation(config3_path: Path, config1_path: Path, data_root: Path, output_dir: Path,
                   verify: bool = True) -> dict[str, Any]:
    c3 = json.loads(Path(config3_path).read_text(encoding="utf-8"))
    c1 = json.loads(Path(config1_path).read_text(encoding="utf-8"))
    root, out_dir = Path(data_root), Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if verify:
        verify_checksums(root, c1["dataset"]["checksum_file"], c1["dataset"]["expected_files"])
    n = int(c1["n_scorers"])
    full, loo = int(c3["consensus"]["full"]), int(c3["consensus"]["leave_one_out"])
    strong, bins = int(c3["strong_consensus"]), c3["level_bins"]
    fraction, bracket, grid = float(c3["supermajority_fraction"]), c3["breakeven_bracket"], c3["grid"]

    # Empirical targets and calibration.
    empirical = sequence_targets(*empirical_sequences(root, c1, c3["task"]), full, loo, strong, bins)
    base, base_info = calibrate(empirical, n, bins, c3)
    base_targets = model_targets(base, n, full, loo, strong, bins)

    # Monte Carlo check through the study's estimators; the run stops if it fails.
    mc = c3["monte_carlo_check"]
    s_auto, s_manual, s_semi, s_indep = simulate(base, int(mc["epochs"]), n, int(mc["seed"]))
    simulated = _flat(sequence_targets(s_auto, s_manual, s_semi, full, loo, strong, bins, independent=s_indep))
    diffs = {k: abs(v - simulated[k]) for k, v in _flat(base_targets).items()
             if v is not None and simulated[k] is not None}
    worst = max(diffs, key=diffs.get)
    mc_out = {"epochs": mc["epochs"], "seed": mc["seed"], "tolerance": mc["tolerance"],
              "max_abs_difference": diffs[worst], "worst_target": worst,
              "passed": diffs[worst] <= float(mc["tolerance"]), "differences": diffs}
    if not mc_out["passed"]:
        (out_dir / "monte_carlo_failure.json").write_text(json.dumps(mc_out, indent=1) + "\n", encoding="utf-8")
        raise AnalysisError(f"Monte Carlo check failed: {worst} differs by {diffs[worst]:.4f}")

    validation = _validation(base_targets, empirical, c3["yardsticks"])
    scorers = sorted(set(grid["scorers"]) | {n})
    points = _points(base, scorers, grid["rules"], fraction, bracket)

    # Identifiability: signatures and reference accuracy across pre-fill abilities (calibrated alpha, n scorers).
    ident = []
    for offset in sorted(grid["prefill_offset"]):
        res = compare_references(replace(base, prefill=offset), n, "majority", fraction, bracket)
        ident.append({"prefill_offset": offset, "true_acc_prefill": res["true_accuracy"]["prefill"],
                      "manual_reference_accuracy": res["manual"]["reference_accuracy"],
                      "assisted_reference_accuracy": res["assisted"]["reference_accuracy"],
                      "accuracy_gain": res["assisted"]["reference_accuracy"] - res["manual"]["reference_accuracy"],
                      **res["signatures"],
                      "assisted_bias_a": res["assisted"]["bias_a"], "manual_bias_a": res["manual"]["bias_a"],
                      "assisted_handicap": res["assisted"]["handicap"], "manual_handicap": res["manual"]["handicap"]})

    # Consequence grid, including the calibrated values.
    alphas = list(grid["alpha"]) + [base.alpha]
    offsets = list(grid["prefill_offset"]) + [base.prefill]
    grid_rows = run_grid(base, alphas, offsets, grid["scorers"], grid["rules"], fraction, bracket)
    with open(out_dir / "grid.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in grid_rows:
            writer.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in row.items()})

    # Sensitivity analyses.
    sensitivity = {}
    for name, spec in c3["sensitivity"].items():
        model, info = calibrate(empirical, n, bins, c3, spread=float(spec.get("spread", 0.0)),
                                consistency=float(spec.get("consistency", 0.0)),
                                fit_idiosyncratic=bool(spec.get("fit_idiosyncratic", False)),
                                scorer_alphas=bool(spec.get("scorer_alphas", False)))
        sensitivity[name] = {
            "model": _model_dict(model), "calibration": info,
            "validation": _validation(model_targets(model, n, full, loo, strong, bins), empirical, c3["yardsticks"]),
            "calibrated_point": _points(model, [n] if model.alphas is not None else scorers, grid["rules"],
                                        fraction, bracket),
        }

    report = {
        "protocol": c3["protocol"], "amendment": c3["amendment"], "frozen_at": c3["frozen_at"],
        "empirical_targets": empirical,
        "calibration": {"model": _model_dict(base), **base_info},
        "model_targets": base_targets,
        "validation": validation,
        "monte_carlo_check": mc_out,
        "calibrated_point": points,
        "identifiability": ident,
        "sensitivity": sensitivity,
        "predictions": _predictions(n, points, grid_rows, ident, validation),
        "grid_csv": "grid.csv",
    }
    path = out_dir / "simulation.json"
    path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True, help="amendment 003 config")
    parser.add_argument("--base-config", type=Path, required=True, help="protocol 001 config")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    env = json.loads(args.base_config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    report = run_simulation(args.config, args.base_config, Path(root), args.output_dir)
    print(json.dumps({k: report[k] for k in ("calibration", "monte_carlo_check", "predictions")}, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
