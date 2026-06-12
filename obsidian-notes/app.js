const STORAGE_KEY = "local-notes.v1";
const SYNC_SETTINGS_KEY = "local-notes.github.v1";

const els = {
  noteList: document.querySelector("#noteList"),
  noteCount: document.querySelector("#noteCount"),
  searchInput: document.querySelector("#searchInput"),
  newNoteBtn: document.querySelector("#newNoteBtn"),
  syncBtn: document.querySelector("#syncBtn"),
  exportBtn: document.querySelector("#exportBtn"),
  importInput: document.querySelector("#importInput"),
  sortBtn: document.querySelector("#sortBtn"),
  titleInput: document.querySelector("#titleInput"),
  editor: document.querySelector("#editor"),
  preview: document.querySelector("#preview"),
  editorGrid: document.querySelector("#editorGrid"),
  editModeBtn: document.querySelector("#editModeBtn"),
  previewModeBtn: document.querySelector("#previewModeBtn"),
  splitModeBtn: document.querySelector("#splitModeBtn"),
  deleteBtn: document.querySelector("#deleteBtn"),
  tagCloud: document.querySelector("#tagCloud"),
  backlinks: document.querySelector("#backlinks"),
  graphCanvas: document.querySelector("#graphCanvas"),
  linkCount: document.querySelector("#linkCount"),
  createdAt: document.querySelector("#createdAt"),
  updatedAt: document.querySelector("#updatedAt"),
  wordCount: document.querySelector("#wordCount"),
  syncStatus: document.querySelector("#syncStatus"),
  githubOwnerInput: document.querySelector("#githubOwnerInput"),
  githubRepoInput: document.querySelector("#githubRepoInput"),
  githubBranchInput: document.querySelector("#githubBranchInput"),
  githubPathInput: document.querySelector("#githubPathInput"),
  githubTokenInput: document.querySelector("#githubTokenInput"),
  saveGithubSettingsBtn: document.querySelector("#saveGithubSettingsBtn"),
  pullGithubBtn: document.querySelector("#pullGithubBtn"),
  pushGithubBtn: document.querySelector("#pushGithubBtn"),
  emptyStateTemplate: document.querySelector("#emptyStateTemplate"),
};

let notes = loadNotes();
let activeId = notes[0]?.id ?? null;
let syncSettings = loadSyncSettings();
let searchTerm = "";
let activeTag = "";
let sortNewestFirst = true;
let saveTimer = null;

function makeId() {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function seedNotes() {
  const now = new Date().toISOString();
  return [
    {
      id: makeId(),
      title: "欢迎使用 Local Notes",
      body: [
        "# 欢迎使用 Local Notes",
        "",
        "这是一个本地 Markdown 笔记工具，适合日常记录、整理想法和维护个人知识库。",
        "",
        "- 使用 `[[每日记录]]` 创建双链",
        "- 使用 `#灵感`、`#学习` 这样的标签归类",
        "- 右侧会显示反向链接和关系图",
        "- 左上角可以导出备份，之后再导入恢复",
        "",
        "## 今天可以开始",
        "",
        "新建一条笔记，把它当成你的收件箱。",
      ].join("\n"),
      createdAt: now,
      updatedAt: now,
    },
    {
      id: makeId(),
      title: "每日记录",
      body: "# 每日记录\n\n#日记\n\n- 今天：\n- 想法：\n- 待办：\n\n关联：[[欢迎使用 Local Notes]]",
      createdAt: now,
      updatedAt: now,
    },
  ];
}

function loadNotes() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (Array.isArray(saved) && saved.length) return saved;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
  const seeded = seedNotes();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(seeded));
  return seeded;
}

