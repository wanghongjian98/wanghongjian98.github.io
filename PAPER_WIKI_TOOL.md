# Paper Wiki Local Tool

This repo includes a local command wrapper for the Zotero PDF paper library and evolving wiki.

Run commands from:

```powershell
C:\Users\wang_h3\Documents\personal page
```

## Common Commands

```powershell
.\paper-wiki.ps1 status
```

Shows paper counts, wiki counts, failures, and Git status.

```powershell
.\paper-wiki.ps1 sync --dry-run
```

Checks whether Zotero can be read and lists the first discovered local PDF items. Close Zotero before a full sync.

```powershell
.\paper-wiki.ps1 sync
```

Reads local Zotero PDF metadata, updates `obsidian-notes/papers/`, then rebuilds `obsidian-notes/wiki/`.

```powershell
.\paper-wiki.ps1 sync --force
```

Regenerates all paper notes even when PDF hashes are unchanged. This can take a long time for hundreds of PDFs.

```powershell
.\paper-wiki.ps1 search "gaussian splatting tomography"
```

Searches the generated paper manifest and prints local Markdown paths.

```powershell
.\paper-wiki.ps1 question "How do neural fields help sparse-view CT?"
```

Creates a durable question page under `obsidian-notes/wiki/questions/` with candidate source papers. Use this as the Karpathy-style accumulation layer: revise the answer over time instead of rediscovering the same fragments.

```powershell
.\paper-wiki.ps1 lint
```

Checks for missing generated paper files, extra stale paper files, and obvious public-safety leaks such as local paths or GitHub tokens.

```powershell
.\paper-wiki.ps1 publish -m "Update paper wiki"
```

Stages paper/wiki/tool changes, commits, rebases from `origin/main`, and pushes to GitHub.

```powershell
.\paper-wiki.ps1 serve
```

Starts a local preview server for `obsidian-notes/` at `http://127.0.0.1:8000/`.

## Workflow

1. Add PDFs to Zotero and make sure the files exist locally.
2. Close Zotero.
3. Run `.\paper-wiki.ps1 sync --dry-run`.
4. Run `.\paper-wiki.ps1 sync`.
5. Use `search` and `question` to evolve the wiki layer.
6. Run `.\paper-wiki.ps1 lint`.
7. Run `.\paper-wiki.ps1 publish -m "Update paper wiki"`.

The public repo should contain summary-level Markdown only. Do not upload full paper text, full translations, PDF files, or reproduced figures/tables.
