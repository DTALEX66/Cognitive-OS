'''Token Estimator - from CC tokenEstimation.ts (495 lines)'''
from __future__ import annotations

FILE_TOKENS_PER_BYTE = {
    '.py': 0.25, '.ts': 0.28, '.js': 0.28, '.md': 0.35, '.txt': 0.40,
    '.json': 0.30, '.yml': 0.30, '.yaml': 0.30, '.html': 0.30, '.css': 0.30,
    '.sql': 0.25, '.c': 0.25, '.h': 0.25, '.cpp': 0.25, '.java': 0.25,
    '.rs': 0.28, '.go': 0.28, '.rb': 0.28, '.sh': 0.35, '.bat': 0.35,
}
DEFAULT_BYTES_PER_TOKEN = 4.0

class TokenEstimator:
    def __init__(self):
        self._cache = {}

    def estimate(self, text: str) -> int:
        if text in self._cache: return self._cache[text]
        count = len(text.encode('utf-8')) / DEFAULT_BYTES_PER_TOKEN
        self._cache[text] = int(count)
        return int(count)

    def estimate_messages(self, messages: list[dict]) -> dict:
        total = 0
        for msg in messages:
            text = msg.get('content', msg.get('text', ''))
            total += self.estimate(text)
        return {'total_tokens': total, 'message_count': len(messages)}

    def estimate_file(self, filename: str, content: str) -> dict:
        import os
        ext = os.path.splitext(filename)[1].lower()
        ratio = FILE_TOKENS_PER_BYTE.get(ext, 0.30)
        byte_count = len(content.encode('utf-8'))
        token_count = int(byte_count * ratio)
        return {'file': filename, 'bytes': byte_count, 'estimated_tokens': token_count, 'ratio': ratio}

    def estimate_batch(self, files: dict[str, str]) -> dict:
        results = {}
        total = 0
        for name, content in files.items():
            r = self.estimate_file(name, content)
            results[name] = r
            total += r['estimated_tokens']
        return {'files': results, 'total_tokens': total, 'file_count': len(files)}
