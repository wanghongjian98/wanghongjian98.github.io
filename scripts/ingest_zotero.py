from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from ingest_pdf import ingest, slugify  # noqa: E402


ZOTERO_DIR = Path.home() / "Zotero"
ZOTERO_DB = ZOTERO_DIR / "zotero.sqlite"
ZOTERO_STORAGE = ZOTERO_DIR / "storage"
WIKI_PAPERS = ROOT / "wiki" / "papers"
MANIFEST = WIKI_PAPERS / "_zotero_ingest_manifest.json"

FIELD_NAMES = {
    "title",
    "date",
    "publicationTitle",
    "proceedingsTitle",
    "conferenceName",
    "DOI",
    "url",
}


@dataclass
class ZoteroPaper:
    item_id: int
    key: str
    title: str
    year: str
    venue: str
    doi: str
    url: str
    attachment_key: str
    pdf_path: Path


def connect() -> sqlite3.Connection:
    uri = f"file:{ZOTERO_DB.as_posix()}?mode=ro&immutable=1"
    return sqlite3.connect(uri, uri=True, timeout=30)


def attachment_path(attachment_key: str, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    if raw_path.startswith("storage:"):
        return ZOTERO_STORAGE / attachment_key / raw_path.split(":", 1)[1]
    return Path(raw_path).expanduser()


def year_from_date(value: str) -> str:
    import re

    match = re.search(r"(19|20)\d{2}", value or "")
    return match.group(0) if match else "undated"


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"items": {}, "failures": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(manifest: dict) -> None:
    WIKI_PAPERS.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_field_map(cur: sqlite3.Cursor, item_ids: list[int]) -> dict[int, dict[str, str]]:
    if not item_ids:
        return {}
    placeholders = ",".join("?" for _ in item_ids)
    field_placeholders = ",".join("?" for _ in FIELD_NAMES)
    rows = cur.execute(
        f"""
        select id.itemID, fc.fieldName, idv.value
        from itemData id
        join fieldsCombined fc on fc.fieldID = id.fieldID
        join itemDataValues idv on idv.valueID = id.valueID
        where id.itemID in ({placeholders})
          and fc.fieldName in ({field_placeholders})
        """,
        [*item_ids, *sorted(FIELD_NAMES)],
    ).fetchall()
    result: dict[int, dict[str, str]] = {}
    for item_id, name, value in rows:
        result.setdefault(item_id, {})[name] = str(value)
    return result


def load_zotero_papers() -> list[ZoteroPaper]:
    con = connect()
    try:
        cur = con.cursor()
        rows = cur.execute(
            """
            select p.itemID, p.key, a.key, ia.path
            from items p
            join itemTypesCombined it on it.itemTypeID = p.itemTypeID
            join itemAttachments ia on ia.parentItemID = p.itemID
            join items a on a.itemID = ia.itemID
            where p.itemID not in (select itemID from deletedItems)
              and a.itemID not in (select itemID from deletedItems)
              and it.typeName not in ('attachment', 'note', 'annotation')
              and (lower(coalesce(ia.contentType, '')) like '%pdf%' or lower(coalesce(ia.path, '')) like '%.pdf')
            order by p.itemID, a.itemID
            """
        ).fetchall()
        by_item: dict[int, tuple[int, str, str, Path]] = {}
        for item_id, key, attachment_key, raw_path in rows:
            path = attachment_path(attachment_key, raw_path)
            if path and path.exists() and item_id not in by_item:
                by_item[item_id] = (item_id, key, attachment_key, path)

        fields = fetch_field_map(cur, list(by_item))
        papers = []
        for item_id, key, attachment_key, path in by_item.values():
            data = fields.get(item_id, {})
            title = data.get("title") or f"Zotero item {key}"
            venue = (
                data.get("publicationTitle")
                or data.get("proceedingsTitle")
                or data.get("conferenceName")
                or "Not recorded"
            )
            papers.append(
                ZoteroPaper(
                    item_id=item_id,
                    key=key,
                    title=title,
                    year=year_from_date(data.get("date", "")),
                    venue=venue,
                    doi=data.get("DOI", ""),
                    url=data.get("url", ""),
                    attachment_key=attachment_key,
                    pdf_path=path,
                )
            )
        return papers
    finally:
        con.close()


def output_slug(paper: ZoteroPaper) -> str:
    return f"{paper.year}-{slugify(paper.title)}-{paper.key.lower()}"


def metadata(paper: ZoteroPaper) -> dict[str, str]:
    return {
        "Zotero key": paper.key,
        "Year": paper.year,
        "Venue": paper.venue,
        "DOI": paper.doi or "Not recorded",
        "URL": paper.url or "Not recorded",
        "Attachment key": paper.attachment_key,
    }


def run(args: argparse.Namespace) -> int:
    papers = load_zotero_papers()
    papers.sort(key=lambda paper: (paper.year, paper.title), reverse=True)
    if args.limit:
        papers = papers[: args.limit]

    if args.dry_run:
        print(f"zotero_db={ZOTERO_DB}")
        print(f"papers_with_existing_pdf={len(papers)}")
        for paper in papers[:10]:
            print(f"- {paper.key} {paper.year} {paper.title} :: {paper.pdf_path}")
        return 0

    manifest = load_manifest()
    items = manifest.setdefault("items", {})
    failures = []
    WIKI_PAPERS.mkdir(parents=True, exist_ok=True)

    for index, paper in enumerate(papers, start=1):
        slug = output_slug(paper)
        output = WIKI_PAPERS / f"{slug}.md"
        if output.exists() and not args.force:
            items[paper.key] = {
                "title": paper.title,
                "year": paper.year,
                "file": output.name,
                "source": f"zotero:{paper.key}",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "existing",
            }
            print(f"[{index}/{len(papers)}] skip {paper.key} {paper.title}")
            if index % 25 == 0:
                manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
                manifest["paper_count"] = len(items)
                manifest["failures"] = failures
                save_manifest(manifest)
            continue
        try:
            written = ingest(
                paper.pdf_path,
                title=paper.title,
                source_label=f"zotero:{paper.key}",
                output_slug=slug,
                max_pages=args.max_pages,
                metadata=metadata(paper),
            )
            items[paper.key] = {
                "title": paper.title,
                "year": paper.year,
                "file": written.name,
                "source": f"zotero:{paper.key}",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "generated",
            }
            print(f"[{index}/{len(papers)}] wrote {written.name}")
        except Exception as exc:  # noqa: BLE001 - keep batch moving
            failure = {"key": paper.key, "title": paper.title, "error": repr(exc)}
            failures.append(failure)
            print(f"[{index}/{len(papers)}] failed {paper.key}: {exc}", file=sys.stderr)
            if args.stop_on_error:
                break
        if index % 25 == 0:
            manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
            manifest["paper_count"] = len(items)
            manifest["failures"] = failures
            save_manifest(manifest)

    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["zotero_db"] = "local Zotero read-only"
    manifest["paper_count"] = len(items)
    manifest["failures"] = failures
    save_manifest(manifest)
    print(f"processed={len(papers)}")
    print(f"manifest_items={len(items)}")
    print(f"failures={len(failures)}")
    return 1 if failures and args.fail_on_error else 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Batch ingest local Zotero PDFs into wiki/papers.")
    parser.add_argument("--dry-run", action="store_true", help="Only list Zotero PDF items.")
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N Zotero PDF items.")
    parser.add_argument("--force", action="store_true", help="Regenerate existing paper summaries.")
    parser.add_argument("--max-pages", type=int, default=12, help="Read first N pages per PDF; 0 reads full PDFs.")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop at the first failed PDF.")
    parser.add_argument("--fail-on-error", action="store_true", help="Return non-zero if any PDF failed.")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
