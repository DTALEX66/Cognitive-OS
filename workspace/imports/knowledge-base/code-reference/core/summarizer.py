# Local extractive summarizer for A-Line ingest
def local_extractive_summary(text, max_sentences=5):
    sentences = text.replace(chr(10), ' ').split('.')
    return '. '.join(s.strip() for s in sentences[:max_sentences] if s.strip())
