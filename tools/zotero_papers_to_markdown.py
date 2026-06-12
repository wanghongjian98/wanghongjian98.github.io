from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: pdfplumber. Install it with `python -m pip install pdfplumber`.") from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
ZOTERO_DIR = Path.home() / "Zotero"
ZOTERO_DB = ZOTERO_DIR / "zotero.sqlite"
ZOTERO_STORAGE = ZOTERO_DIR / "storage"
OUTPUT_DIR = REPO_ROOT / "obsidian-notes" / "papers"
MANIFEST_PATH = OUTPUT_DIR / "_generation_manifest.json"
FAILED_PATH = OUTPUT_DIR / "_failed.md"

FIELD_NAMES = {
    "title",
    "abstractNote",
    "date",
    "publicationTitle",
    "proceedingsTitle",
    "conferenceName",
    "DOI",
    "url",
    "publisher",
    "reportNumber",
    "institution",
    "archiveID",
    "citationKey",
}

SECTION_PATTERNS = {
    "abstract": re.compile(r"^\s*(abstract|summary)\s*$", re.I),
    "introduction": re.compile(r"^\s*(\d+\.?\s*)?(introduction|background)\s*$", re.I),
    "methods": re.compile(r"^\s*(\d+\.?\s*)?(methods?|methodology|materials and methods|approach)\s*$", re.I),
    "results": re.compile(r"^\s*(\d+\.?\s*)?(results?|experiments?|evaluation)\s*$", re.I),
    "discussion": re.compile(r"^\s*(\d+\.?\s*)?(discussion|conclusion|conclusions|limitations?)\s*$", re.I),
}

STOPWORDS = {
    "about", "after", "again", "against", "also", "among", "based", "because", "been", "before",
    "being", "between", "both", "could", "data", "does", "during", "each", "from", "have", "into",
    "more", "most", "only", "other", "over", "paper", "present", "proposed", "show", "shown", "such",
    "than", "that", "their", "there", "these", "this", "through", "using", "were", "which", "while",
    "with", "within", "without", "would", "study", "method", "methods", "result", "results",
}


@dataclass
class Paper:
    item_id: int
    key: str
    item_type: str
    fields: dict[str, str] = field(default_factory=dict)
    creators: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    collections: list[str] = field(default_factory=list)
    pdf_path: Path | None = None
    attachment_key: str = ""

    @property
    def title(self) -> str:
        return self.fields.get("title", f"Zotero item {self.key}")

    @property
    def year(self) -> str:
        match = re.search(r"(19|20)\d{2}", self.fields.get("date", ""))
        return match.group(0) if match else "undated"

    @property
    def venue(self) -> str:
        for key in ("publicationTitle", "proceedingsTitle", "conferenceName", "institution", "publisher"):
            if self.fields.get(key):
                return self.fields[key]
        return self.item_type


def connect_zotero() -> sqlite3.Connection:
    uri = f"file:{ZOTERO_DB.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=30)


def fetch_fields(cur: sqlite3.Cursor, item_ids: list[int]) -> dict[int, dict[str, str]]:
    if not item_ids:
        return {}
    placeholders = ",".join("?" for _ in item_ids)
    rows = cur.execute(
        f"""
        select id.itemID, fc.fieldName, idv.value
        from itemData id
        join fieldsCombined fc on fc.fieldID = id.fieldID
        join itemDataValues idv on idv.valueID = id.valueID
        where id.itemID in ({placeholders})
          and fc.fieldName in ({",".join("?" for _ in FIELD_NAMES)})
        """,
        [*item_ids, *sorted(FIELD_NAMES)],
    ).fetchall()
    result: dict[int, dict[str, str]] = defaultdict(dict)
    for item_id, name, value in rows:
        result[item_id][name] = str(value)
    return result


def fetch_creators(cur: sqlite3.Cursor, item_ids: list[int]) -> dict[int, list[str]]:
    if not item_ids:
        return {}
    placeholders = ",".join("?" for _ in item_ids)
    rows = cur.execute(
        f"""
        select ic.itemID, c.firstName, c.lastName, c.fieldMode
        from itemCreators ic
        join creators c on c.creatorID = ic.creatorID
        where ic.itemID in ({placeholders})
        order by ic.itemID, ic.orderIndex
        """,
        item_ids,
    ).fetchall()
    result: dict[int, list[str]] = defaultdict(list)
    for item_id, first, last, field_mode in rows:
        if field_mode == 1:
            name = (last or first or "").strip()
        else:
            name = " ".join(part for part in [first, last] if part).strip()
        if name:
            result[item_id].append(name)
    return result


