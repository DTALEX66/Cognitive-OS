import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {'.py', '.md', '.yaml', '.yml', '.toml', '.json', '.txt'}
TEXT_FILENAMES = {'.gitignore'}
SKIP_DIRS = {
    '.git',
    '.venv',
    '.agents',
    '.codex',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
}
SKIP_PREFIXES = (
    'data/',
    'workspace/imports/',
    'workspace/local-imports/',
)

MOJIBAKE_MARKERS = (
    '\ufeff',
    '\ufffd',
    '\u00c3',
    '\u00c2',
    '\u00e2\u20ac',
    '\u00ef\u00bb\u00bf',
    '\u935a\u5ea3\u753b',
    '\u6d60\u8bf2\u59df',
    '\u93c7\u5b58\u67ca',
    '\u93c1\u7248\u5d41',
    '\u93c2\u56e6\u6b22',
)


def iter_project_text_files():
    for path in PROJECT_ROOT.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(PROJECT_ROOT)
        rel_text = relative.as_posix()
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if rel_text.startswith(SKIP_PREFIXES):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_FILENAMES:
            continue
        yield path


class EncodingPolicyTests(unittest.TestCase):
    def test_project_text_files_are_utf8_without_mojibake_markers(self):
        failures = []

        for path in iter_project_text_files():
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            data = path.read_bytes()
            if data.startswith(b'\xef\xbb\xbf'):
                failures.append(f'{relative}: unexpected UTF-8 BOM')

            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError as exc:
                failures.append(f'{relative}: invalid UTF-8 at byte {exc.start}')
                continue

            for marker in MOJIBAKE_MARKERS:
                if marker in text:
                    escaped = marker.encode('unicode_escape').decode('ascii')
                    failures.append(f'{relative}: contains mojibake marker {escaped}')
                    break

        self.assertEqual(failures, [])


if __name__ == '__main__':
    unittest.main()
