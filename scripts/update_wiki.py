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

METHOD_CONCEPTS = {
    "Gaussian Splatting",
    "Diffusion Model",
    "Neural Field",
    "Implicit Neural Representation",
    "Sparse-view Reconstruction",
    "Limited-angle Reconstruction",
    "Deblurring",
    "Image Restoration",
    "Tomography",
}

DATASET_STOPWORDS = {
    "Early",
    "Events",
    "First",
    "Number",
    "Table",
    "The",
    "This",
}

KNOWN_DATASETS = [
    "AAPM",
    "Mayo",
    "LIDC",
    "DeepLesion",
    "DSEC",
    "MVSEC",
    "DVS Gesture",
    "CIFAR10-DVS",
    "N-ImageNet",
    "DAVIS",
    "E2PD",
    "BS-ERGB",
    "GoPro",
    "REDS",
    "Vimeo90K",
    "Middlebury",
    "ImageNet",
    "COCO",
    "DTU",
    "LLFF",
    "Blender",
    "Mip-NeRF 360",
    "NeRF Synthetic",
    "D-NeRF",
    "HyperNeRF",
    "DyNeRF",
    "Technicolor",
    "Plenoptic Video",
    "JIGSAWS",
]


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


def clean_enough(item: str) -> bool:
    if item.startswith("TODO:"):
        return False
    if any(marker in item for marker in ["cid:", "â", "�", "~", "\\"]):
        return False
    if not (40 <= len(item) <= 260):
        return False
    if item.count(" ") < 6:
        return False
    if sum(char.isdigit() for char in item) > len(item) * 0.18:
        return False
    words = re.findall(r"[A-Za-z]{2,}", item)
    if words and sum(len(word) for word in words) / len(words) > 14:
        return False
    return True


def open_problem_candidate(item: str) -> bool:
    low = item.lower()
    markers = ["future work", "future research", "limitation", "limitations", "remain challenging", "remains challenging"]
    return clean_enough(item) and any(marker in low for marker in markers)


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
    concepts = wikilinks(section(text, "Related Concepts"))
    return [concept for concept in concepts if concept in METHOD_CONCEPTS]


def dataset_candidates(text: str) -> list[str]:
    body = section(text, "Dataset")
    body_lower = body.lower()
    candidates = [name for name in KNOWN_DATASETS if name.lower() in body_lower]
    return sorted(set(candidates))[:8]


def create_open_problem(source_title: str, source_path: Path, text: str, kind: str) -> Path:
    clean = re.sub(r"\[\[|\]\]", "", text)
    if not clean_enough(clean):
        return OPEN_PROBLEM_DIR / f"{slugify(clean[:90])}.md"
    path = ensure_page(OPEN_PROBLEM_DIR, "Extracted Open Problems", "open_problem.md", "open_problem")
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
        if concept.lower().startswith("todo:") or concept.lower() == "todo":
            continue
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

    for item in bullet_items(section(text, "Limitations"))[:2]:
        if not open_problem_candidate(item):
            continue
        create_open_problem(paper_title, path, item, "limitation")
        stats["open_problems"] += 1

    for item in bullet_items(section(text, "Future Work"))[:2]:
        if not open_problem_candidate(item):
            continue
        create_open_problem(paper_title, path, item, "future work")
        stats["open_problems"] += 1

    return stats


def update_all() -> dict[str, int]:
    for directory in [PAPER_DIR, CONCEPT_DIR, METHOD_DIR, DATASET_DIR, OPEN_PROBLEM_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    total = defaultdict(int)
    for path in sorted(PAPER_DIR.glob("*.md")):
        if path.name == "index.md":
            continue
        stats = update_from_paper(path)
        for key, value in stats.items():
            total[key] += value
    write_indexes()
    return total


def page_links(directory: Path) -> list[str]:
    links = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "index.md":
            continue
        title = title_from_filename(path)
        rel = path.relative_to(WIKI).as_posix()
        links.append(f"- [{title}]({rel})")
    return links


def page_count(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r"^- \[\[", text, re.M))


def link_for(directory: Path, slug: str, label: str) -> str:
    return f"[{label}]({directory.name}/{slug}.md)"


def ranked_links(directory: Path, limit: int = 8) -> list[str]:
    rows = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "index.md":
            continue
        rows.append((page_count(path), title_from_filename(path), path.relative_to(WIKI).as_posix()))
    rows.sort(key=lambda row: (-row[0], row[1].lower()))
    return [f"- [{title}]({rel}) - {count} linked papers" for count, title, rel in rows[:limit]]