function loadSyncSettings() {
  const defaults = {
    owner: "wanghongjian98",
    repo: "wanghongjian98.github.io",
    branch: "main",
    path: "obsidian-notes",
    token: "",
  };
  try {
    const settings = { ...defaults, ...JSON.parse(localStorage.getItem(SYNC_SETTINGS_KEY) || "{}") };
    if (settings.path === "notes") {
      settings.path = "obsidian-notes";
      localStorage.setItem(SYNC_SETTINGS_KEY, JSON.stringify(settings));
    }
    return settings;
  } catch {
    return defaults;
  }
}

function persistSyncSettings() {
  localStorage.setItem(SYNC_SETTINGS_KEY, JSON.stringify(syncSettings));
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
}

function schedulePersist() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(persist, 250);
}

function activeNote() {
  return notes.find((note) => note.id === activeId) ?? notes[0] ?? null;
}

function noteTitle(note) {
  return note.title.trim() || "未命名笔记";
}

function formatDate(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function extractTags(text) {
  return Array.from(
    new Set(Array.from(text.matchAll(/(^|[^\p{L}\p{N}_-])#([\p{L}\p{N}_-]+)/gu)).map((match) => match[2]))
  );
}

function extractLinks(text) {
  return Array.from(new Set(Array.from(text.matchAll(/\[\[([^\]]+)\]\]/g)).map((match) => match[1].trim()).filter(Boolean)));
}

function getFilteredNotes() {
  const term = searchTerm.toLowerCase();
  const filtered = notes.filter((note) => {
    const tags = extractTags(note.body);
    const haystack = `${note.title}\n${note.body}\n${tags.join(" ")}`.toLowerCase();
    return (!term || haystack.includes(term)) && (!activeTag || tags.includes(activeTag));
  });

  return filtered.sort((a, b) => {
    const delta = new Date(b.updatedAt) - new Date(a.updatedAt);
    return sortNewestFirst ? delta : -delta;
  });
}

function renderNoteList() {
  const filtered = getFilteredNotes();
  els.noteList.innerHTML = "";
  els.noteCount.textContent = `${filtered.length} 条笔记`;
  els.sortBtn.textContent = sortNewestFirst ? "最近更新" : "较早更新";

  if (!filtered.length) {
    els.noteList.append(els.emptyStateTemplate.content.cloneNode(true));
    return;
  }

  filtered.forEach((note) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `note-item${note.id === activeId ? " active" : ""}`;
    item.innerHTML = `
      <strong>${escapeHtml(noteTitle(note))}</strong>
      <span>${formatDate(note.updatedAt)} · ${note.path ? "GitHub" : "Local"} · ${makeExcerpt(note.body)}</span>
    `;
    item.addEventListener("click", () => {
      activeId = note.id;
      render();
    });
    els.noteList.append(item);
  });
}

function makeExcerpt(text) {
  const clean = text.replace(/[#>*_`[\]()]/g, " ").replace(/\s+/g, " ").trim();
  return escapeHtml(clean.slice(0, 58) || "空白笔记");
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[char];
  });
}

function renderEditor() {
  const note = activeNote();
  const hasNote = Boolean(note);
  els.titleInput.disabled = !hasNote;
  els.editor.disabled = !hasNote;
  els.deleteBtn.disabled = !hasNote;

  if (!note) {
    els.titleInput.value = "";
    els.editor.value = "";
    els.preview.innerHTML = "";
    return;
  }

  if (document.activeElement !== els.titleInput) els.titleInput.value = note.title;
  if (document.activeElement !== els.editor) els.editor.value = note.body;
  els.preview.innerHTML = markdownToHtml(note.body);
  els.createdAt.textContent = formatDate(note.createdAt);
  els.updatedAt.textContent = formatDate(note.updatedAt);
  els.wordCount.textContent = String(countWords(note.body));
}

function renderSyncSettings() {
  els.githubOwnerInput.value = syncSettings.owner;
  els.githubRepoInput.value = syncSettings.repo;
  els.githubBranchInput.value = syncSettings.branch;
  els.githubPathInput.value = syncSettings.path;
  els.githubTokenInput.value = syncSettings.token;
  renderSyncStatus();
}

function renderSyncStatus(message = "") {
  const note = activeNote();
  if (message) {
    els.syncStatus.textContent = message;
    return;
  }
  if (!syncSettings.token) {
    els.syncStatus.textContent = "未连接";
    return;
  }
  els.syncStatus.textContent = note?.path ? "已关联 md" : "本地草稿";
}

function countWords(text) {
  const latinWords = text.match(/[A-Za-z0-9]+/g) || [];
  const cjkChars = text.match(/[\u4e00-\u9fff]/g) || [];
  return latinWords.length + cjkChars.length;
}

function markdownToHtml(markdown) {
  const lines = escapeHtml(markdown).split("\n");
  const html = [];
  let inList = false;
  let inCode = false;
  let codeLines = [];

  const closeList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };

  lines.forEach((line) => {
    if (line.startsWith("```")) {
      if (inCode) {
        html.push(`<pre><code>${codeLines.join("\n")}</code></pre>`);
        codeLines = [];
      } else {
        closeList();
      }
      inCode = !inCode;
      return;
    }

    if (inCode) {
      codeLines.push(line);
      return;
    }

    if (!line.trim()) {
      closeList();
      html.push("");
      return;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      closeList();
      html.push(`<h${heading[1].length}>${inlineMarkdown(heading[2])}</h${heading[1].length}>`);
      return;
    }

    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.replace(/^[-*]\s+/, ""))}</li>`);
      return;
    }

    if (line.startsWith("&gt; ")) {
      closeList();
      html.push(`<blockquote>${inlineMarkdown(line.slice(5))}</blockquote>`);
      return;
    }

    closeList();
    html.push(`<p>${inlineMarkdown(line)}</p>`);
  });

  closeList();
  if (inCode) html.push(`<pre><code>${codeLines.join("\n")}</code></pre>`);
  return html.join("\n");
}

function inlineMarkdown(text) {
  return text
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[\[([^\]]+)\]\]/g, (_, title) => {
      const exists = notes.some((note) => noteTitle(note) === title.trim());
      return `<a href="#" class="wiki-link${exists ? "" : " missing"}" data-title="${escapeHtml(title.trim())}">[[${escapeHtml(title.trim())}]]</a>`;
    })
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function renderTags() {
  const allTags = new Map();
  notes.forEach((note) => {
    extractTags(note.body).forEach((tag) => allTags.set(tag, (allTags.get(tag) || 0) + 1));
  });

  els.tagCloud.innerHTML = "";
  if (!allTags.size) {
    els.tagCloud.innerHTML = '<span class="muted">暂无标签</span>';
    return;
  }

  Array.from(allTags.entries())
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .forEach(([tag, count]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `tag${tag === activeTag ? " active" : ""}`;
      button.textContent = `#${tag} ${count}`;
      button.addEventListener("click", () => {
        activeTag = activeTag === tag ? "" : tag;
        render();
      });
      els.tagCloud.append(button);
    });
}

