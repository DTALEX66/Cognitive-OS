from app.schemas import ContextPack
from app.memory.store import search_memory
from app.rag.context_engine import build_context_pack


def retrieve(query: str, top_k: int = 5) -> ContextPack:
    items = search_memory(query, top_k=top_k)
    return build_context_pack(query=query, items=items, top_k=top_k)
