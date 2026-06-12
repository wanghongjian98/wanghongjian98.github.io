from __future__ import annotations

import argparse
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
PAPER_DIR = WIKI / "papers"
CONCEPT_DIR = WIKI / "concepts"
METHOD_DIR = WIKI / "methods"
DATASET_DIR = WIKI / "datasets"
OPEN_PROBLEM_DIR = WIKI / "open_problems"
TEMPLATES = ROOT / "templates"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return re.sub(r"-+", "-", text)[:90] or "page"


def title_from_filename(path: Path) -> str:
    first_heading = re.search(r"^#\s+(.+)$", path.read_text(encoding="utf-8", errors="ignore"), re.M)
    return first_heading.group(1).strip() if first_heading else path.stem.replace("-", " ").title()


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)", re.M)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def bullet_items(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            item = line[2:].strip()
            if item and not item.startswith("TODO:"):
                items.append(item)
    return items


def wikilinks(text: str) -> list[str]:
    return sorted(set(match.strip() for match in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)))


def backup(path: Path) -> None:
    if not path.exists():
        return
    backup_dir = path.parent / ".backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, backup_dir / f"{path.stem}.{stamp}{path.suffix}")


def template(name: str, fallback: str) -> str:
    path = TEMPLATES / name
    return path.read_text(encoding="utf-8") if path.exists() else fallback


def ensure_page(directory: Path, title: str, template_name: str, page_type: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{slugify(title)}.md"
    if not path.exists():
        text = template(
            template_name,
            "# {{title}}\n\nType: {{type}}\n\n## Summary\n\nTODO\n\n## Paper Mentions\n\n",
        )
        path.write_text(text.replace("{{title}}", title).replace("{{type}}", page_type), encoding="utf-8")
    return path


def append_once(path: Path, heading: str, lines: list[str]) -> bool:
    if not lines:
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    additions = [line for line in lines if line not in text]
    if not additions:
        return False
    backup(path)
    if f"## {heading}" not in text:
        text = text.rstrip() + f"\n\n## {heading}\n\n"
    text = text.rstrip() + "\n" + "\n".join(additions) + "\n"
    path.write_text(text, encoding="utf-8")
    return True


def method_candidates(text: str) -> list[str]:
    candidates = []
    for item in bullet_items(section(text, "Method"))[:4]:
        phrase = re.sub(r"^\W+|\W+$", "", item)
        phrase = re.split(r"[,.;:]", phrase)[0]
        if 6 <= len(phrase) <= 80:
            candidates.append(phrase)
    return candidates


def dataset_candidates(text: str) -> list[str]:
    candidates = []
    for item in bullet_items(section(text, "Dataset")):
        for match in re.findall(r"\b[A-Z][A-Za-z0-9_-]{2,}\b", item):
            if match.lower() not in {"TODO".lower()}:
                candidates.append(match)
    return sorted(set(candidates))[:8]


def create_open_problem(source_title: str, source_path: Path, text: str, kind: str) -> Path:
    clean = re.sub(r"\[\[|\]\]", "", text)
    title = clean[:90].rstrip(". ")
    path = ensure_page(OPEN_PROBLEM_DIR, title, "open_problem.md", "open_problem")
    rel = source_path.relative_to(WIKI).as_posix()
    line = f"- From [[{source_title}]] (`{rel}`): {kind} - {clean}"
    append_once(path, "Evidence", [line])
    return path


def update_from_paper(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    paper_title = title_from_filename(path)
    paper_link = f"[[{paper_title}]]"
    stats = defaultdict(int)

    for concept in wikilinks(section(text, "Related Concepts")):
        concept_path = ensure_page(CONCEPT_DIR, concept, "concept.md", "concept")
        if append_once(concept_path, "Paper Mentions", [f"- {paper_link}"]):
            stats["concepts"] += 1

    for method in method_candidates(text):
        method_path = ensure_page(METHOD_DIR, method, "method.md", "method")
        if append_once(method_path, "Paper Mentions", [f"- {paper_link}"]):
            stats["methods"] += 1

    for dataset in dataset_candidates(text):
        dataset_path = ensure_page(DATASET_DIR, dataset, "concept.md", "dataset")
        if append_once(dataset_path, "Paper Mentions", [f"- {paper_link}"]):
            stats["datasets"] += 1

    for item in bullet_items(section(text, "Limitations")):
        create_open_problem(paper_title, path, item, "limitation")
        stats["open_problems"] += 1

    for item in bullet_items(section(text, "Future Work")):
        create_open_problem(paper_title, path, item, "future work")
        stats["open_problems"] += 1

    return stats


def update_all() -> dict[str, int]:
    for directory in [PAPER_DIR, CONCEPT_DIR, METHOD_DIR, DATASET_DIR, OPEN_PROBLEM_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    total = defaultdict(int)
    for path in sorted(PAPER_DIR.glob("*.md")):
        stats = update_from_paper(path)
        for key, value in stats.items():
            total[key] += value
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Obsidian wiki pages from structured paper summaries.")
    parser.parse_args()
    stats = update_all()
    print("updated:")
    for key in ["concepts", "methods", "datasets", "open_problems"]:
        print(f"- {key}: {stats.get(key, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
