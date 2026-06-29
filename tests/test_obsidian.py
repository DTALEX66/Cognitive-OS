"""Tests for Obsidian input layer — frontmatter, wikilinks, tags, canvas."""

import json
import unittest
from pathlib import Path

from app.ingestion.file import IngestionError
from app.ingestion.obsidian import (
    _extract_body_tags,
    _extract_dataview,
    _parse_frontmatter,
    _parse_canvas_content,
    _resolve_wikilinks,
    ingest_obsidian_file,
    parse_file,
)
from app.schemas import CoreObject


class ParseFrontmatterTests(unittest.TestCase):
    def test_empty_text_no_frontmatter(self):
        data, body, title = _parse_frontmatter('   ')
        self.assertEqual(data, {})
        self.assertEqual(body, '')

    def test_no_frontmatter_raw_body(self):
        data, body, title = _parse_frontmatter('# Hello\n\nSome content.')
        self.assertEqual(data, {})
        self.assertIn('Hello', body)

    def test_basic_frontmatter(self):
        text = """---
title: My Note
tags: [dev, python]
aliases:
  - My Note v2
---

# Content
"""
        data, body, title = _parse_frontmatter(text)
        self.assertEqual(title, 'My Note')
        self.assertEqual(data['tags'], ['dev', 'python'])
        self.assertEqual(data['aliases'], ['My Note v2'])
        self.assertIn('# Content', body)

    def test_frontmatter_with_dots_closing(self):
        text = """---
title: Using ...
...

Body starts here.
"""
        data, body, title = _parse_frontmatter(text)
        self.assertEqual(title, 'Using ...')
        self.assertEqual(body, 'Body starts here.')

    def test_malformed_yaml_returns_empty(self):
        text = """---
: invalid : yaml ::
---

ok body
"""
        data, body, title = _parse_frontmatter(text)
        self.assertIsInstance(data, dict)
        self.assertIn('ok body', body)


class WikilinkTests(unittest.TestCase):
    def test_basic_wikilink(self):
        result, links = _resolve_wikilinks('See [[NoteName]] for details.')
        self.assertEqual(result, 'See NoteName for details.')
        self.assertEqual(links, ['NoteName'])

    def test_wikilink_with_display(self):
        result, links = _resolve_wikilinks('See [[NoteName|display text]]')
        self.assertEqual(result, 'See display text')
        self.assertEqual(links, ['NoteName'])

    def test_multiple_wikilinks(self):
        result, links = _resolve_wikilinks('[[A]] and [[B|B-display]]')
        self.assertEqual(result, 'A and B-display')
        self.assertEqual(links, ['A', 'B'])

    def test_no_wikilinks(self):
        result, links = _resolve_wikilinks('Plain text only.')
        self.assertEqual(result, 'Plain text only.')
        self.assertEqual(links, [])


class TagExtractionTests(unittest.TestCase):
    def test_basic_tags(self):
        tags = _extract_body_tags('a #tag and another #long-tag/name')
        self.assertIn('tag', tags)
        self.assertIn('long-tag/name', tags)

    def test_ignores_headings(self):
        tags = _extract_body_tags('## Not a tag\n\nBut #tag is.')
        self.assertNotIn('Not a tag', tags)
        self.assertIn('tag', tags)

    def test_ignores_code_blocks(self):
        tags = _extract_body_tags('```\n#notatag\n```\n\n#real-tag')
        self.assertEqual(tags, ['real-tag'])

    def test_ignores_inline_code(self):
        tags = _extract_body_tags('`#notatag` and #realtag')
        self.assertEqual(tags, ['realtag'])

    def test_deduplicates_tags(self):
        tags = _extract_body_tags('#tag #tag #other')
        self.assertEqual(len(tags), 2)


class DataviewTests(unittest.TestCase):
    def test_basic_dataview(self):
        text = 'Some text\nKey:: Value\nAnother:: 42'
        fields = _extract_dataview(text)
        self.assertEqual(fields.get('Key'), 'Value')
        self.assertEqual(fields.get('Another'), '42')

    def test_no_dataview_fields(self):
        fields = _extract_dataview('Plain text with no colons.')
        self.assertEqual(fields, {})

    def test_multiline_key(self):
        text = 'Status:: Active\nPriority:: High\n'
        fields = _extract_dataview(text)
        self.assertEqual(fields.get('Status'), 'Active')
        self.assertEqual(fields.get('Priority'), 'High')


class ParseFileIntegrationTests(unittest.TestCase):
    """Tests parse_file with real fixture files."""

    def setUp(self):
        self._dir = Path(__file__).resolve().parent / 'fixtures' / 'obsidian'
        self._dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for child in self._dir.iterdir():
            child.unlink(missing_ok=True)
        self._dir.rmdir()

    def _write(self, name: str, content: str) -> Path:
        p = self._dir / name
        p.write_text(content, encoding='utf-8')
        return p

    def test_parse_basic_markdown(self):
        p = self._write('note.md', '# Hello\n\nJust a note.')
        content, meta = parse_file(str(p))
        self.assertEqual(meta.title, 'note')
        self.assertEqual(meta.tags, [])
        self.assertEqual(meta.links, [])
        self.assertIn('Hello', content)

    def test_parse_with_frontmatter_and_tags(self):
        p = self._write('note.md', """---
title: My Note
tags: [dev, obsidian]
aliases: [My Note Alias]
---

# Content with #example-tag
""")
        content, meta = parse_file(str(p))
        self.assertEqual(meta.title, 'My Note')
        self.assertIn('example-tag', meta.tags)
        self.assertIn('dev', meta.tags)
        self.assertIn('obsidian', meta.tags)
        self.assertEqual(meta.aliases, ['My Note Alias'])

    def test_parse_with_wikilinks(self):
        p = self._write('note.md', 'See [[OtherPage]] and [[Page|display named]].')
        content, meta = parse_file(str(p))
        self.assertIn('OtherPage', meta.links)
        self.assertIn('Page', meta.links)
        self.assertIn('display named', content)
        self.assertNotIn('[', content)

    def test_parse_with_dataview(self):
        p = self._write('note.md', """---
title: Dataview Note
---

Status:: Active
Priority:: High

Some content.
""")
        content, meta = parse_file(str(p))
        self.assertEqual(meta.title, 'Dataview Note')
        self.assertEqual(meta.dataview_fields.get('Status'), 'Active')
        self.assertEqual(meta.dataview_fields.get('Priority'), 'High')

    def test_rejects_unsupported_extension(self):
        p = self._write('note.pdf', 'not supported')
        with self.assertRaises(IngestionError):
            parse_file(str(p))


