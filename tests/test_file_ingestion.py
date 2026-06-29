import unittest
from pathlib import Path

from app.ingestion.file import IngestionError, ingest_file


class FileIngestionTests(unittest.TestCase):
    def test_rejects_invalid_utf8_without_silent_byte_loss(self):
        path = Path('data') / 'output' / 'invalid_utf8_fixture.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'valid prefix \xff invalid byte')

        try:
            with self.assertRaises(IngestionError):
                ingest_file(str(path))
        finally:
            path.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
