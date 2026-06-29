from app.schemas import CoreObject


def ingest(data: dict) -> CoreObject:
    """Normalize any input into CoreObject.

    First version supports text-like input. File/url/pdf can be implemented in ingestion modules.
    """
    content = str(data.get("content", "")).strip()
    source = str(data.get("source", "manual"))
    input_type = str(data.get("type", "text"))
    return CoreObject(
        object_type="document",
        content=content,
        source=source,
        metadata={"input_type": input_type},
    )
