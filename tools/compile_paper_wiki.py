from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = REPO_ROOT / "obsidian-notes" / "papers"
MANIFEST_PATH = PAPERS_DIR / "_generation_manifest.json"
WIKI_DIR = REPO_ROOT / "obsidian-notes" / "wiki"


TOPIC_RULES = {
    "event-camera": {
        "label": "Event Camera and Neuromorphic Vision",
        "folder": "concepts",
        "patterns": ["event", "neuromorphic", "spike", "spiking", "dvs", "asynchronous"],
    },
    "x-ray-tomography": {
        "label": "X-ray CT and Tomography",
        "folder": "concepts",
        "patterns": ["x-ray", "xray", "ct", "tomography", "tomographic", "radiography", "synchrotron"],
    },
    "sparse-view-reconstruction": {
        "label": "Sparse-view Reconstruction",
        "folder": "methods",
        "patterns": ["sparse-view", "sparse view", "ultrasparse", "limited-angle", "few-view"],
    },
    "neural-fields": {
        "label": "Neural Fields and Implicit Representations",
        "folder": "methods",
        "patterns": ["nerf", "neural field", "implicit neural", "inr", "radiance field"],
    },
    "gaussian-splatting": {
        "label": "Gaussian Splatting",
        "folder": "methods",
        "patterns": ["gaussian splatting", "3dgs", "gaussian representation", "gaussian field"],
    },
    "dynamic-4d-imaging": {
        "label": "Dynamic and 4D Imaging",
        "folder": "concepts",
        "patterns": ["4d", "dynamic", "time-resolved", "ultrafast", "high-speed", "motion"],
    },
    "deblurring-restoration": {
        "label": "Deblurring and Image Restoration",
        "folder": "methods",
        "patterns": ["deblur", "restoration", "super-resolution", "denoising", "interpolation"],
    },
    "computational-microscopy": {
        "label": "Computational Microscopy",
        "folder": "concepts",
        "patterns": ["microscopy", "light field", "ptychography", "phase contrast", "coherent"],
    },
    "diffusion-generative-priors": {
        "label": "Diffusion and Generative Priors",
        "folder": "methods",
        "patterns": ["diffusion", "score", "generative", "prior"],
    },
    "sensor-hardware": {
        "label": "Sensors and Imaging Hardware",
        "folder": "concepts",
        "patterns": ["sensor", "detector", "cmos", "spad", "scintillator", "camera", "beamline"],
    },
}