def fetch_tags(cur: sqlite3.Cursor, item_ids: list[int]) -> dict[int, list[str]]:
    if not item_ids:
        return {}
    placeholders = ",".join("?" for _ in item_ids)
    rows = cur.execute(
        f"""
        select it.itemID, t.name
        from itemTags it
        join tags t on t.tagID = it.tagID
        where it.itemID in ({placeholders})
        order by lower(t.name)
        """,
        item_ids,
    ).fetchall()
    result: dict[int, list[str]] = defaultdict(list)
    for item_id, tag in rows:
        if tag:
            result[item_id].append(tag)
    return result


def collection_paths(cur: sqlite3.Cursor) -> dict[int, str]:
    rows = cur.execute("select collectionID, collectionName, parentCollectionID from collections").fetchall()
    names = {row[0]: row[1] for row in rows}
    parents = {row[0]: row[2] for row in rows}

    def path_for(collection_id: int) -> str:
        parts = []
        current = collection_id
        seen = set()
        while current and current not in seen:
            seen.add(current)
            parts.append(names.get(current, ""))
            current = parents.get(current)
        return " / ".join(reversed([p for p in parts if p]))

    return {collection_id: path_for(collection_id) for collection_id in names}


def fetch_collections(cur: sqlite3.Cursor, item_ids: list[int]) -> dict[int, list[str]]:
    if not item_ids:
        return {}
    paths = collection_paths(cur)
    placeholders = ",".join("?" for _ in item_ids)
    rows = cur.execute(
        f"""
        select ci.itemID, ci.collectionID
        from collectionItems ci
        where ci.itemID in ({placeholders})
        order by ci.itemID
        """,
        item_ids,
    ).fetchall()
    result: dict[int, list[str]] = defaultdict(list)
    for item_id, collection_id in rows:
        path = paths.get(collection_id)
        if path:
            result[item_id].append(path)
    return result


