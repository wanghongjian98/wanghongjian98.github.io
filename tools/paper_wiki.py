from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = REPO_ROOT / "obsidian-notes" / "papers"
WIKI_DIR = REPO_ROOT / "obsidian-notes" / "wiki"
QUESTIONS_DIR = WIKI_DIR / "questions"
MANIFEST_PATH = PAPERS_DIR / "_generation_manifest.json"
ZOTERO_SCRIPT = REPO_ROOT / "tools" / "zotero_papers_to_markdown.py"
WIKI_SCRIPT = REPO_ROOT / "tools" / "compile_paper_wiki.py"

SENSITIVE_PATTERNS = [
    "github_pat_",
    "ghp_",
    "Bearer ",
    "C:\\Users\\",
    "/Users/",
    "**Original:**",
    "**中文:**",
]


def run_cmd(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(quote(part) for part in cmd))
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, check=check)


def quote(value: str) -> str:
    return f'"{value}"' if re.search(r"\s", value) else value


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"generated": {}, "failures": []}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def records() -> list[dict]:
    manifest = load_manifest()
    return [
        record
        for record in manifest.get("generated", {}).values()
        if isinstance(record, dict) and record.get("file")
    ]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return re.sub(r"-+", "-", text)[:90] or "question"


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[\w+-]{2,}", text, flags=re.UNICODE)]


def searchable_text(record: dict) -> str:
    parts = [
        record.get("title", ""),
        record.get("authors", ""),
        record.get("venue", ""),
        record.get("year", ""),
        " ".join(record.get("tags") or []),
        " ".join(record.get("collections") or []),
    ]
    return " ".join(parts)


def search_records(query: str, limit: int) -> list[tuple[int, dict]]:
    query_tokens = tokenize(query)
    scored: list[tuple[int, dict]] = []
    for record in records():
        haystack = searchable_text(record).lower()
        score = sum(haystack.count(token) for token in query_tokens)
        if score:
            scored.append((score, record))
    scored.sort(key=lambda item: (item[0], item[1].get("year", ""), item[1].get("title", "")), reverse=True)
    return scored[:limit]


def cmd_status(_args: argparse.Namespace) -> int:
    manifest = load_manifest()
    paper_records = records()
    paper_files = list(PAPERS_DIR.glob("*.md")) if PAPERS_DIR.exists() else []
    wiki_files = list(WIKI_DIR.rglob("*.md")) if WIKI_DIR.exists() else []
    failures = manifest.get("failures") or []

    print(f"repo: {REPO_ROOT}")
    print(f"papers: {len(paper_records)} records, {len(paper_files)} markdown files")
    print(f"wiki: {len(wiki_files)} markdown files")
    print(f"manifest: {MANIFEST_PATH if MANIFEST_PATH.exists() else 'missing'}")
    print(f"failures: {len(failures)}")
    print()
    run_cmd(["git", "status", "--short", "--branch"], check=False)
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    zotero_cmd = [sys.executable, str(ZOTERO_SCRIPT), "--prune-stale"]
    if args.force:
        zotero_cmd.append("--force")
    if args.limit:
        zotero_cmd += ["--limit", str(args.limit)]
    if args.max_pages:
        zotero_cmd += ["--max-pages", str(args.max_pages)]
    if args.dry_run:
        zotero_cmd.append("--dry-run")
        run_cmd(zotero_cmd)
        return 0

    run_cmd(zotero_cmd)
    run_cmd([sys.executable, str(WIKI_SCRIPT), "--check"])
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    matches = search_records(args.query, args.limit)
    if not matches:
        print("No matches.")
        return 0
    for score, record in matches:
        path = PAPERS_DIR / record["file"]
        print(f"[{score}] {record.get('year', 'undated')} {record.get('title', 'Untitled')}")
        print(f"    {path}")
    return 0