COMPARISON_RULES = {
    "event-camera-for-3d-reconstruction": {
        "label": "Event Camera for 3D Reconstruction",
        "requires": ["event-camera", "gaussian-splatting"],
        "also": ["neural-fields"],
    },
    "neural-representations-for-tomography": {
        "label": "Neural Representations for Tomography",
        "requires": ["x-ray-tomography"],
        "also": ["neural-fields", "gaussian-splatting", "sparse-view-reconstruction"],
    },
    "dynamic-x-ray-imaging": {
        "label": "Dynamic X-ray Imaging",
        "requires": ["x-ray-tomography", "dynamic-4d-imaging"],
        "also": [],
    },
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return re.sub(r"-+", "-", text) or "untitled"


def load_records() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = [record for record in manifest.get("generated", {}).values() if isinstance(record, dict)]
    return sorted(records, key=lambda r: (year_key(r.get("year")), r.get("title", "").lower()), reverse=True)


def year_key(year: str | None) -> tuple[int, int]:
    if year and re.fullmatch(r"(19|20)\d{2}", year):
        return (1, int(year))
    return (0, 0)


def record_text(record: dict) -> str:
    parts = [
        record.get("title", ""),
        record.get("venue", ""),
        " ".join(record.get("tags") or []),
        " ".join(record.get("collections") or []),
    ]
    return " ".join(parts).lower()


def classify(records: list[dict]) -> dict[str, list[dict]]:
    topics: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        text = record_text(record)
        matched = False
        for slug, rule in TOPIC_RULES.items():
            if any(pattern in text for pattern in rule["patterns"]):
                topics[slug].append(record)
                matched = True
        if not matched:
            topics["needs-review"].append(record)
    return topics


def paper_link(record: dict) -> str:
    return f"[{record.get('title', 'Untitled')}](../papers/{record['file']})"


def wikilink(slug: str, label: str | None = None) -> str:
    return f"[[{slug}{'|' + label if label else ''}]]"


def frontmatter(title: str, page_type: str, tags: list[str], sources: list[str] | None = None) -> str:
    today = date.today().isoformat()
    src = sources or []
    return "\n".join(
        [
            "---",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            f"created: {today}",
            f"updated: {today}",
            f"type: {page_type}",
            f"tags: [{', '.join(tags)}]",
            "sources:",
            *[f"  - {source}" for source in src],
            "---",
            "",
        ]
    )


def write_schema() -> None:
    text = frontmatter("Research Wiki Schema", "schema", ["schema", "research"]) + """# Research Wiki Schema

## Domain

This wiki covers computational imaging, event cameras, X-ray CT/tomography, neural rendering, Gaussian splatting, sparse-view reconstruction, dynamic imaging, and related sensor hardware.

## Layers

- `../papers/`: immutable public-safe source summaries generated from Zotero PDFs.
- `concepts/`: durable topic pages that synthesize multiple papers.
- `methods/`: algorithm and method-family pages.
- `comparisons/`: cross-topic synthesis pages.
- `questions/`: durable answers worth keeping.
- `index.md`: human entry point and catalog.
- `log.md`: append-only maintenance history.

## Conventions

- File names are lowercase slugs with hyphens.
- Every concept/method/comparison page links to at least two other wiki pages when possible.
- Claims should cite paper summary files using Markdown links to `../papers/<file>.md`.
- Public pages must not reproduce full paper text, full translations, or figure/table crops from copyrighted PDFs.
- New source summaries should first update `../papers/`, then re-run `python tools/compile_paper_wiki.py`.

## Maintenance Loop

1. Ingest new Zotero PDFs into `../papers/`.
2. Compile or update concept/method/comparison pages.
3. Ask research questions against the wiki.
4. Promote useful answers into `questions/`.
5. Lint for duplicate topics, orphan pages, stale claims, and missing bridge pages.
"""
    (WIKI_DIR / "SCHEMA.md").write_text(text, encoding="utf-8")


def top_records(records: list[dict], n: int = 12) -> list[dict]:
    return records[:n]


def write_topic_page(slug: str, records: list[dict]) -> None:
    rule = TOPIC_RULES.get(slug, {"label": "Needs Review", "folder": "concepts", "patterns": []})
    folder = WIKI_DIR / rule["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    years = Counter(record.get("year", "undated") for record in records)
    venues = Counter(record.get("venue", "unknown") for record in records)
    tags = [slug, "papers"]
    sources = [f"../papers/{record['file']}" for record in top_records(records, 8)]
    related = [other for other in TOPIC_RULES if other != slug and overlap(records, other)]

    lines = [
        frontmatter(rule["label"], "concept" if rule["folder"] == "concepts" else "method", tags, sources),
        f"# {rule['label']}",
        "",
        f"This page is an LLM-wiki synthesis node compiled from {len(records)} Zotero paper summaries. It is meant to evolve as new papers are ingested.",
        "",
        "## Current Shape",
        "",
        f"- Paper count: {len(records)}",
        f"- Year range: {year_range(records)}",
        f"- Most common venues/types: {', '.join(name for name, _ in venues.most_common(5))}",
        f"- Dense years: {', '.join(f'{year} ({count})' for year, count in years.most_common(6))}",
        "",
        "## Representative Papers",
        "",
    ]
    for record in top_records(records, 20):
        lines.append(f"- {paper_link(record)} — {record.get('authors', 'Unknown')} ({record.get('year', 'undated')})")

    lines.extend(["", "## Research Use", ""])
    lines.extend(research_use_bullets(slug, records))
    lines.extend(["", "## Related Wiki Pages", ""])
    for related_slug in sorted(related)[:12]:
        related_rule = TOPIC_RULES[related_slug]
        lines.append(f"- {wikilink(related_slug, related_rule['label'])}")
    if not related:
        lines.append("- Add links after more synthesis passes.")
    lines.extend(["", "## Maintenance Notes", "", "- Add stronger claims only after manually checking the linked paper summaries.", "- Split this page if it grows into several separable research lines.", ""])
    (folder / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")


def overlap(records: list[dict], other_slug: str) -> bool:
    rule = TOPIC_RULES[other_slug]
    count = 0
    for record in records:
        text = record_text(record)
        if any(pattern in text for pattern in rule["patterns"]):
            count += 1
    return count >= 3


def year_range(records: list[dict]) -> str:
    years = sorted({int(record["year"]) for record in records if re.fullmatch(r"(19|20)\d{2}", str(record.get("year", "")))})
    if not years:
        return "undated-heavy"
    return f"{years[0]}-{years[-1]}"


def research_use_bullets(slug: str, records: list[dict]) -> list[str]:
    defaults = {
        "event-camera": [
            "- Track how asynchronous sensing changes reconstruction, deblurring, 3D, and low-latency vision pipelines.",
            "- Watch bridge papers that combine events with frames, X-ray imaging, NeRF, or Gaussian splatting.",
        ],
        "x-ray-tomography": [
            "- Use this as the hub for CT reconstruction, beamline imaging, dynamic tomography, and sparse-view methods.",
            "- Separate hardware/beamline papers from reconstruction-method papers during future lint passes.",
        ],
        "gaussian-splatting": [
            "- Follow which 3DGS ideas transfer from RGB rendering into CT, event cameras, and dynamic reconstruction.",
            "- Track limitations around physical consistency, attenuation models, and sparse-view stability.",
        ],
        "neural-fields": [
            "- Treat neural fields as a shared representation layer across NeRF, INR tomography, and dynamic imaging.",
            "- Compare continuous representations against Gaussian and classical iterative reconstruction baselines.",
        ],
    }
    return defaults.get(slug, ["- Use this page as the consolidation point for papers assigned to this topic.", "- Promote stable cross-paper insights into explicit claims after manual review."])


def write_comparison_page(slug: str, label: str, records: list[dict], topic_membership: dict[str, list[dict]]) -> None:
    path = WIKI_DIR / "comparisons"
    path.mkdir(parents=True, exist_ok=True)
    rules = COMPARISON_RULES[slug]
    linked_topics = rules["requires"] + rules.get("also", [])
    sources = [f"../papers/{record['file']}" for record in top_records(records, 10)]
    lines = [
        frontmatter(label, "comparison", ["comparison", "research"], sources),
        f"# {label}",
        "",
        "This comparison page is a bridge node. It should accumulate cross-paper distinctions, not duplicate single-paper summaries.",
        "",
        "## Connected Pages",
        "",
    ]
    for topic in linked_topics:
        if topic in TOPIC_RULES:
            lines.append(f"- {wikilink(topic, TOPIC_RULES[topic]['label'])}")
    lines.extend(["", "## Candidate Evidence", ""])
    for record in top_records(records, 20):
        lines.append(f"- {paper_link(record)} — {record.get('year', 'undated')}")
    lines.extend(
        [
            "",
            "## Questions To Keep Updating",
            "",
            "- Which assumptions are shared across these method families?",
            "- Which benchmark or data conditions make the methods incomparable?",
            "- Which papers introduce evidence that should revise older claims?",
            "",
        ]
    )
    (path / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")


def write_index(records: list[dict], topics: dict[str, list[dict]]) -> None:
    lines = [
        frontmatter("Computational Imaging Research Wiki", "index", ["index", "research"]),
        "# Computational Imaging Research Wiki",
        "",
        "This is the compiled wiki layer over the Zotero paper summaries. The source summaries live in `../papers/`; this directory holds evolving synthesis pages.",
        "",
        "## Start Here",
        "",
        "- [[SCHEMA|Schema and maintenance rules]]",
        "- [[log|Maintenance log]]",
        "- [Paper source index](../papers/index.md)",
        "",
        "## Core Concepts",
        "",
    ]
    for slug, rule in sorted(TOPIC_RULES.items(), key=lambda item: item[1]["label"]):
        if rule["folder"] == "concepts" and topics.get(slug):
            lines.append(f"- [[{slug}|{rule['label']}]] — {len(topics[slug])} papers")
    lines.extend(["", "## Method Families", ""])
    for slug, rule in sorted(TOPIC_RULES.items(), key=lambda item: item[1]["label"]):
        if rule["folder"] == "methods" and topics.get(slug):
            lines.append(f"- [[{slug}|{rule['label']}]] — {len(topics[slug])} papers")
    lines.extend(["", "## Comparisons", ""])
    for slug, rule in COMPARISON_RULES.items():
        lines.append(f"- [[{slug}|{rule['label']}]]")
    lines.extend(["", "## Library Snapshot", "", f"- Paper summaries: {len(records)}", f"- Generated: {datetime.now(timezone.utc).isoformat()}", ""])
    (WIKI_DIR / "index.md").write_text("\n".join(lines), encoding="utf-8")


def write_log(records: list[dict], topics: dict[str, list[dict]]) -> None:
    lines = [
        "# Research Wiki Log",
        "",
        f"## {datetime.now(timezone.utc).isoformat()} ingest | Zotero PDF library",
        "",
        f"- Compiled {len(records)} public-safe paper summaries into wiki pages.",
        f"- Topic pages updated: {sum(1 for slug in TOPIC_RULES if topics.get(slug))}.",
        "- Source layer remains immutable and copyright-safe under `../papers/`.",
        "",
    ]
    (WIKI_DIR / "log.md").write_text("\n".join(lines), encoding="utf-8")


def compile_wiki() -> None:
    records = load_records()
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    for subdir in ["concepts", "methods", "comparisons", "questions"]:
        (WIKI_DIR / subdir).mkdir(parents=True, exist_ok=True)

    topics = classify(records)
    write_schema()
    for slug, topic_records in topics.items():
        if slug in TOPIC_RULES and topic_records:
            write_topic_page(slug, topic_records)

    for slug, rule in COMPARISON_RULES.items():
        candidate_records = comparison_records(rule, topics)
        write_comparison_page(slug, rule["label"], candidate_records, topics)

    write_index(records, topics)
    write_log(records, topics)
    print(f"wiki_dir={WIKI_DIR}")
    print(f"paper_records={len(records)}")
    for slug, topic_records in sorted(topics.items()):
        print(f"{slug}={len(topic_records)}")


def comparison_records(rule: dict, topics: dict[str, list[dict]]) -> list[dict]:
    key_to_record: dict[str, dict] = {}
    for topic in rule["requires"] + rule.get("also", []):
        for record in topics.get(topic, []):
            key_to_record[record["key"]] = record
    return sorted(key_to_record.values(), key=lambda r: (year_key(r.get("year")), r.get("title", "").lower()), reverse=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile public Zotero paper summaries into an evolving LLM wiki.")
    parser.add_argument("--check", action="store_true", help="Validate manifest exists before compiling.")
    return parser.parse_args()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    if args.check and not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing manifest: {MANIFEST_PATH}")
    compile_wiki()
