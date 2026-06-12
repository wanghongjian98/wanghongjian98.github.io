$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$RepoRoot\tools\paper_wiki.py" @args
