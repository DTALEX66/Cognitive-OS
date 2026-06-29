from fastapi import FastAPI, HTTPException

from app.api.ingest import ingest
from app.core.router import route
from app.rag.retriever import retrieve
from app.core.compiler import compile_task
from app.agent.executor import execute
from app.memory.store import list_lessons, save_lesson, save_memory, search_memory
from app.core.trace import log_trace, list_traces
from app.evaluation.evaluator import evaluate
from app.evaluation.feedback import compile_lesson
from app.ingestion.file import IngestionError, ingest_directory, ingest_file
from app.learning.cards import (
    create_card,
    create_card_from_document,
    due_cards,
    list_cards,
    list_review_events,
    review_learning_card,
)
from app.tools.registry import list_tools

app = FastAPI(title='Cognitive OS v2', version='0.2.0')


@app.get('/health')
def health():
    return {'status': 'ok', 'system': 'cognitive-os-v2'}


@app.get('/tools')
def tools():
    return {'items': list_tools()}


@app.post('/ingest')
def ingest_api(input_data: dict):
    doc = ingest(input_data)
    save_memory(doc)
    return doc


@app.post('/ingest/file')
def ingest_file_api(payload: dict):
    try:
        doc = ingest_file(
            str(payload.get('path', '')),
            source=payload.get('source'),
            metadata=payload.get('metadata'),
        )
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    decision = route(doc)
    doc.attention_score = decision.score
    doc.route = decision.route
    if decision.route != 'DROP':
        save_memory(doc)
    return {'document': doc, 'route': decision}


@app.post('/ingest/directory')
def ingest_directory_api(payload: dict):
    try:
        docs = ingest_directory(
            str(payload.get('path', '')),
            pattern=str(payload.get('pattern', '*.md')),
            limit=int(payload.get('limit', 50)),
            source=payload.get('source'),
            metadata=payload.get('metadata'),
        )
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    items = []
    for doc in docs:
        decision = route(doc)
        doc.attention_score = decision.score
        doc.route = decision.route
        if decision.route != 'DROP':
            save_memory(doc)
        items.append({'document': doc, 'route': decision})

    return {'count': len(items), 'items': items}


@app.post('/route')
def route_api(input_data: dict):
    doc = ingest(input_data)
    return route(doc)


@app.post('/run')
def run(input_data: dict):
    doc = ingest(input_data)
    decision = route(doc)
    doc.attention_score = decision.score
    doc.route = decision.route

    if decision.route == 'DROP':
        return {'status': 'ignored', 'document': doc, 'route': decision}

    if decision.route == 'REVIEW':
        save_memory(doc)
        return {'status': 'needs_review', 'document': doc, 'route': decision}

    save_memory(doc)
    context = retrieve(doc.content)
    task = compile_task(context)
    trace = execute(task)
    log_trace(trace)
    eval_result = evaluate(trace)
    lesson = compile_lesson(eval_result, trace)
    save_lesson(lesson)

    return {
        'status': 'done',
        'document': doc,
        'route': decision,
        'context': context,
        'task': task,
        'trace': trace,
        'eval': eval_result,
        'lesson': lesson,
    }


@app.post('/memory/search')
def memory_search(payload: dict):
    query = str(payload.get('query', ''))
    top_k = int(payload.get('top_k', 5))
    return {'query': query, 'items': search_memory(query, top_k=top_k)}


@app.get('/traces')
def traces():
    return {'items': list_traces()}


@app.get('/memory/lessons')
def lessons():
    return {'items': list_lessons()}


@app.post('/learning/cards')
def learning_cards_create(payload: dict):
    metadata = payload.get('metadata')
    if not isinstance(metadata, dict):
        metadata = {}

    front = str(payload.get('front', '')).strip()
    back = str(payload.get('back', '')).strip()
    content = str(payload.get('content', '')).strip()

    if front and back:
        card = create_card(
            front,
            back,
            source=str(payload.get('source', 'manual')),
            source_object_id=payload.get('source_object_id'),
            metadata=metadata,
        )
        return {'card': card}

    doc = ingest({'content': content or back or front, 'source': payload.get('source', 'manual'), 'metadata': metadata})
    decision = route(doc)
    doc.attention_score = decision.score
    doc.route = decision.route
    if decision.route == 'DROP':
        raise HTTPException(status_code=400, detail='content is too low-value to create a learning card')
    card = create_card_from_document(doc, front=front or None, back=back or None)
    return {'card': card, 'route': decision}


@app.get('/learning/cards')
def learning_cards_list():
    return {'items': list_cards()}


@app.post('/learning/review')
def learning_review(payload: dict):
    card_id = str(payload.get('card_id', ''))
    if not card_id:
        raise HTTPException(status_code=400, detail='card_id is required')
    try:
        score = float(payload.get('score', 0.0))
        card, event = review_learning_card(card_id, score)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {'card': card, 'event': event}


@app.get('/learning/due')
def learning_due():
    return {'items': due_cards()}


@app.get('/learning/reviews')
def learning_reviews():
    return {'items': list_review_events()}