function renderBacklinks() {
  const note = activeNote();
  els.backlinks.innerHTML = "";
  if (!note) return;

  const title = noteTitle(note);
  const linked = notes.filter((candidate) => candidate.id !== note.id && extractLinks(candidate.body).includes(title));

  if (!linked.length) {
    els.backlinks.innerHTML = '<span class="muted">暂无反向链接</span>';
    return;
  }

  linked.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "backlink";
    button.textContent = noteTitle(item);
    button.addEventListener("click", () => {
      activeId = item.id;
      render();
    });
    els.backlinks.append(button);
  });
}

function renderGraph() {
  const canvas = els.graphCanvas;
  const ctx = canvas.getContext("2d");
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.max(320, Math.floor(rect.width * scale));
  canvas.height = Math.max(220, Math.floor(rect.height * scale));
  ctx.scale(scale, scale);

  const width = canvas.width / scale;
  const height = canvas.height / scale;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#171717";
  ctx.fillRect(0, 0, width, height);

  const current = activeNote();
  if (!current) return;

  const currentTitle = noteTitle(current);
  const directTitles = extractLinks(current.body);
  const backlinkTitles = notes
    .filter((note) => extractLinks(note.body).includes(currentTitle))
    .map(noteTitle);
  const titles = Array.from(new Set([currentTitle, ...directTitles, ...backlinkTitles])).slice(0, 10);
  els.linkCount.textContent = `${Math.max(0, titles.length - 1)} 个链接`;

  const center = { x: width / 2, y: height / 2 };
  const radius = Math.min(width, height) * 0.32;

  const nodes = titles.map((title, index) => {
    if (index === 0) return { title, x: center.x, y: center.y, primary: true };
    const angle = ((index - 1) / Math.max(1, titles.length - 1)) * Math.PI * 2 - Math.PI / 2;
    return {
      title,
      x: center.x + Math.cos(angle) * radius,
      y: center.y + Math.sin(angle) * radius,
      primary: false,
    };
  });

  ctx.strokeStyle = "rgba(105, 184, 168, 0.42)";
  ctx.lineWidth = 1;
  nodes.slice(1).forEach((node) => {
    ctx.beginPath();
    ctx.moveTo(center.x, center.y);
    ctx.lineTo(node.x, node.y);
    ctx.stroke();
  });

  nodes.forEach((node) => {
    ctx.beginPath();
    ctx.fillStyle = node.primary ? "#69b8a8" : "#2c2a27";
    ctx.strokeStyle = node.primary ? "#8ed6c4" : "#565149";
    ctx.arc(node.x, node.y, node.primary ? 18 : 13, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = node.primary ? "#10201d" : "#f2efe8";
    ctx.font = node.primary ? "700 11px Segoe UI" : "11px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(node.title.slice(0, 8), node.x, node.y + 4);
  });
}

function setViewMode(mode) {
  els.editorGrid.className = `editor-grid ${mode}`;
  [
    [els.editModeBtn, "edit"],
    [els.previewModeBtn, "preview-only"],
    [els.splitModeBtn, "split"],
  ].forEach(([button, value]) => button.classList.toggle("active", value === mode));
}

function createNote(title = "未命名笔记", body = "") {
  const now = new Date().toISOString();
  const note = { id: makeId(), title, body, createdAt: now, updatedAt: now, path: "", sha: "" };
  notes.unshift(note);
  activeId = note.id;
  persist();
  render();
  els.titleInput.focus();
  els.titleInput.select();
}

function updateActiveNote(patch) {
  const note = activeNote();
  if (!note) return;
  Object.assign(note, patch, { updatedAt: new Date().toISOString() });
  schedulePersist();
  renderNoteList();
  renderTags();
  renderBacklinks();
  renderGraph();
}

async function deleteActiveNote() {
  const note = activeNote();
  if (!note) return;
  if (!confirm(`删除「${noteTitle(note)}」？`)) return;
  if (note.path && note.sha && syncSettings.token && confirm("同时删除 GitHub 上的 .md 文件？")) {
    renderSyncStatus("删除远端...");
    await deleteRemoteNote(note);
  }
  notes = notes.filter((item) => item.id !== note.id);
  activeId = notes[0]?.id ?? null;
  persist();
  if (!notes.length) createNote();
  render();
}

function exportNotes() {
  const blob = new Blob([JSON.stringify({ exportedAt: new Date().toISOString(), notes }, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `local-notes-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function importNotes(file) {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    try {
      const parsed = JSON.parse(reader.result);
      const incoming = Array.isArray(parsed) ? parsed : parsed.notes;
      if (!Array.isArray(incoming)) throw new Error("Invalid notes file");
      notes = incoming
        .filter((note) => note.title !== undefined && note.body !== undefined)
        .map((note) => ({
          id: note.id || makeId(),
          title: String(note.title),
          body: String(note.body),
          createdAt: note.createdAt || new Date().toISOString(),
          updatedAt: note.updatedAt || new Date().toISOString(),
        }));
      activeId = notes[0]?.id ?? null;
      persist();
      render();
    } catch {
      alert("导入失败：请选择 Local Notes 导出的 JSON 文件。");
    }
  });
  reader.readAsText(file);
}

function saveGithubSettings() {
  syncSettings = {
    owner: els.githubOwnerInput.value.trim(),
    repo: els.githubRepoInput.value.trim(),
    branch: els.githubBranchInput.value.trim() || "main",
    path: normalizePath(els.githubPathInput.value.trim() || "obsidian-notes"),
    token: els.githubTokenInput.value.trim(),
  };
  persistSyncSettings();
  renderSyncStatus("设置已保存");
}

function normalizePath(path) {
  return path.replace(/^\/+|\/+$/g, "");
}

function requireGithubSettings() {
  saveGithubSettings();
  if (!syncSettings.owner || !syncSettings.repo || !syncSettings.branch || !syncSettings.path || !syncSettings.token) {
    throw new Error("请先填写 GitHub 设置和 token。");
  }
}

function slugifyTitle(title) {
  const cleaned = title
    .trim()
    .replace(/[\\/:*?"<>|#%{}^~[\]`]+/g, "-")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  return cleaned || `note-${new Date().toISOString().slice(0, 10)}`;
}

function notePath(note) {
  return note.path || `${syncSettings.path}/${slugifyTitle(noteTitle(note))}.md`;
}

function markdownTitle(markdown, fallback) {
  const heading = markdown.match(/^#\s+(.+)$/m);
  return heading ? heading[1].trim() : fallback;
}

function utf8ToBase64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function base64ToUtf8(base64) {
  const binary = atob(base64.replace(/\s/g, ""));
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function githubFetch(path, options = {}) {
  const response = await fetch(`https://api.github.com/repos/${syncSettings.owner}/${syncSettings.repo}${path}`, {
    ...options,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${syncSettings.token}`,
      "X-GitHub-Api-Version": "2022-11-28",
      ...(options.headers || {}),
    },
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(data?.message || `GitHub API ${response.status}`);
  }
  return data;
}

async function getRemoteFile(path) {
  try {
    return await githubFetch(`/contents/${encodeURIComponentPath(path)}?ref=${encodeURIComponent(syncSettings.branch)}`);
  } catch (error) {
    if (String(error.message).includes("Not Found")) return null;
    throw error;
  }
}

function encodeURIComponentPath(path) {
  return path.split("/").map(encodeURIComponent).join("/");
}

async function saveNoteToGithub(note) {
  if (!note) throw new Error("当前没有可同步的笔记。");
  requireGithubSettings();
  renderSyncStatus("保存中...");
  const path = notePath(note);
  const remote = note.sha ? { sha: note.sha } : await getRemoteFile(path);
  const result = await githubFetch(`/contents/${encodeURIComponentPath(path)}`, {
    method: "PUT",
    body: JSON.stringify({
      message: `Update note: ${noteTitle(note)}`,
      content: utf8ToBase64(note.body),
      branch: syncSettings.branch,
      sha: remote?.sha,
    }),
  });
  note.path = result.content.path;
  note.sha = result.content.sha;
  note.updatedAt = new Date().toISOString();
  persist();
  render();
  renderSyncStatus("已保存");
}

async function pushAllNotesToGithub() {
  requireGithubSettings();
  for (let index = 0; index < notes.length; index += 1) {
    renderSyncStatus(`推送 ${index + 1}/${notes.length}`);
    await saveNoteToGithub(notes[index]);
  }
  renderSyncStatus("全部已推送");
}

async function pullNotesFromGithub() {
  requireGithubSettings();
  renderSyncStatus("拉取中...");
  let listing = [];
  try {
    listing = await githubFetch(`/contents/${encodeURIComponentPath(syncSettings.path)}?ref=${encodeURIComponent(syncSettings.branch)}`);
  } catch (error) {
    if (!String(error.message).includes("Not Found")) throw error;
  }
  const files = Array.isArray(listing) ? listing.filter((item) => item.type === "file" && item.name.endsWith(".md")) : [];
  const pulled = [];

  for (const file of files) {
    const detail = await githubFetch(`/contents/${encodeURIComponentPath(file.path)}?ref=${encodeURIComponent(syncSettings.branch)}`);
    const body = base64ToUtf8(detail.content || "");
    const title = markdownTitle(body, file.name.replace(/\.md$/i, ""));
    const existing = notes.find((note) => note.path === file.path || noteTitle(note) === title);
    const now = new Date().toISOString();
    pulled.push({
      id: existing?.id || makeId(),
      title,
      body,
      path: file.path,
      sha: detail.sha,
      createdAt: existing?.createdAt || now,
      updatedAt: now,
    });
  }

  const localOnly = notes.filter((note) => !note.path || !pulled.some((remote) => remote.path === note.path));
  notes = [...pulled, ...localOnly];
  activeId = notes[0]?.id ?? null;
  persist();
  render();
  renderSyncStatus(`拉取 ${pulled.length} 条`);
}

async function deleteRemoteNote(note) {
  if (!syncSettings.token || !note.path || !note.sha) return;
  await githubFetch(`/contents/${encodeURIComponentPath(note.path)}`, {
    method: "DELETE",
    body: JSON.stringify({
      message: `Delete note: ${noteTitle(note)}`,
      branch: syncSettings.branch,
      sha: note.sha,
    }),
  });
}

async function runGithubAction(action) {
  try {
    await action();
  } catch (error) {
    renderSyncStatus("同步失败");
    alert(error.message);
  }
}

function bindEvents() {
  els.newNoteBtn.addEventListener("click", () => createNote());
  els.syncBtn.addEventListener("click", () => runGithubAction(() => saveNoteToGithub(activeNote())));
  els.exportBtn.addEventListener("click", exportNotes);
  els.importInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) importNotes(file);
    event.target.value = "";
  });
  els.sortBtn.addEventListener("click", () => {
    sortNewestFirst = !sortNewestFirst;
    renderNoteList();
  });
  els.searchInput.addEventListener("input", (event) => {
    searchTerm = event.target.value.trim();
    renderNoteList();
  });
  els.titleInput.addEventListener("input", (event) => {
    updateActiveNote({ title: event.target.value });
  });
  els.editor.addEventListener("input", (event) => {
    updateActiveNote({ body: event.target.value });
    els.preview.innerHTML = markdownToHtml(event.target.value);
    els.wordCount.textContent = String(countWords(event.target.value));
  });
  els.deleteBtn.addEventListener("click", () => runGithubAction(deleteActiveNote));
  els.saveGithubSettingsBtn.addEventListener("click", saveGithubSettings);
  els.pullGithubBtn.addEventListener("click", () => runGithubAction(pullNotesFromGithub));
  els.pushGithubBtn.addEventListener("click", () => runGithubAction(pushAllNotesToGithub));
  els.editModeBtn.addEventListener("click", () => setViewMode("edit"));
  els.previewModeBtn.addEventListener("click", () => setViewMode("preview-only"));
  els.splitModeBtn.addEventListener("click", () => setViewMode("split"));
  els.preview.addEventListener("click", (event) => {
    const link = event.target.closest(".wiki-link");
    if (!link) return;
    event.preventDefault();
    const title = link.dataset.title;
    const existing = notes.find((note) => noteTitle(note) === title);
    if (existing) {
      activeId = existing.id;
      render();
    } else {
      createNote(title, `# ${title}\n\n`);
    }
  });
  window.addEventListener("resize", renderGraph);
}

function render() {
  renderNoteList();
  renderEditor();
  renderTags();
  renderBacklinks();
  renderGraph();
  renderSyncStatus();
}

bindEvents();
renderSyncSettings();
render();
