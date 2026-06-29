def embed(text: str) -> list[float]:
    return [float((sum(map(ord, text)) % 997) / 997)]