class CanvasParsingTests(unittest.TestCase):
    def setUp(self):
        self._dir = Path(__file__).resolve().parent / 'fixtures' / 'canvas'
        self._dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for child in self._dir.iterdir():
            child.unlink(missing_ok=True)
        self._dir.rmdir()

    def _write_canvas(self, name: str, data: dict) -> Path:
        p = self._dir / name
        p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return p

    def test_parse_basic_canvas(self):
        data = {
            "nodes": [
                {"id": "n1", "type": "text", "text": "Node one", "label": ""},
                {"id": "n2", "type": "text", "text": "Node two", "label": ""},
            ],
            "edges": [],
        }
        p = self._write_canvas('my-canvas.canvas', data)
        content, meta = parse_file(str(p))
        self.assertTrue(meta.is_canvas)
        self.assertIn('Node one', content)
        self.assertIn('Node two', content)
        self.assertEqual(len(meta.canvas_nodes or []), 2)

    def test_canvas_with_edges(self):
        data = {
            "nodes": [
                {"id": "n1", "type": "text", "text": "Root concept", "label": ""},
                {"id": "n2", "type": "text", "text": "Child concept", "label": ""},
            ],
            "edges": [
                {"fromNode": "n1", "toNode": "n2", "label": "relates to"},
            ],
        }
        p = self._write_canvas('graph.canvas', data)
        content, meta = parse_file(str(p))
        self.assertTrue(meta.is_canvas)
        self.assertIn('Root concept', content)
        self.assertIn('Child concept', content)
        edges = meta.frontmatter.get('edges', [])
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]['label'], 'relates to')

    def test_empty_canvas(self):
        p = self._write_canvas('empty.canvas', {"nodes": [], "edges": []})
        content, meta = parse_file(str(p))
        self.assertTrue(meta.is_canvas)
        self.assertIn('empty canvas', content)

    def test_invalid_canvas_raises(self):
        p = self._dir / 'bad.canvas'
        p.write_text('not json', encoding='utf-8')
        with self.assertRaises(IngestionError):
            parse_file(str(p))


class IngestObsidianFileTests(unittest.TestCase):
    """Tests the main ingest_obsidian_file function end-to-end."""

    def setUp(self):
        self._dir = Path(__file__).resolve().parent / 'fixtures' / 'obsidian_ingest'
        self._dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for child in self._dir.iterdir():
            child.unlink(missing_ok=True)
        self._dir.rmdir()

    def _write(self, name: str, content: str) -> Path:
        p = self._dir / name
        p.write_text(content, encoding='utf-8')
        return p

    def test_ingest_basic_md(self):
        p = self._write('note.md', '# Simple\n\nContent here.')
        doc = ingest_obsidian_file(str(p))
        self.assertIsInstance(doc, CoreObject)
        self.assertIn('obsidian:', doc.source)
        self.assertEqual(doc.metadata.get('obsidian_title'), 'note')
        self.assertFalse(doc.metadata.get('obsidian_is_canvas'))

    def test_ingest_with_full_metadata(self):
        p = self._write('full.md', """---
title: Full Note
tags: [tag1, tag2]
aliases: [Full Note Alias]
---

# Heading

Body with #body-tag and [[LinkedPage]].

Status:: active
""")
        doc = ingest_obsidian_file(str(p))
        self.assertEqual(doc.metadata.get('obsidian_title'), 'Full Note')
        tags = doc.metadata.get('obsidian_tags', [])
        self.assertIn('tag1', tags)
        self.assertIn('tag2', tags)
        self.assertIn('body-tag', tags)
        links = doc.metadata.get('obsidian_links', [])
        self.assertIn('LinkedPage', links)
        aliases = doc.metadata.get('obsidian_aliases', [])
        self.assertIn('Full Note Alias', aliases)
        dv = doc.metadata.get('obsidian_dataview', {})
        self.assertEqual(dv.get('Status'), 'active')

    def test_ingest_canvas(self):
        data = {
            "nodes": [
                {"id": "n1", "type": "text", "text": "Canvas node A", "label": ""},
            ],
            "edges": [],
        }
        p = self._dir / 'board.canvas'
        p.write_text(json.dumps(data), encoding='utf-8')

        doc = ingest_obsidian_file(str(p))
        self.assertTrue(doc.metadata.get('obsidian_is_canvas'))
        self.assertEqual(doc.metadata.get('obsidian_title'), 'board')
        self.assertIn('Canvas node A', doc.content)

    def test_ingest_with_quality_check(self):
        p = self._write('empty.md', '')
        doc = ingest_obsidian_file(str(p))
        self.assertIn('quality_score', doc.metadata)
        self.assertLess(doc.metadata['quality_score'], 0.5)


if __name__ == '__main__':
    unittest.main()
