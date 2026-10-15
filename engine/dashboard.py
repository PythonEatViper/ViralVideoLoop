"""Build projects/<project>/dashboard.html: one self-contained page, data embedded."""
import json
from datetime import datetime, timedelta
from pathlib import Path

import vvl

TEMPLATE = Path(__file__).with_name("dashboard_template.html")
RECENT_DAYS = 14


def staff_card(pdir, cfg, member):
    """Status plus, for model-run staff, the live instructions and the files they come from."""
    if member["runner"] not in ("grok", "claude"):
        return member
    files = [{"path": str(f.relative_to(vvl.REPO)), "exists": f.exists(),
              "modified": datetime.fromtimestamp(f.stat().st_mtime).astimezone().isoformat() if f.exists() else None}
             for f in vvl.prompt_sources(pdir, member)]
    own = pdir / "team" / f"{member['id']}.md"
    everyone = pdir / "team" / "everyone.md"
    return {**member, "prompt": vvl.render_prompt(pdir, cfg, member),
            "bootstrap": vvl.bootstrap_text(pdir, cfg, member), "files": files,
            "notes": own.read_text() if own.exists() else "",
            "notes_everyone": everyone.read_text() if everyone.exists() else ""}


def build(pdir, cfg):
    vvl.write_prompt_files(pdir, cfg)
    vvl.write_forecasts(pdir)
    cutoff = (vvl.now() - timedelta(days=RECENT_DAYS)).isoformat()
    recent = lambda rtype: [r for r in vvl.load(pdir, rtype) if r["at"] >= cutoff]
    plans = sorted((pdir / "plans").glob("*.md"))[-RECENT_DAYS:]
    rejected = len(list((pdir / "inbox").glob("_rejected/*/*.error.txt")))
    data = {
        "generated_at": vvl.now().isoformat(),
        "repo": str(vvl.REPO),
        "project_id": pdir.name,
        "version": str(vvl.data_version(pdir)),
        "project": {k: cfg[k] for k in ("name", "brief", "cadence", "budget", "rules", "gates")},
        "staff": [staff_card(pdir, cfg, m) for m in vvl.staff_status(pdir, cfg)],
        "posts": vvl.load(pdir, "post"),
        "publishes": vvl.load(pdir, "publish"),
        "metrics": vvl.load(pdir, "metric"),
        "comments": vvl.load(pdir, "comment"),
        "forecasts": vvl.load(pdir, "forecast"),
        "accounts": vvl.load(pdir, "account"),
        "ideas": vvl.load(pdir, "idea"),
        "learnings": vvl.load(pdir, "learning"),
        "reviews": vvl.load(pdir, "review"),
        "todos": vvl.load(pdir, "todo"),
        "signals": recent("signal"),
        # Reference cards stay on the page however old they are: the boss decides from them.
        "refs": [s for s in vvl.load(pdir, "signal") if any(m.endswith("sheet.jpg") for m in s.get("media", []))],
        "notes": recent("note"),
        "incidents": recent("incident"),
        "engagements": recent("engagement"),
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
