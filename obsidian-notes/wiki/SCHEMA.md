---
title: "Research Wiki Schema"
created: 2026-06-12
updated: 2026-06-12
type: schema
tags: [schema, research]
sources:
---
# Research Wiki Schema

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
