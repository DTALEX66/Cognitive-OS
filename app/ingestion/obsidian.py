"""Obsidian Input Layer — frontmatter, wikilink, tag, canvas parser

Parses Obsidian-flavoured Markdown (.md) and Canvas (.canvas) files into
structured CoreObject documents with extracted metadata.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from app.ingestion.file import IngestionError, PROJECT_ROOT, _resolve_project_path
from app.ingestion.quality import assess_content_quality
from app.schemas import CoreObject

# ── Public data structures ───────────────────────────────────────────


@dataclass
class ObsidianMetadata:
    """Parsed Obsidian file metadata."""
    title: str | None = None
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)        # wikilink targets
    frontmatter: dict[str, Any] = field(default_factory=dict)
    dataview_fields: dict[str, Any] = field(default_factory=dict)
    is_canvas: bool = False
    canvas_nodes: list[dict[str, Any]] | None = None


SUPPORTED_EXTENSIONS = {'.md', '.markdown', '.canvas'}
MAX_FILE_BYTES = 2_000_000


# ── Frontmatter ──────────────────────────────────────────────────────


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str, str | None]:
    """Extract YAML frontmatter and remaining body.

    Returns (frontmatter_dict, body, title_from_frontmatter).
    """
    pattern = re.compile(
        r'^---\s*\n'         # opening ---
        r'(.*?)'              # frontmatter content (non-greedy)
        r'\n(?:\.{3}|---)'   # closing --- or ...
        r'\s*\n',             # trailing newline
        re.DOTALL,
    )
    match = pattern.match(text)
    if not match:
        return {}, text.strip(), None

    raw = match.group(1)
    body = text[match.end():].strip()

    if yaml is None:
        return {}, body, None

    try:
        data: dict[str, Any] = dict(yaml.safe_load(raw) or {})
    except Exception:
        data = {}

    title = data.get('title') or data.get('Title')
    if title is not None:
        title = str(title).strip() or None

    return data, body, title


# ── Wikilinks ────────────────────────────────────────────────────────


WIKILINK_RE = re.compile(r'\[\[([^\[\]]+?)(?:\|([^\[\]]*?))?\]\]')


def _resolve_wikilinks(text: str) -> tuple[str, list[str]]:
    """Replace [[wikilink|display]] with display text (or page name).

    Returns (text_with_links_resolved, list_of_link_targets).
    """
    links: list[str] = []

    def _replacer(m: re.Match) -> str:
        target = m.group(1).strip()
        display = m.group(2)
        links.append(target)
        return display.strip() if display else target

    result = WIKILINK_RE.sub(_replacer, text)
    return result, links


# ── Tags ─────────────────────────────────────────────────────────────


def _extract_body_tags(text: str) -> list[str]:
    """Extract #tags from Markdown body.

    Rules:
    - Must start with #
    - Only word chars and hyphens/underscores
    - Not inside a code block or inline code
    - Ignore markdown headings (## heading)
    """
    stripped = _strip_code_fences(text)
    # Match #tag but not ## (heading) or ### etc
    # Negative lookbehind: not preceded by # or a word character
    matches = re.findall(r'(?<![#\w])#([\w\-/]+)', stripped)
    seen: set[str] = set()
    tags: list[str] = []
    for t in matches:
        if t not in seen:
            seen.add(t)
            tags.append(t)
    return tags


def _strip_code_fences(text: str) -> str:
    """Remove fenced code blocks and inline code to avoid false tag matches."""
    # Remove fenced code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    return text


# ── Dataview inline fields (Key:: Value) ────────────────────────────


DATAVIEW_RE = re.compile(r'^([\w ]+)::\s*(.+)$', re.MULTILINE)


def _extract_dataview(text: str) -> dict[str, Any]:
    """Extract Dataview inline fields (Key:: Value)."""
    fields: dict[str, Any] = {}
    for match in DATAVIEW_RE.finditer(text):
        key = match.group(1).strip()
        value = match.group(2).strip()
        if key and value:
            fields[key] = value
    return fields


# ── Canvas (.canvas JSON) ────────────────────────────────────────────


def _parse_canvas_content(path: Path) -> tuple[str, ObsidianMetadata]:
    """Parse an Obsidian .canvas JSON file.

    Returns (aggregated_text_content, metadata_with_nodes).
    """
    try:
        data_bytes = path.read_bytes()
        data = json.loads(data_bytes.decode('utf-8-sig'))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise IngestionError(f'invalid .canvas JSON: {path.name}') from exc

    nodes = data.get('nodes', [])
    edges = data.get('edges', [])

    text_parts: list[str] = []
    node_list: list[dict[str, Any]] = []
    links: list[str] = []
    tags: list[str] = []

    for node in nodes:
        node_type = node.get('type', 'text')
        node_id = node.get('id', '')
        node_text = node.get('text', '') or ''
        node_label = node.get('label', '') or ''

        entry: dict[str, Any] = {
            'id': node_id,
            'type': node_type,
            'text': node_text,
            'label': node_label,
        }
        node_list.append(entry)

        # Collect text content
        if node_text:
            text_parts.append(node_text)

        # For file links, extract wikilink-like targets
        if node_type == 'file' and node_text:
            links.append(node_text)

        # Collect tags from file names / labels
        for src in (node_text, node_label):
            body_tags = _extract_body_tags(src)
            tags.extend(t for t in body_tags if t not in tags)

    # Edges as relationships
    edge_info = []
    for edge in edges:
        edge_info.append({
            'from': edge.get('fromNode', ''),
            'to': edge.get('toNode', ''),
            'label': edge.get('label', ''),
        })

    meta = ObsidianMetadata(
        title=path.stem,
        tags=tags,
        links=links,
        frontmatter={'canvas_node_count': len(node_list), 'edges': edge_info},
        is_canvas=True,
        canvas_nodes=node_list,
    )

    content = '\n\n'.join(text_parts) if text_parts else f'(empty canvas: {path.stem})'
    return content, meta


# ── Main file parsing ────────────────────────────────────────────────


def _read_file_bytes(path: Path) -> bytes:
    if not path.exists():
        raise IngestionError(f'file does not exist: {path.name}')
    if not path.is_file():
        raise IngestionError(f'path is not a file: {path.name}')
    if path.stat().st_size > MAX_FILE_BYTES:
        raise IngestionError(f'file too large: {path.name}')
    return path.read_bytes()


def parse_file(path: str | Path) -> tuple[str, ObsidianMetadata]:
    """Read and parse an Obsidian file.

    Supports .md/.markdown (frontmatter, wikilinks, tags, dataview)
    and .canvas (JSON node/edge graph).

    Returns (cleaned_body_text, ObsidianMetadata).
    """
    raw_path = Path(str(path))
    resolved = raw_path if raw_path.is_absolute() else Path(str(_resolve_project_path(str(path))))

    if resolved.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise IngestionError(f'unsupported Obsidian file type: {resolved.suffix}')

    # Canvas path
    if resolved.suffix.lower() == '.canvas':
        return _parse_canvas_content(resolved)

    # Markdown path
    data_bytes = _read_file_bytes(resolved)
    try:
        text = data_bytes.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise IngestionError(f'file must be valid UTF-8: {resolved.name}') from exc

    frontmatter, body, fm_title = _parse_frontmatter(text)
    body_resolved, links = _resolve_wikilinks(body)

    # Tags: from frontmatter + body
    fm_tags: list[str] = []
    raw_tags = frontmatter.get('tags', [])
    if isinstance(raw_tags, list):
        fm_tags = [str(t).strip() for t in raw_tags if isinstance(t, str)]
    elif isinstance(raw_tags, str):
        fm_tags = [t.strip() for t in raw_tags.split(',') if t.strip()]
    body_tags = _extract_body_tags(body_resolved)

    all_tags = list(dict.fromkeys(fm_tags + body_tags))  # deduplicate, preserve order

    # Aliases
    raw_aliases = frontmatter.get('aliases', [])
    if isinstance(raw_aliases, list):
        aliases = [str(a).strip() for a in raw_aliases if isinstance(a, str)]
    elif isinstance(raw_aliases, str):
        aliases = [a.strip() for a in raw_aliases.split('\n') if a.strip()]
    else:
        aliases = []

    # Dataview
    dv_fields = _extract_dataview(body_resolved)

    # Title
    title = fm_title or resolved.stem

    meta = ObsidianMetadata(
        title=title,
        tags=all_tags,
        aliases=aliases,
        links=links,
        frontmatter=frontmatter,
        dataview_fields=dv_fields,
    )

    return body_resolved.strip(), meta


# ── Public API ───────────────────────────────────────────────────────


def ingest_obsidian_file(
    path: str,
    source: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CoreObject:
    """Parse an Obsidian Markdown or Canvas file into a CoreObject.

    This is the main entry point. It extracts frontmatter, wikilinks,
    tags, dataview fields (for .md), or node/edge data (for .canvas),
    and stores everything in the CoreObject's metadata.
    """
    content, obs_meta = parse_file(path)
    quality = assess_content_quality(content, source_type='obsidian')

    resolved_path = _resolve_project_path(path)

    try:
        rel_path = str(resolved_path.relative_to(PROJECT_ROOT)).replace('\\', '/')
    except ValueError:
        rel_path = str(resolved_path)
    meta: dict[str, Any] = {
        'input_type': 'obsidian',
        'obsidian_title': obs_meta.title,
        'obsidian_tags': obs_meta.tags,
        'obsidian_aliases': obs_meta.aliases,
        'obsidian_links': obs_meta.links,
        'obsidian_is_canvas': obs_meta.is_canvas,
        'file_path': rel_path,
        'extension': resolved_path.suffix.lower(),
    }

    if obs_meta.dataview_fields:
        meta['obsidian_dataview'] = obs_meta.dataview_fields

    if obs_meta.frontmatter:
        meta['obsidian_frontmatter'] = obs_meta.frontmatter

    if obs_meta.canvas_nodes:
        meta['obsidian_canvas_nodes'] = obs_meta.canvas_nodes

    if metadata:
        meta.update(metadata)

    meta.update(quality.metadata())

    source_name = source or f'obsidian:{meta["file_path"]}'

    return CoreObject(
        object_type='document',
        content=content,
        source=source_name,
        metadata=meta,
    )
