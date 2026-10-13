"""Push forecast: will the platform keep distributing this post?

Recommendation feeds show a new post to a small test audience and widen distribution when
that audience watches, rewatches and shares. The early numbers a seller copies from the
analytics page are the same signals, so a snapshot can be scored.

The thresholds below are STARTING POINTS. "guide" ones come from third-party creator guides
(no platform publishes its real thresholds); "guess" ones are the director's first estimates;
"benchmark" ones were set from the public numbers of outside hits (`vvl predict --benchmarks`).
knowledge/forecast.md lists the sources. Once a project has enough measured posts, compare
each forecast with what happened (`vvl predict --check`) and adjust the numbers here.
"""

# name: (label, weight, weak below, strong from, basis)
SIGNALS = {
    "hold": ("3 秒留存", 30, 0.55, 0.70, "guide"),
    "watch": ("平均观看 / 时长", 20, 0.40, 0.80, "guess"),
    "completion": ("完播率", 15, 0.30, 0.60, "guide"),
    # Raised 2026-10-13: Calmlings and Pudgy Penguins hits measured on TikTok share at 3.3-3.9%.
    "shares": ("分享 / 播放", 12, 0.005, 0.030, "benchmark"),
    "saves": ("收藏 / 播放", 8, 0.002, 0.010, "guess"),
    # Lowered 2026-10-12: nine Calmlings reels with 0.1M-74M views had likes 1.4-6.8% and
    # comments 0.02-0.13%; the old lines (3% / 0.1%) graded every one of those hits weak.
    "likes": ("点赞 / 播放", 6, 0.015, 0.05, "benchmark"),
    "comments": ("评论 / 播放", 5, 0.0003, 0.001, "benchmark"),
    "follows": ("新关注 / 播放", 4, 0.001, 0.005, "guess"),
}
MIN_VIEWS = 100       # below this, rates are noise
MIN_COVERAGE = 0.4    # share of the total weight that must have data


def values(metric, duration_s):
    """The signal values a snapshot contains. Missing ones are left out, never guessed."""
    views = metric.get("views") or 0
    out = {}
    # YouTube reports "viewed vs swiped away"; it measures the same decision as a 3-second hold.
    hold = metric.get("hold_3s_rate", metric.get("viewed_rate"))
    if hold is not None:
        out["hold"] = hold
    if metric.get("avg_watch_s") is not None and duration_s:
        out["watch"] = metric["avg_watch_s"] / duration_s
    if metric.get("completion_rate") is not None:
        out["completion"] = metric["completion_rate"]
    if views:
        for name, field in (("shares", "shares"), ("saves", "saves"), ("likes", "likes"),
                            ("comments", "comments"), ("follows", "new_followers")):
            if metric.get(field) is not None:
                out[name] = metric[field] / views
    return out


def points(value, weak, strong):
    """0-100: 40 at the weak line, 70 at the strong line, 100 at 1.5x the strong line."""
    if value < weak:
        return 40 * value / weak
    if value < strong:
        return 40 + 30 * (value - weak) / (strong - weak)
    return min(100, 70 + 30 * (value - strong) / (0.5 * strong))


def score(signal_values):
    """Grade a set of signal values (measured or estimated): (score 0-100, coverage, signals)."""
    signals, total, weight_sum = [], 0, 0
    for name, value in signal_values.items():
        label, weight, weak, strong, basis = SIGNALS[name]
        pts = points(value, weak, strong)
        level = "weak" if value < weak else "strong" if value >= strong else "ok"
        signals.append({"name": name, "label": label, "value": round(value, 4), "level": level,
                        "points": round(pts),
                        "weak": weak, "strong": strong, "weight": weight, "basis": basis})
        total += pts * weight
        weight_sum += weight
    coverage = weight_sum / sum(s[1] for s in SIGNALS.values())
    return (round(total / weight_sum) if weight_sum else None), round(coverage, 2), signals


def verdict(points_total):
    return "push" if points_total >= 70 else "hold" if points_total >= 45 else "stall"


def forecast(metric, duration_s):
    """Score one measured snapshot. Returns the record fields of a `forecast`."""
    total, coverage, signals = score(values(metric, duration_s))
    views = metric.get("views") or 0
    enough = views >= MIN_VIEWS and coverage >= MIN_COVERAGE
    worst = sorted((s for s in signals if s["level"] == "weak"), key=lambda s: -s["weight"])
    return {"post_id": metric["post_id"], "platform": metric["platform"],
            "age_hours": metric["age_hours"], "views": views, "score": total if enough else None,
            "verdict": verdict(total) if enough else "unknown", "coverage": coverage,
            "signals": signals, "weakest": worst[0]["name"] if worst else ""}


def estimate(expected):
    """Score an idea before it is made, from the director's estimate of each signal.
    The estimates are a judgement; the arithmetic is the same as for measured posts, so an
    idea's score and the finished post's score can be compared."""
    unknown = sorted(set(expected) - set(SIGNALS))
    if unknown:
        raise ValueError(f"unknown signal(s) {unknown}; use: {', '.join(SIGNALS)}")
    missing = sorted(set(SIGNALS) - set(expected))
    if missing:
        raise ValueError(f"estimate every signal; missing: {', '.join(missing)}")
    total, _, signals = score({name: expected[name] for name in SIGNALS})
    return {"expected": expected, "predicted_score": total, "predicted_verdict": verdict(total),
            "predicted_signals": signals}
