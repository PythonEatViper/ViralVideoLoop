"""Build projects/<project>/dashboard.html: one self-contained page, data embedded."""
import json
from datetime import timedelta
from pathlib import Path

import vvl

TEMPLATE = Path(__file__).with_name("dashboard_template.html")
RECENT_DAYS = 14


def build(pdir, cfg):
    cutoff = (vvl.now() - timedelta(days=RECENT_DAYS)).isoformat()
    recent = lambda rtype: [r for r in vvl.load(pdir, rtype) if r["at"] >= cutoff]
    plans = sorted((pdir / "plans").glob("*.md"))[-RECENT_DAYS:]
    rejected = len(list((pdir / "inbox").glob("_rejected/*/*.error.txt")))
    data = {
        "generated_at": vvl.now().isoformat(),
        "repo": str(vvl.REPO),
        "project_id": pdir.name,
        "project": {k: cfg[k] for k in ("name", "brief", "cadence", "budget", "rules", "gates")},
        "staff": vvl.staff_status(pdir, cfg),
        "posts": vvl.load(pdir, "post"),
        "publishes": vvl.load(pdir, "publish"),
        "metrics": vvl.load(pdir, "metric"),
        "comments": vvl.load(pdir, "comment"),
        "accounts": vvl.load(pdir, "account"),
        "ideas": vvl.load(pdir, "idea"),
        "learnings": vvl.load(pdir, "learning"),
        "reviews": vvl.load(pdir, "review"),
        "todos": vvl.load(pdir, "todo"),
        "signals": recent("signal"),
        "notes": recent("note"),
        "incidents": recent("incident"),
        "cost": vvl.cost_summary(pdir, cfg),
        "costs": vvl.load(pdir, "cost"),
        "ready": vvl.outbox_ready(pdir),
        "due": vvl.due_snapshots(pdir, cfg),
        "rejected_files": rejected,
        "plans": [{"name": p.stem, "text": p.read_text()} for p in plans],
    }
    # "</" would end the script tag early if scraped text contained it.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = pdir / "dashboard.html"
    out.write_text(TEMPLATE.read_text().replace("/*DATA*/null", payload))
    return out