def cmd_question(args: argparse.Namespace) -> int:
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = slugify(args.question)
    path = QUESTIONS_DIR / f"{timestamp}-{slug}.md"
    matches = search_records(args.question, args.limit)

    lines = [
        "---",
        f"title: {json.dumps(args.question, ensure_ascii=False)}",
        f"created: {datetime.now(timezone.utc).isoformat()}",
        "type: research-question",
        "tags: [question, research]",
        "---",
        "",
        f"# {args.question}",
        "",
        "## Working Answer",
        "",
        "- Capture the current answer here after reviewing the candidate sources below.",
        "- Promote stable conclusions into concept, method, or comparison pages.",
        "",
        "## Candidate Sources",
        "",
    ]
    if matches:
        for score, record in matches:
            lines.append(f"- [{record.get('title', 'Untitled')}](../../papers/{record['file']}) - score {score}, {record.get('year', 'undated')}")
    else:
        lines.append("- No manifest matches yet. Try broader terms or add tags/collections in Zotero.")
    lines.extend(["", "## Notes", "", "- "])

    path.write_text("\n".join(lines), encoding="utf-8")
    print(path)
    return 0


def cmd_lint(_args: argparse.Namespace) -> int:
    paper_records = records()
    expected = {record["file"] for record in paper_records}
    existing = {path.name for path in PAPERS_DIR.glob("*.md") if not path.name.startswith("_") and path.name != "index.md"}
    missing = sorted(expected - existing)
    extra = sorted(existing - expected)

    sensitive_hits: list[tuple[Path, str]] = []
    for base in [PAPERS_DIR, WIKI_DIR]:
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SENSITIVE_PATTERNS:
                if pattern in text:
                    sensitive_hits.append((path, pattern))

    print(f"records={len(paper_records)}")
    print(f"missing_paper_files={len(missing)}")
    print(f"extra_paper_files={len(extra)}")
    print(f"sensitive_hits={len(sensitive_hits)}")
    for path, pattern in sensitive_hits[:20]:
        print(f"- {path}: {pattern}")

    return 1 if missing or extra or sensitive_hits else 0


def cmd_publish(args: argparse.Namespace) -> int:
    run_cmd(["git", "add", "README.md", "obsidian-notes/papers", "obsidian-notes/wiki", "tools", "paper-wiki.ps1", "paper-wiki.bat", "PAPER_WIKI_TOOL.md"])
    status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if status.returncode == 0:
        print("Nothing staged; skip commit and push.")
        return 0
    run_cmd(["git", "commit", "-m", args.message])
    run_cmd(["git", "pull", "--rebase", "origin", "main"])
    run_cmd(["git", "push", "origin", "main"])
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    root = REPO_ROOT / "obsidian-notes"
    if not root.exists():
        raise SystemExit(f"Missing directory: {root}")

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **handler_kwargs):
            super().__init__(*handler_args, directory=str(root), **handler_kwargs)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving {root}")
    print(f"http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local tool for the Zotero paper wiki.")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Show library, wiki, and git status.")
    status.set_defaults(func=cmd_status)

    sync = sub.add_parser("sync", help="Read Zotero PDFs and rebuild the wiki.")
    sync.add_argument("--dry-run", action="store_true", help="Only inspect Zotero discovery.")
    sync.add_argument("--force", action="store_true", help="Regenerate paper notes even when PDFs are unchanged.")
    sync.add_argument("--limit", type=int, default=0, help="Process only the first N Zotero PDF items.")
    sync.add_argument("--max-pages", type=int, default=0, help="Read only the first N pages per PDF.")
    sync.set_defaults(func=cmd_sync)

    search = sub.add_parser("search", help="Search the local paper manifest.")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(func=cmd_search)

    question = sub.add_parser("question", help="Create a durable wiki question page with candidate sources.")
    question.add_argument("question")
    question.add_argument("--limit", type=int, default=12)
    question.set_defaults(func=cmd_question)

    lint = sub.add_parser("lint", help="Check generated files for drift and public-safety leaks.")
    lint.set_defaults(func=cmd_lint)

    publish = sub.add_parser("publish", help="Commit and push paper/wiki updates to origin/main.")
    publish.add_argument("-m", "--message", default="Update paper wiki")
    publish.set_defaults(func=cmd_publish)

    serve = sub.add_parser("serve", help="Serve obsidian-notes locally over HTTP.")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(func=cmd_serve)
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
