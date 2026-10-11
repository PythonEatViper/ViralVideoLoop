"""vvl — the command line of ViralVideoLoop. No model calls; safe for any agent or human to run.

Run `./vvl help` for the command list. All data lives in projects/<project>/db/*.jsonl,
one JSON record per line; the last line with a given id is the current version.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

from schema import TYPES

REPO = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
KINDS = {"str": str, "int": int, "num": (int, float), "bool": bool, "list": list, "dict": dict,
         "time": str}


# ---------- project and storage ----------

def project_dir(name=None):
    name = name or os.environ.get("VVL_PROJECT") or tomllib.loads(
        (REPO / "vvl.toml").read_text())["active_project"]
    path = REPO / "projects" / name
    if not (path / "project.toml").exists():
        sys.exit(f"no such project: {name} (expected {path}/project.toml)")
    return path


def config(pdir):
    return tomllib.loads((pdir / "project.toml").read_text())


def now():
    return datetime.now().astimezone().replace(microsecond=0)


def parse_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def history(pdir, rtype):
    path = pdir / "db" / f"{rtype}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load(pdir, rtype):
    """Current records of a type, oldest first: the last line per id wins."""
    latest = {}
    for rec in history(pdir, rtype):
        latest[rec["id"]] = rec
    return list(latest.values())


def validate(rtype, rec):
    """Return a list of problems; empty means the record is valid."""
    spec = TYPES[rtype]
    fields = {**spec["required"], **spec["optional"]}
    problems = [f"missing required field '{f}'" for f in spec["required"] if rec.get(f) in (None, "")]
    for name, value in rec.items():
        if name in ("type", "id", "at", "by", "first_at", "seen"):
            continue
        if name not in fields:
            problems.append(f"unknown field '{name}' (allowed: {', '.join(fields)})")
            continue
        kind = fields[name][0]
        if not isinstance(value, KINDS[kind]) or (kind != "bool" and isinstance(value, bool)):
            problems.append(f"field '{name}' must be {kind}, got {type(value).__name__}")
        elif kind == "time":
            try:
                if parse_time(value).tzinfo is None:
                    problems.append(f"field '{name}' needs a UTC offset, e.g. 2026-10-11T08:30:00+08:00")
            except ValueError:
                problems.append(f"field '{name}' is not an ISO 8601 time: {value}")
        allowed = spec["enums"].get(name)
        if allowed and value not in allowed:
            problems.append(f"field '{name}' must be one of {allowed}, got '{value}'")
    return problems


def add_record(pdir, rtype, fields, by):
    """Validate, merge with the earlier version of the same record if any, and append."""
    if rtype not in TYPES:
        raise ValueError(f"unknown type '{rtype}' (known: {', '.join(TYPES)})")
    rec = {k: v for k, v in fields.items() if k != "type"}
    rec["by"] = rec.get("by") or by
    if not rec["by"]:
        raise ValueError("who is adding this? pass --by <staff id>")
    key = TYPES[rtype]["key"]
    if "id" not in rec:
        if key:
            if any(rec.get(k) in (None, "") for k in key):
                raise ValueError(f"missing key field(s) {key}")
            # 24 and 24.0 must give the same id.
            parts = [str(float(rec[k])) if type(rec[k]) in (int, float) else str(rec[k]) for k in key]
            digest = hashlib.sha1("|".join(parts).encode()).hexdigest()[:10]
            rec["id"] = f"{rtype}_{digest}"
        else:
            stamp = now().strftime("%m%d%H%M%S")
            rec["id"] = f"{rtype}_{stamp}_{hashlib.sha1(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:4]}"
    old = next((r for r in load(pdir, rtype) if r["id"] == rec["id"]), None)
    merged = {**(old or {}), **rec}
    problems = validate(rtype, merged)
    if problems:
        raise ValueError("; ".join(problems))
    merged["type"] = rtype
    merged["at"] = now().isoformat()
    merged["first_at"] = old.get("first_at", old["at"]) if old else merged["at"]
    merged["seen"] = (old.get("seen", 1) + 1) if old else 1
    (pdir / "db").mkdir(exist_ok=True)
    with open(pdir / "db" / f"{rtype}.jsonl", "a") as f:
        f.write(json.dumps(merged, ensure_ascii=False) + "\n")
    if rtype == "incident" and merged.get("new_status"):
        add_record(pdir, "heartbeat", {"status": merged["new_status"],
                                       "note": f"{merged['kind']}: {merged['detail']}"[:200]}, merged["by"])
    return merged, old is not None


# ---------- derived views (shared with the dashboard) ----------

def staff_status(pdir, cfg):
    beats = {b["by"]: b for b in load(pdir, "heartbeat")}
    last_write = {}
    for rtype in TYPES:
        for rec in load(pdir, rtype):
            if rec["at"] > last_write.get(rec["by"], ""):
                last_write[rec["by"]] = rec["at"]
    out = []
    for member in cfg["staff"]:
        beat = beats.get(member["id"])
        last = max(filter(None, [beat and beat["at"], last_write.get(member["id"])]), default=None)
        if member["runner"] in ("human", "script"):
            state = "n/a"
        elif member.get("enabled") is False:
            state = "off"
        elif not last:
            state = "not_started"
        elif beat and beat["status"] != "ok":
            state = beat["status"]
        elif now() - parse_time(last) > timedelta(hours=member.get("max_silence_hours", 26)):
            state = "silent"
        else:
            state = "ok"
        out.append({**member, "state": state, "last_seen": last, "last_note": beat and beat.get("note")})
    return out


def cost_summary(pdir, cfg):
    budget = cfg.get("budget", {})
    costs = load(pdir, "cost")
    week_ago = now() - timedelta(days=7)
    spent = lambda rows: round(sum(c["credits"] for c in rows), 1)
    this_week = [c for c in costs if parse_time(c.get("spent_at") or c["at"]) > week_ago]
    by_ref, by_item = {}, {}
    for c in costs:
        by_ref[c.get("ref", "other")] = round(by_ref.get(c.get("ref", "other"), 0) + c["credits"], 1)
        by_item[c["item"]] = round(by_item.get(c["item"], 0) + c["credits"], 1)
    balance = next((b for b in load(pdir, "balance") if b["provider"] == budget.get("provider")), None)
    return {"budget": budget, "balance": balance, "spent_total": spent(costs),
            "spent_week": spent(this_week), "by_ref": by_ref, "by_item": by_item}


def due_snapshots(pdir, cfg, platform=None):
    """Metric snapshots that should have been taken by now and have not been."""
    ages = cfg["cadence"]["metric_snapshots_hours"]
    done = {(m["post_id"], m["platform"], float(m["age_hours"])) for m in load(pdir, "metric")}
    out = []
    for pub in load(pdir, "publish"):
        if platform and pub["platform"] != platform:
            continue
        age_now = (now() - parse_time(pub["published_at"])).total_seconds() / 3600
        reached = [a for a in ages if age_now >= a]
        # Only the newest reached snapshot matters; older missed ones cannot be recovered.
        if reached and (pub["post_id"], pub["platform"], float(reached[-1])) not in done:
            out.append({"post_id": pub["post_id"], "platform": pub["platform"], "url": pub["url"],
                        "age_hours": reached[-1], "actual_age_hours": round(age_now, 1)})
    return out


def outbox_ready(pdir, platform=None):
    """Posts approved for publishing that are not yet live on the given platform."""
    live = {(p["post_id"], p["platform"]) for p in load(pdir, "publish")}
    out = []
    for post_file in sorted((pdir / "outbox").glob("*/post.json")):
        post = json.loads(post_file.read_text())
        if post.get("status") != "ready":
            continue
        for target in post["platforms"]:
            if (not platform or target == platform) and (post["id"], target) not in live:
                out.append({"post_id": post["id"], "platform": target, "folder": str(post_file.parent),
                            "publish_window": post.get("publish_window")})
    return out


def state_text(pdir, cfg):
    reviews = [r for r in load(pdir, "review") if r["status"] == "pending"]
    todos = [t for t in load(pdir, "todo") if t["status"] == "open"]
    posts = load(pdir, "post")
    plans = sorted((pdir / "plans").glob("*.md"))
    cost = cost_summary(pdir, cfg)
    lines = [f"# STATE — {cfg['name']}", "",
             f"Generated {now().isoformat()} by `./vvl build`. Do not edit; read START_HERE.md first.", "",
             f"- Latest plan: {plans[-1].relative_to(REPO) if plans else 'none yet'}",
             f"- Waiting for the boss: {len(reviews)} review(s), {len(todos)} todo(s)",
             f"- Credits: {cost['balance']['credits'] if cost['balance'] else '?'} left; "
             f"{cost['spent_week']} spent in the last 7 days (cap {cost['budget'].get('weekly_credit_cap', '?')})",
             "", "## Posts"]
    lines += [f"- [{p['status']}] {p['id']} — {p['title']}" for p in posts] or ["- none"]
    lines += ["", "## Pending reviews"]
    lines += [f"- {r['id']} ({r['gate']}): {r['title']}" for r in reviews] or ["- none"]
    lines += ["", "## Open todos"]
    lines += [f"- {t['id']} [{t.get('owner', 'boss')}]: {t['text']}" for t in todos] or ["- none"]
    lines += ["", "## Ready to publish"]
    lines += [f"- {o['post_id']} → {o['platform']}" for o in outbox_ready(pdir)] or ["- none"]
    lines += ["", "## Metric snapshots due"]
    lines += [f"- {d['post_id']} on {d['platform']}: {d['age_hours']}h snapshot" for d in due_snapshots(pdir, cfg)] or ["- none"]
    lines += ["", "## Staff"]
    lines += [f"- {s['id']} ({s['runner']}): {s['state']}" + (f", last seen {s['last_seen']}" if s["last_seen"] else "")
              for s in staff_status(pdir, cfg)]
    return "\n".join(lines) + "\n"


# ---------- commands ----------

def parse_fields(args):
    if args.json:
        return json.loads(args.json)
    if args.file:
        return json.loads(Path(args.file).read_text())
    fields = {}
    for pair in args.fields:
        if "=" not in pair:
            sys.exit(f"expected key=value, got '{pair}'")
        key, value = pair.split("=", 1)
        try:
            fields[key] = json.loads(value)
        except json.JSONDecodeError:
            fields[key] = value
    return fields


def cmd_add(args, pdir, cfg):
    data = parse_fields(args)
    failed = False
    for item in data if isinstance(data, list) else [data]:
        try:
            rec, updated = add_record(pdir, args.type, item, args.by)
            print(f"{'updated' if updated else 'added'} {rec['id']}")
        except ValueError as e:
            failed = True
            print(f"REJECTED: {e}", file=sys.stderr)
    if failed:
        sys.exit(1)


def cmd_ingest(args, pdir, cfg):
    """Take every JSON file dropped in inbox/<staff id>/ into the database."""
    inbox, counts = pdir / "inbox", {"added": 0, "updated": 0, "rejected": 0}
    day = now().strftime("%Y-%m-%d")
    for path in sorted(inbox.glob("*/*.json")):
        if path.parent.name.startswith("_"):
            continue
        errors = []
        try:
            data = json.loads(path.read_text())
            for item in data if isinstance(data, list) else [data]:
                try:
                    _, updated = add_record(pdir, item.get("type", ""), item, path.parent.name)
                    counts["updated" if updated else "added"] += 1
                except ValueError as e:
                    errors.append(f"{e} — in {json.dumps(item, ensure_ascii=False)[:160]}")
        except (json.JSONDecodeError, AttributeError) as e:
            errors.append(f"not valid JSON: {e}")
        dest = inbox / ("_rejected" if errors else "_done") / day
        dest.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), dest / f"{path.parent.name}__{path.name}")
        if errors:
            counts["rejected"] += len(errors)
            (dest / f"{path.parent.name}__{path.name}.error.txt").write_text("\n".join(errors) + "\n")
            print(f"REJECTED {path.name}: {errors[0]}", file=sys.stderr)
    print(json.dumps(counts))


def cmd_list(args, pdir, cfg):
    rows = load(pdir, args.type)
    for cond in args.where or []:
        key, value = cond.split("=", 1)
        rows = [r for r in rows if str(r.get(key)) == value]
    if args.days:
        cutoff = (now() - timedelta(days=args.days)).isoformat()
        rows = [r for r in rows if r["at"] >= cutoff]
    if args.sort:
        have = [r for r in rows if r.get(args.sort) is not None]
        have.sort(key=lambda r: r[args.sort], reverse=not args.asc)
        rows = have + [r for r in rows if r.get(args.sort) is None]
    else:
        rows.reverse()
    rows = rows[:args.limit]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    first = next(iter(TYPES[args.type]["required"]))
    for r in rows:
        extra = f"  {args.sort}={r.get(args.sort)}" if args.sort else ""
        label = r.get("title") or r.get("text") or r.get("statement") or r.get("detail") or r.get(first)
        print(f"{r['id']}  {r['at'][:16]}  {r['by']}{extra}  {str(label)[:90]}")
    print(f"({len(rows)} shown)")


def cmd_get(args, pdir, cfg):
    rec = next((r for r in load(pdir, args.type) if r["id"] == args.id), None)
    if not rec:
        sys.exit(f"no {args.type} with id {args.id}")
    print(json.dumps(rec, ensure_ascii=False, indent=1))


def cmd_schema(args, pdir, cfg):
    names = [args.type] if args.type else list(TYPES)
    print("\n\n".join(schema_text(n) for n in names))


def schema_text(name):
    spec = TYPES[name]
    lines = [f"### {name} — {spec['desc']}"]
    if spec["key"]:
        lines.append(f"Same {' + '.join(spec['key'])} = same record (re-adding updates it).")
    for group in ("required", "optional"):
        for field, (kind, desc) in spec[group].items():
            allowed = spec["enums"].get(field)
            choices = f" one of: {' | '.join(allowed)}." if allowed else ""
            lines.append(f"- `{field}` ({kind}, {group}){':' if desc or choices else ''} {desc}{choices}".rstrip())
    return "\n".join(lines)


def cmd_prompt(args, pdir, cfg):
    member = next((s for s in cfg["staff"] if s["id"] == args.staff), None)
    if not member:
        sys.exit(f"no staff '{args.staff}' (known: {', '.join(s['id'] for s in cfg['staff'])})")
    roles = REPO / "engine" / "roles"
    text = (roles / "_common.md").read_text() + "\n" + (roles / f"{member['role']}.md").read_text()
    brief = "\n".join(f"- {k}: {v if isinstance(v, str) else '; '.join(v)}"
                      for k, v in cfg["brief"].items() if k != "docs")
    rules = "\n".join(f"- {k}: {v}" for k, v in cfg["rules"].items())
    values = {**{k: str(v) for k, v in member.items()}, "project": cfg["name"], "repo": str(REPO),
              "project_dir": str(pdir), "brief": brief, "rules": rules,
              "snapshots": ", ".join(f"{h}h" for h in cfg["cadence"]["metric_snapshots_hours"]),
              "publish_window": cfg["cadence"]["publish_window"],
              "posts_every_days": str(cfg["cadence"]["posts_every_days"]),
              "weekly_cap": str(cfg["budget"]["weekly_credit_cap"])}
    for name in TYPES:
        text = text.replace("{{schema:%s}}" % name, schema_text(name))
    for key, value in values.items():
        text = text.replace("{{%s}}" % key, value)
    for optional in ("platform", "watch"):
        text = text.replace("{{%s}}" % optional, "(not set)")
    print(text)


def cmd_staff(args, pdir, cfg):
    for s in staff_status(pdir, cfg):
        print(f"{s['id']:<16} {s['runner']:<7} {s['state']:<12} {s.get('schedule', '')}")


def cmd_checkin(args, pdir, cfg):
    add_record(pdir, "heartbeat", {"status": args.status, **({"note": args.note} if args.note else {})}, args.staff)
    print(f"{args.staff}: {args.status}")


def cmd_due(args, pdir, cfg):
    rows = due_snapshots(pdir, cfg, args.platform)
    print(json.dumps(rows, ensure_ascii=False, indent=1) if rows else "nothing due")


def cmd_outbox(args, pdir, cfg):
    rows = outbox_ready(pdir, args.platform)
    print(json.dumps(rows, ensure_ascii=False, indent=1) if rows else "nothing ready")


def cmd_todo(args, pdir, cfg):
    if args.action == "done":
        add_record(pdir, "todo", {"id": args.id, "status": "done"}, args.by or "boss")
        print(f"done: {args.id}")
        return
    for t in load(pdir, "todo"):
        if t["status"] == "open":
            print(f"{t['id']}  [{t.get('owner', 'boss')}]  {t['text']}" + (f"\n    $ {t['cmd']}" if t.get("cmd") else ""))


def cmd_review(args, pdir, cfg):
    if args.action in ("approve", "changes"):
        status = "approved" if args.action == "approve" else "changes_requested"
        fields = {"id": args.id, "status": status}
        if args.note:
            fields["decision_note"] = args.note
        add_record(pdir, "review", fields, args.by or "boss")
        print(f"{args.id}: {status}")
        return
    for r in load(pdir, "review"):
        if r["status"] == "pending":
            print(f"{r['id']}  ({r['gate']})  {r['title']}\n    {r.get('summary', '')}\n    file: {r.get('path', '-')}")


def cmd_cost(args, pdir, cfg):
    print(json.dumps(cost_summary(pdir, cfg), ensure_ascii=False, indent=1))


def cmd_status(args, pdir, cfg):
    print(state_text(pdir, cfg))


def cmd_build(args, pdir, cfg):
    import dashboard
    out = dashboard.build(pdir, cfg)
    (REPO / "STATE.md").write_text(state_text(pdir, cfg))
    if args.cmd == "build":
        print(out)
    return out


def cmd_start(args, pdir, cfg):
    subprocess.run(["open", str(cmd_build(args, pdir, cfg))], check=True)


def cmd_shot(args, pdir, cfg):
    """Screenshot the dashboard (or one page of it) to a PNG with headless Chrome."""
    page = cmd_build(args, pdir, cfg)
    out = Path(args.out).resolve() if args.out else pdir / "dashboard.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={args.width},{args.height}", f"--screenshot={out}",
                    "--virtual-time-budget=2000", f"file://{page}#/{args.page}"],
                   check=True, capture_output=True)
    print(out)


def cmd_schedule(args, pdir, cfg):
    """Install or remove the daily director run (macOS launchd)."""
    label = "com.viralvideoloop.director"
    plist = Path.home() / "Library/LaunchAgents" / f"{label}.plist"
    if args.action == "status":
        print(f"installed: {plist}" if plist.exists() else "not installed")
        return
    subprocess.run(["launchctl", "unload", str(plist)], capture_output=True)
    if args.action == "remove":
        plist.unlink(missing_ok=True)
        print("removed")
        return
    hour, minute = map(int, args.time.split(":"))
    template = (REPO / "engine" / "schedule" / "director.plist").read_text()
    plist.write_text(template.replace("{{label}}", label).replace("{{repo}}", str(REPO))
                     .replace("{{hour}}", str(hour)).replace("{{minute}}", str(minute)))
    subprocess.run(["launchctl", "load", str(plist)], check=True)
    print(f"installed: director runs every day at {args.time} (log: {REPO}/engine/schedule/director.log)")


def main():
    parser = argparse.ArgumentParser(prog="vvl", description=__doc__.split("\n\n")[0])
    parser.add_argument("--project", help="project folder name (default: active_project in vvl.toml)")
    sub = parser.add_subparsers(dest="cmd")

    def command(name, func, help_text):
        p = sub.add_parser(name, help=help_text)
        p.set_defaults(func=func)
        return p

    sub.add_parser("help", help="show this list")
    command("status", cmd_status, "where everything stands, as text")
    command("build", cmd_build, "regenerate dashboard.html and STATE.md")
    command("start", cmd_start, "build the dashboard and open it in the browser")
    p = command("shot", cmd_shot, "screenshot the dashboard to a PNG")
    p.add_argument("--page", default="", help="page to capture, e.g. cost, posts, team (default: home)")
    p.add_argument("--out")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=1700)

    p = command("add", cmd_add, "add or update a record: vvl add signal --by seller_tiktok --json '{...}'")
    p.add_argument("type", choices=TYPES)
    p.add_argument("fields", nargs="*", help="key=value pairs (values are parsed as JSON when possible)")
    p.add_argument("--by", help="staff id of the writer")
    p.add_argument("--json", help="one record, or a list of records, as JSON")
    p.add_argument("--file", help="path of a JSON file holding one record or a list")
    command("ingest", cmd_ingest, "take JSON files dropped in inbox/<staff id>/ into the database")

    p = command("list", cmd_list, "query records: vvl list signal --where stage=rising --sort relevance")
    p.add_argument("type", choices=TYPES)
    p.add_argument("--where", action="append", help="field=value (repeatable)")
    p.add_argument("--sort")
    p.add_argument("--asc", action="store_true")
    p.add_argument("--days", type=int, help="only records written in the last N days")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--json", action="store_true")
    p = command("get", cmd_get, "print one record")
    p.add_argument("type", choices=TYPES)
    p.add_argument("id")

    p = command("due", cmd_due, "metric snapshots that are due now")
    p.add_argument("--platform")
    p = command("outbox", cmd_outbox, "posts approved and waiting to be published")
    p.add_argument("--platform")
    p = command("todo", cmd_todo, "open human todos; `vvl todo done <id>` ticks one off")
    p.add_argument("action", nargs="?", choices=["done"])
    p.add_argument("id", nargs="?")
    p.add_argument("--by")
    p = command("review", cmd_review, "pending decisions; `vvl review approve|changes <id> --note ...`")
    p.add_argument("action", nargs="?", choices=["approve", "changes"])
    p.add_argument("id", nargs="?")
    p.add_argument("--note")
    p.add_argument("--by")
    command("cost", cmd_cost, "credits left, spent this week, spend by episode and by model")

    command("staff", cmd_staff, "who is on the team and whether each is running")
    p = command("checkin", cmd_checkin, "a staff member reports it ran: vvl checkin seller_tiktok --note ...")
    p.add_argument("staff")
    p.add_argument("--status", default="ok", choices=["ok", "throttled", "paused"])
    p.add_argument("--note")
    p = command("prompt", cmd_prompt, "print the full prompt for a staff member (paste into its bot)")
    p.add_argument("staff")
    p = command("schema", cmd_schema, "print the record formats")
    p.add_argument("type", nargs="?", choices=TYPES)
    p = command("schedule", cmd_schedule, "install/remove the daily director run")
    p.add_argument("action", choices=["install", "remove", "status"])
    p.add_argument("--time", default="08:30")

    args = parser.parse_args()
    if not args.cmd or args.cmd == "help":
        parser.print_help()
        return
    pdir = project_dir(args.project)
    args.func(args, pdir, config(pdir))


if __name__ == "__main__":
    main()
