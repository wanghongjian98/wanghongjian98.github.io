from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI_PAPERS = ROOT / "wiki" / "papers"
TEMPLATE = ROOT / "templates" / "paper.md"

FIELDS = [
    "Problem",
    "Method",
    "Dataset",
    "Loss",
    "Innovation",
    "Limitations",
    "Future Work",
    "Related Concepts",
]

KEYWORDS = {
    "Problem": ["problem", "challenge", "limitation of existing", "we address", "aim", "objective"],
    "Method": ["method", "approach", "framework", "architecture", "pipeline", "algorithm", "we propose"],
    "Dataset": ["dataset", "data set", "benchmark", "experiments on", "collected", "trained on"],
    "Loss": ["loss", "objective function", "regularization", "penalty", "optimization objective"],
    "Innovation": ["novel", "contribution", "innovation", "first", "introduce", "outperform"],
    "Limitations": ["limitation", "fail", "failure", "cannot", "sensitive", "assumption"],
    "Future Work": ["future work", "future research", "remain", "could be", "extension"],
}

CONCEPT_PATTERNS = [
    "Event Camera",
    "Neuromorphic Vision",
    "X-ray CT",
    "Tomography",
    "Sparse-view Reconstruction",
    "Limited-angle Reconstruction",
    "Neural Field",
    "Implicit Neural Representation",
    "Gaussian Splatting",
    "Diffusion Model",
    "Computational Microscopy",
    "Deblurring",
    "Image Restoration",
    "Dynamic Imaging",
    "4D Imaging",
]


@dataclass
class PaperSummary:
    title: str
    slug: str
    source_pdf: Path
    text_chars: int
    fields: dict[str, list[str]]


def extract_pdf_text(path: Path) -> str:
    try:
        import pdfplumber

        chunks = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                chunks.append(page.extract_text() or "")
        text = "\n".join(chunks)
        if text.strip():
            return clean_text(text)
    except Exception:
        pass

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return clean_text("\n".join(page.extract_text() or "" for page in reader.pages))
    except Exception as exc:
        raise SystemExit(f"Could not extract text from {path}: {exc}") from exc


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", compact)
    return [part.strip() for part in parts if 60 <= len(part.strip()) <= 450]


def infer_title(path: Path, text: str) -> str:
    for line in text.splitlines()[:40]:
        line = re.sub(r"\s+", " ", line).strip()
        if 12 <= len(line) <= 180 and not re.search(r"^(abstract|introduction|keywords)\b", line, re.I):
            return line
    return path.stem.replace("_", " ").replace("-", " ").strip().title()


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return re.sub(r"-+", "-", text)[:90] or "paper"


def pick_snippets(text: str, field: str, limit: int = 4) -> list[str]:
    result = []
    lower_keywords = KEYWORDS.get(field, [])
    for sentence in sentences(text):
        low = sentence.lower()
        if any(keyword in low for keyword in lower_keywords):
            result.append(sentence)
        if len(result) >= limit:
            break
    return result or ["TODO: review the PDF and fill this section."]


def related_concepts(text: str) -> list[str]:
    lower = text.lower()
    concepts = [concept for concept in CONCEPT_PATTERNS if concept.lower() in lower]
    acronyms = sorted(set(re.findall(r"\b[A-Z][A-Z0-9]{2,}\b", text)))[:12]
    for acronym in acronyms:
        if acronym not in {"PDF", "IEEE", "CVPR", "ICCV", "ECCV", "MICCAI"}:
            concepts.append(acronym)
    seen = set()
    unique = []
    for concept in concepts:
        key = concept.lower()
        if key not in seen:
            seen.add(key)
            unique.append(concept)
    return unique[:12] or ["TODO: add concepts"]


def summarize(path: Path) -> PaperSummary:
    text = extract_pdf_text(path)
    title = infer_title(path, text)
    fields = {field: pick_snippets(text, field) for field in FIELDS if field != "Related Concepts"}
    fields["Related Concepts"] = [f"[[{concept}]]" for concept in related_concepts(text)]
    return PaperSummary(title=title, slug=slugify(title), source_pdf=path, text_chars=len(text), fields=fields)


def load_template() -> str:
    if TEMPLATE.exists():
        return TEMPLATE.read_text(encoding="utf-8")
    return """# {{title}}

Source PDF: `{{source_pdf}}`

{{sections}}
"""


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render(summary: PaperSummary) -> str:
    sections = []
    for field in FIELDS:
        sections.append(f"## {field}\n\n{bullets(summary.fields[field])}")
    template = load_template()
    return (
        template.replace("{{title}}", summary.title)
        .replace("{{source_pdf}}", str(summary.source_pdf))
        .replace("{{created_at}}", datetime.now(timezone.utc).isoformat())
        .replace("{{text_chars}}", str(summary.text_chars))
        .replace("{{sections}}", "\n\n".join(sections))
    )


def backup(path: Path) -> None:
    if not path.exists():
        return
    backup_dir = path.parent / ".backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, backup_dir / f"{path.stem}.{stamp}{path.suffix}")


def ingest(pdf_path: Path) -> Path:
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")
    WIKI_PAPERS.mkdir(parents=True, exist_ok=True)
    summary = summarize(pdf_path)
    output = WIKI_PAPERS / f"{summary.slug}.md"
    backup(output)
    output.write_text(render(summary), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract one research PDF into a structured Obsidian Markdown summary.")
    parser.add_argument("pdf", help="Path to one PDF file.")
    args = parser.parse_args()
    output = ingest(Path(args.pdf))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