def attachment_path(attachment_key: str, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    if raw_path.startswith("storage:"):
        return ZOTERO_STORAGE / attachment_key / raw_path.split(":", 1)[1]
    return Path(raw_path).expanduser()


def load_papers() -> list[Paper]:
    con = connect_zotero()
    try:
        cur = con.cursor()
        rows = cur.execute(
            """
            select p.itemID, p.key, it.typeName, a.key, ia.path
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

        by_item: dict[int, Paper] = {}
        for item_id, key, item_type, attachment_key, raw_path in rows:
            path = attachment_path(attachment_key, raw_path)
            if not path or not path.exists():
                continue
            if item_id not in by_item:
                by_item[item_id] = Paper(
                    item_id=item_id,
                    key=key,
                    item_type=item_type,
                    pdf_path=path,
                    attachment_key=attachment_key,
                )

        item_ids = list(by_item)
        fields = fetch_fields(cur, item_ids)
        creators = fetch_creators(cur, item_ids)
        tags = fetch_tags(cur, item_ids)
        collections = fetch_collections(cur, item_ids)
        for item_id, paper in by_item.items():
            paper.fields = fields.get(item_id, {})
            paper.creators = creators.get(item_id, [])
            paper.tags = tags.get(item_id, [])
            paper.collections = collections.get(item_id, [])
        return list(by_item.values())
    finally:
        con.close()


def slugify(text: str, fallback: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    text = re.sub(r"-+", "-", text)
    return text[:90].strip("-") or fallback


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_pdf(path: Path, max_pages: int | None = None) -> tuple[list[dict], str]:
    pages: list[dict] = []
    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        selected = pdf.pages[:max_pages] if max_pages else pdf.pages
        for idx, page in enumerate(selected, start=1):
            text = clean_text(page.extract_text(layout=True) or "")
            pages.append({"page": idx, "text": text})
    return pages, f"{len(pages)}/{total_pages}"


def section_map(pages: list[dict]) -> dict[str, list[int]]:
    sections: dict[str, list[int]] = defaultdict(list)
    for page in pages:
        lines = [clean_text(line) for line in page["text"].splitlines()]
        for line in lines:
            if len(line) > 90:
                continue
            for name, pattern in SECTION_PATTERNS.items():
                if pattern.match(line):
                    sections[name].append(page["page"])
    return {name: sorted(set(nums)) for name, nums in sections.items()}


def candidate_text(paper: Paper, pages: list[dict]) -> str:
    parts = [paper.title, paper.fields.get("abstractNote", "")]
    parts.extend(page["text"] for page in pages[: min(8, len(pages))])
    return " ".join(parts)


def keywords(text: str, limit: int = 12) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+-]{3,}", text)
    counts = Counter(w.lower() for w in words if w.lower() not in STOPWORDS and not w.isdigit())
    selected = []
    for word, _count in counts.most_common(limit * 2):
        if any(word in existing or existing in word for existing in selected):
            continue
        selected.append(word)
        if len(selected) >= limit:
            break
    return selected


def infer_topic_terms(paper: Paper, kws: list[str]) -> list[str]:
    terms = []
    for source in [paper.title, " ".join(paper.tags), " ".join(kws)]:
        lower = source.lower()
        if "event" in lower:
            terms.append("event-based imaging")
        if "tomograph" in lower or "ct" in lower or "x-ray" in lower or "xray" in lower:
            terms.append("X-ray tomography")
        if "gaussian" in lower or "nerf" in lower or "radiance" in lower:
            terms.append("neural 3D representation")
        if "deblur" in lower or "motion" in lower:
            terms.append("motion restoration")
        if "diffusion" in lower or "score" in lower:
            terms.append("generative priors")
        if "microscop" in lower or "light field" in lower:
            terms.append("computational microscopy")
    return sorted(set(terms)) or kws[:4]


def first_author_label(creators: list[str]) -> str:
    if not creators:
        return "Unknown authors"
    if len(creators) == 1:
        return creators[0]
    return f"{creators[0]} et al."


def year_sort_key(year: str) -> tuple[int, int]:
    if re.fullmatch(r"(19|20)\d{2}", year or ""):
        return (1, int(year))
    return (0, 0)


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def bullet_list(items: Iterable[str]) -> str:
    values = [item for item in items if item]
    return "\n".join(f"- {item}" for item in values) if values else "- Not recorded."


def public_note(paper: Paper, pages: list[dict], page_status: str, pdf_digest: str) -> str:
    sections = section_map(pages)
    text = candidate_text(paper, pages)
    kws = keywords(text)
    topics = infer_topic_terms(paper, kws)
    source_pages = ", ".join(f"{name}: p.{', '.join(map(str, nums[:4]))}" for name, nums in sections.items()) or "Section headings not reliably detected."
    doi = paper.fields.get("DOI", "")
    url = paper.fields.get("url", "")
    abstract_present = "yes" if paper.fields.get("abstractNote") else "no"
    collection_text = bullet_list(paper.collections)
    tag_text = bullet_list(paper.tags)
    creator_text = ", ".join(paper.creators[:12]) + (" et al." if len(paper.creators) > 12 else "")
    terms_table = "\n".join(f"| {md_escape(term)} | recurring term detected from title/metadata/PDF text |" for term in kws[:10])

    return f"""---
title: "{paper.title.replace('"', "'")}"
year: "{paper.year}"
zotero_key: "{paper.key}"
source: "Zotero local PDF"
public_version: true
generated: "{datetime.now(timezone.utc).isoformat()}"
---

# {paper.title}

> Public reading note generated from a local Zotero PDF. This file intentionally avoids full original text, full translation, and figure/table reproduction because this GitHub Pages repository is public.

## Metadata

| Field | Value |
|---|---|
| Authors | {md_escape(creator_text or "Not recorded")} |
| Year | {md_escape(paper.year)} |
| Venue | {md_escape(paper.venue)} |
| Item type | {md_escape(paper.item_type)} |
| DOI | {md_escape(doi or "Not recorded")} |
| URL | {md_escape(url or "Not recorded")} |
| Zotero key | `{paper.key}` |
| PDF pages read | {md_escape(page_status)} |
| PDF hash | `{pdf_digest[:16]}` |
| Abstract in Zotero | {abstract_present} |

## Collections

{collection_text}

## Tags

{tag_text}

## Terminology Ledger

| Canonical term | Note |
|---|---|
{terms_table or "| Not enough text extracted | No recurring terms detected |"}

## Chinese Reading Note

这篇论文由 {first_author_label(paper.creators)} 发表，主题集中在 {", ".join(topics)}。脚本已按 nature-reader 的 source-map-first 思路读取本地 PDF，并用章节位置、术语表和元数据生成公开版阅读笔记；由于目标仓库是公开 GitHub Pages，本文件不包含论文全文原文、全文中文翻译或完整图表复刻。

## Core Problem

- 论文题名和 PDF 高频术语显示，核心问题与 {", ".join(topics[:3])} 相关。
- 适合从 Zotero collection 和 tags 中继续判断它在你的研究图谱中的位置。
- 若需要真正的逐段中英对照，应在本机私有目录生成，不上传到公开 repo。

## Method / Approach

- 公开版仅记录方法线索，不复写论文正文。
- 高频术语：{", ".join(kws[:8]) if kws else "not enough extractable text"}。
- 章节锚点：{source_pages}

## Contribution

- 该条目已纳入本地 Zotero PDF 文献库，并具备可追溯的 Zotero key 和 PDF hash。
- 可作为后续人工精读、journal club、或私有全文 reader 的入口。
- 如果 DOI/URL 存在，建议从原始出版页面核对最终版本和补充材料。

## Limitations / Reading Cautions

- 这是公开摘要版，不能替代完整 paper.md bilingual reader。
- 自动章节识别依赖 PDF 文本层；双栏、公式、页眉页脚可能影响抽取。
- 图表没有上传到公开 repo；需要图文对应时应在本机私有 reader 中处理。

## Reproducibility / Follow-up

- Re-run script: `python tools/zotero_papers_to_markdown.py --force`
- Zotero item key: `{paper.key}`
- Attachment key: `{paper.attachment_key}`
- DOI: {doi or "Not recorded"}
- URL: {url or "Not recorded"}
"""


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"generated": {}, "failures": []}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_index(records: list[dict]) -> None:
    by_year: dict[str, list[dict]] = defaultdict(list)
    by_collection: dict[str, list[dict]] = defaultdict(list)
    for record in sorted(records, key=lambda r: (r.get("year", ""), r.get("title", "")), reverse=True):
        by_year[record.get("year") or "undated"].append(record)
        for collection in record.get("collections") or ["Unsorted"]:
            by_collection[collection].append(record)

    lines = [
        "# Zotero Paper Library",
        "",
        "Public, copyright-safe reading notes generated from local Zotero PDFs.",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Papers: {len(records)}",
        "",
        "## By Year",
        "",
    ]
    for year in sorted(by_year.keys(), key=year_sort_key, reverse=True):
        lines.append(f"### {year}")
        for record in by_year[year]:
            lines.append(f"- [{record['title']}]({record['file']}) — {record.get('authors', 'Unknown')} ({record.get('venue', 'Unknown venue')})")
        lines.append("")

    lines.extend(["## By Collection", ""])
    for collection in sorted(by_collection.keys(), key=str.lower):
        lines.append(f"### {collection}")
        for record in sorted(by_collection[collection], key=lambda r: r["title"].lower()):
            lines.append(f"- [{record['title']}]({record['file']}) — {record.get('year', 'undated')}")
        lines.append("")

    (OUTPUT_DIR / "index.md").write_text("\n".join(lines), encoding="utf-8")


def write_failed(failures: list[dict]) -> None:
    lines = ["# Failed Zotero Paper Exports", ""]
    if not failures:
        lines.append("No failures in the latest run.")
    else:
        for failure in failures:
            lines.append(f"- `{failure.get('key', 'unknown')}` {failure.get('title', '')}: {failure.get('error', '')}")
    FAILED_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prune_stale_markdown(records: list[dict]) -> list[str]:
    keep = {"index.md", "_failed.md"}
    keep.update(record["file"] for record in records if record.get("file"))
    removed = []
    for path in OUTPUT_DIR.glob("*.md"):
        if path.name not in keep:
            path.unlink()
            removed.append(path.name)
    return removed


def run(args: argparse.Namespace) -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    papers = load_papers()
    papers.sort(key=lambda p: (year_sort_key(p.year), p.title.lower()), reverse=True)
    if args.limit:
        papers = papers[: args.limit]

    if args.dry_run:
        print(f"zotero_db={ZOTERO_DB}")
        print(f"output_dir={OUTPUT_DIR}")
        print(f"papers_with_existing_pdf={len(papers)}")
        for paper in papers[:5]:
            print(f"- {paper.key} {paper.year} {paper.title} :: {paper.pdf_path}")
        return 0

    manifest = load_manifest()
    generated = manifest.setdefault("generated", {})
    failures: list[dict] = []
    records: list[dict] = []
    existing_records = {
        key: value for key, value in generated.items() if isinstance(value, dict) and value.get("file")
    }
    old_file_counts = Counter(record.get("file", "") for record in existing_records.values())

    for index, paper in enumerate(papers, start=1):
        assert paper.pdf_path is not None
        fallback = f"{paper.year}-{paper.key.lower()}"
        filename = f"{paper.year}-{slugify(paper.title, fallback)}-{paper.key.lower()}.md"
        note_path = OUTPUT_DIR / filename
        try:
            digest = file_hash(paper.pdf_path)
            previous = generated.get(paper.key, {})
            if (
                not args.force
                and note_path.exists()
                and previous.get("pdf_sha256") == digest
                and previous.get("file") == filename
            ):
                records.append(previous)
                print(f"[{index}/{len(papers)}] skip {paper.key} {paper.title}")
                continue
            old_file = previous.get("file")
            old_path = OUTPUT_DIR / old_file if old_file else None
            if (
                not args.force
                and previous.get("pdf_sha256") == digest
                and old_path
                and old_path.exists()
                and old_file_counts.get(old_file, 0) == 1
            ):
                old_path.replace(note_path)
                previous["file"] = filename
                previous["generated_at"] = datetime.now(timezone.utc).isoformat()
                generated[paper.key] = previous
                records.append(previous)
                print(f"[{index}/{len(papers)}] migrated {paper.key} {filename}")
                continue

            pages, page_status = extract_pdf(paper.pdf_path, max_pages=args.max_pages)
            note_path.write_text(public_note(paper, pages, page_status, digest), encoding="utf-8")
            record = {
                "key": paper.key,
                "title": paper.title,
                "year": paper.year,
                "authors": first_author_label(paper.creators),
                "venue": paper.venue,
                "file": filename,
                "collections": paper.collections,
                "tags": paper.tags,
                "pdf_sha256": digest,
                "pdf_pages_read": page_status,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            generated[paper.key] = record
            records.append(record)
            print(f"[{index}/{len(papers)}] wrote {filename}")
        except Exception as exc:  # noqa: BLE001 - batch job should keep going
            failure = {"key": paper.key, "title": paper.title, "error": repr(exc)}
            failures.append(failure)
            print(f"[{index}/{len(papers)}] failed {paper.key}: {exc}", file=sys.stderr)
            if args.stop_on_error:
                break

    for key, record in existing_records.items():
        if key not in {r["key"] for r in records} and (OUTPUT_DIR / record.get("file", "")).exists():
            records.append(record)

    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["source"] = "local Zotero database"
    manifest["output_dir"] = str(OUTPUT_DIR.relative_to(REPO_ROOT))
    manifest["paper_count"] = len(records)
    manifest["failures"] = failures
    save_manifest(manifest)
    write_index(records)
    write_failed(failures)
    if args.prune_stale:
        removed = prune_stale_markdown(records)
        print(f"pruned_stale_markdown={len(removed)}")
    print(f"generated_records={len(records)}")
    print(f"failures={len(failures)}")
    return 1 if failures and args.fail_on_error else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate public Markdown notes from local Zotero PDFs.")
    parser.add_argument("--dry-run", action="store_true", help="Only print Zotero/PDF discovery stats.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of papers processed.")
    parser.add_argument("--force", action="store_true", help="Regenerate notes even when PDF hash is unchanged.")
    parser.add_argument("--max-pages", type=int, default=0, help="Read only the first N pages; 0 reads the full PDF.")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop at first paper failure.")
    parser.add_argument("--fail-on-error", action="store_true", help="Return non-zero if any paper failed.")
    parser.add_argument("--prune-stale", action="store_true", help="Delete generated paper markdown files no longer referenced by the manifest.")
    return parser.parse_args()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(run(parse_args()))