def write_indexes() -> None:
    paper_links = page_links(PAPER_DIR)
    concept_links = page_links(CONCEPT_DIR)
    method_links = page_links(METHOD_DIR)
    dataset_links = page_links(DATASET_DIR)
    open_problem_links = page_links(OPEN_PROBLEM_DIR)

    root_lines = [
        "# Research Wiki",
        "",
        "这是从本地 Zotero PDF 自动生成、再逐步人工迭代的 Obsidian-style research wiki。它的目标不是替代精读，而是把几百篇论文沉淀成可导航、可追问、可扩展的研究地图。",
        "",
        "## Dashboard",
        "",
        f"- Paper summaries: {len(paper_links)}",
        f"- Concept pages: {len(concept_links)}",
        f"- Method pages: {len(method_links)}",
        f"- Dataset pages: {len(dataset_links)}",
        f"- Open problem pages: {len(open_problem_links)}",
        "",
        "## How To Use This Wiki",
        "",
        "1. 从下面的 `Research Map` 进入一个主题，而不是从 587 篇论文逐篇翻。",
        "2. 在概念页或方法页里看 `Paper Mentions`，找到高频论文和交叉方向。",
        "3. 把真正精读后的判断写回概念页的 `Summary`、`Key Questions` 或新建 `research_ideas/` 页面。",
        "4. Zotero 新增论文后运行 `python scripts/ingest_zotero.py --max-pages 12` 和 `python scripts/update_wiki.py` 刷新索引。",
        "",
        "## Research Map",
        "",
        "### Event-based Sensing and Neuromorphic Vision",
        "",
        f"- Core concepts: {link_for(CONCEPT_DIR, 'event-camera', 'Event Camera')}, {link_for(CONCEPT_DIR, 'neuromorphic-vision', 'Neuromorphic Vision')}",
        f"- Closely related methods: {link_for(METHOD_DIR, 'deblurring', 'Deblurring')}, {link_for(METHOD_DIR, 'image-restoration', 'Image Restoration')}",
        "- Typical questions: event streams for deblurring, HDR, frame interpolation, optical flow, 3D reconstruction, and low-latency sensing.",
        "",
        "### X-ray CT, Tomography, and Dynamic Imaging",
        "",
        f"- Core concepts: {link_for(CONCEPT_DIR, 'tomography', 'Tomography')}, {link_for(CONCEPT_DIR, 'x-ray-ct', 'X-ray CT')}, {link_for(CONCEPT_DIR, 'dynamic-imaging', 'Dynamic Imaging')}, {link_for(CONCEPT_DIR, '4d-imaging', '4D Imaging')}",
        f"- Closely related methods: {link_for(METHOD_DIR, 'tomography', 'Tomography')}, {link_for(METHOD_DIR, 'sparse-view-reconstruction', 'Sparse-view Reconstruction')}, {link_for(METHOD_DIR, 'neural-field', 'Neural Field')}",
        "- Typical questions: sparse-view CT, limited-angle reconstruction, dynamic/4D tomography, synchrotron imaging, physics-informed reconstruction, and beamline data processing.",
        "",
        "### Neural Representations and Gaussian Splatting",
        "",
        f"- Core concepts: {link_for(CONCEPT_DIR, 'neural-field', 'Neural Field')}, {link_for(CONCEPT_DIR, 'implicit-neural-representation', 'Implicit Neural Representation')}, {link_for(CONCEPT_DIR, 'gaussian-splatting', 'Gaussian Splatting')}",
        f"- Closely related methods: {link_for(METHOD_DIR, 'gaussian-splatting', 'Gaussian Splatting')}, {link_for(METHOD_DIR, 'implicit-neural-representation', 'Implicit Neural Representation')}, {link_for(METHOD_DIR, 'diffusion-model', 'Diffusion Model')}",
        "- Typical questions: continuous scene/volume representation, 3DGS for CT, radiative Gaussian splatting, NeRF/INR baselines, dynamic view synthesis, and physical consistency.",
        "",
        "### Restoration, Priors, and Generative Models",
        "",
        f"- Core concepts: {link_for(CONCEPT_DIR, 'deblurring', 'Deblurring')}, {link_for(CONCEPT_DIR, 'image-restoration', 'Image Restoration')}, {link_for(CONCEPT_DIR, 'diffusion-model', 'Diffusion Model')}",
        f"- Closely related methods: {link_for(METHOD_DIR, 'deblurring', 'Deblurring')}, {link_for(METHOD_DIR, 'image-restoration', 'Image Restoration')}, {link_for(METHOD_DIR, 'diffusion-model', 'Diffusion Model')}",
        "- Typical questions: learned priors, event-guided restoration, low-light/HDR recovery, super-resolution, denoising, and diffusion priors for inverse problems.",
        "",
        "## High-Signal Intersections",
        "",
        f"- {link_for(CONCEPT_DIR, 'event-camera', 'Event Camera')} x {link_for(CONCEPT_DIR, 'gaussian-splatting', 'Gaussian Splatting')}: event-aided 3D reconstruction, deblurring, and novel view synthesis.",
        f"- {link_for(CONCEPT_DIR, 'x-ray-ct', 'X-ray CT')} x {link_for(CONCEPT_DIR, 'gaussian-splatting', 'Gaussian Splatting')}: radiative Gaussian representations and sparse-view tomographic reconstruction.",
        f"- {link_for(CONCEPT_DIR, 'tomography', 'Tomography')} x {link_for(CONCEPT_DIR, 'neural-field', 'Neural Field')}: implicit continuous reconstruction, dynamic CT, and physics-informed neural fields.",
        f"- {link_for(CONCEPT_DIR, 'dynamic-imaging', 'Dynamic Imaging')} x {link_for(CONCEPT_DIR, '4d-imaging', '4D Imaging')}: time-resolved acquisition, motion modeling, and continuous-time reconstruction.",
        f"- {link_for(CONCEPT_DIR, 'diffusion-model', 'Diffusion Model')} x {link_for(METHOD_DIR, 'sparse-view-reconstruction', 'Sparse-view Reconstruction')}: generative priors for underdetermined inverse problems.",
        "",
        "## Suggested Reading Routes",
        "",
        "### Route A: Event Cameras to 3D Reconstruction",
        "",
        f"1. {link_for(CONCEPT_DIR, 'event-camera', 'Event Camera')}",
        f"2. {link_for(METHOD_DIR, 'deblurring', 'Deblurring')}",
        f"3. {link_for(METHOD_DIR, 'gaussian-splatting', 'Gaussian Splatting')}",
        f"4. {link_for(CONCEPT_DIR, 'dynamic-imaging', 'Dynamic Imaging')}",
        "",
        "### Route B: Sparse-view CT to Neural Reconstruction",
        "",
        f"1. {link_for(CONCEPT_DIR, 'x-ray-ct', 'X-ray CT')}",
        f"2. {link_for(METHOD_DIR, 'tomography', 'Tomography')}",
        f"3. {link_for(METHOD_DIR, 'sparse-view-reconstruction', 'Sparse-view Reconstruction')}",
        f"4. {link_for(METHOD_DIR, 'neural-field', 'Neural Field')}",
        f"5. {link_for(METHOD_DIR, 'gaussian-splatting', 'Gaussian Splatting')}",
        "",
        "### Route C: Dynamic 4D Imaging",
        "",
        f"1. {link_for(CONCEPT_DIR, 'dynamic-imaging', 'Dynamic Imaging')}",
        f"2. {link_for(CONCEPT_DIR, '4d-imaging', '4D Imaging')}",
        f"3. {link_for(CONCEPT_DIR, 'tomography', 'Tomography')}",
        f"4. {link_for(METHOD_DIR, 'image-restoration', 'Image Restoration')}",
        "",
        "## Most Connected Pages",
        "",
        "### Concepts",
        "",
        *(ranked_links(CONCEPT_DIR) or ["- None yet."]),
        "",
        "### Methods",
        "",
        *(ranked_links(METHOD_DIR) or ["- None yet."]),
        "",
        "### Datasets",
        "",
        *(ranked_links(DATASET_DIR) or ["- None yet."]),
        "",
        "## Maintenance Loop",
        "",
        "```powershell",
        "cd \"C:\\Users\\wang_h3\\Documents\\personal page\"",
        "python scripts\\ingest_zotero.py --max-pages 12",
        "python scripts\\update_wiki.py",
        "git add wiki scripts templates README.md .gitignore",
        "git commit -m \"Update research wiki\"",
        "git push origin main",
        "```",
        "",
        "## Quality Notes",
        "",
        "- `wiki/papers/` 里的单篇页是 public-safe 自动摘要，只保存元数据、关键词级信号和 Obsidian 链接，不保存 PDF 全文或大段原文。",
        "- 概念页、方法页和数据集页是自动链接骨架。真正有价值的 synthesis 应该逐步人工写入 `Summary`、`Key Questions` 和 `research_ideas/`。",
        "- `open_problems/extracted-open-problems.md` 是候选池，不是最终研究问题清单。需要人工合并、改写和去噪。",
        "",
        "## Sections",
        "",
        "- [Paper index](papers/index.md)",
        "- [Concepts](#concepts)",
        "- [Methods](#methods)",
        "- [Datasets](#datasets)",
        "- [Open Problems](#open-problems)",
        "- [Research ideas](research_ideas/)",
        "",
        "## Concepts",
        "",
        *(concept_links or ["- None yet."]),
        "",
        "## Methods",
        "",
        *(method_links or ["- None yet."]),
        "",
        "## Datasets",
        "",
        *(dataset_links or ["- None yet."]),
        "",
        "## Open Problems",
        "",
        *(open_problem_links or ["- None yet."]),
        "",
    ]
    index_path = WIKI / "index.md"
    backup(index_path)
    index_path.write_text("\n".join(root_lines), encoding="utf-8")

    paper_index = ["# Paper Index", "", *paper_links, ""]
    paper_index_path = PAPER_DIR / "index.md"
    backup(paper_index_path)
    paper_index_path.write_text("\n".join(paper_index), encoding="utf-8")


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
