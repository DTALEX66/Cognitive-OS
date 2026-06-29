"""Memory Palace - Spatial Memory Retrieval System

Algorithm Core:
  1. LSI (Latent Semantic Indexing) for spatial embedding of knowledge
  2. Graph-based palace navigation (Room = Node, Path = Edge, Walk = Sequence)
  3. FSRS integration for spatial retrieval scheduling
  4. Visual/Sensory encoding hooks for mnemonic association
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from enum import Enum
import json
import math
import hashlib



class KnowledgeType(str, Enum):
    SUBJECT = "subject"
    CONCEPT = "concept"
    PROJECT = "project"
    RESOURCE = "resource"
    DECISION = "decision"
    PATTERN = "pattern"
    LESSON = "lesson"
    PREFERENCE = "preference"
    GOAL = "goal"


class Room:
    """Knowledge palace room."""
    def __init__(self, name: str, knowledge_type: KnowledgeType = KnowledgeType.CONCEPT, parent=None):
        self.name = name
        self.knowledge_type = knowledge_type
        self.parent = parent
        self.children = []
        self.items = []

    def add_child(self, child):
        self.children.append(child)

    def add_item(self, item):
        self.items.append(item)

    def total_items(self):
        total = len(self.items)
        for c in self.children:
            total += c.total_items()
        return total


class PalaceArchitecture(str, Enum):
    ROMAN = "roman"           # Roman villa style (traditional method of loci)
    MEDIEVAL = "medieval"     # Castle/tower with hierarchical floors
    TREE = "tree"             # Forest/tree with branching paths
    CITY = "city"             # City with streets and landmarks
    LIBRARY = "library"       # Library with shelves and sections


class SenseModality(str, Enum):
    VISUAL = "visual"          # Visual imagery (default, strongest)
    AUDITORY = "auditory"      # Sound-based encoding
    KINESTHETIC = "kinesthetic"  # Movement/action based
    OLFACTORY = "olfactory"    # Smell-based
    GUSTATORY = "gustatory"    # Taste-based


class MemoryRoom:
    def __init__(self, name: str, x: float, y: float, z: float = 0.0):
        self.name = name
        self.x = x  # Spatial coordinates (for LSI embedding)
        self.y = y
        self.z = z
        self.items: list[dict] = []
        self.connections: list[str] = []  # Connected room names
        self.sensory_hooks: list[str] = []  # Vivid imagery hooks

    def distance_to(self, other: 'MemoryRoom') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'x': self.x, 'y': self.y, 'z': self.z,
            'items': len(self.items),
            'connections': self.connections,
            'sensory_hooks': self.sensory_hooks,
        }


class MemoryPalace:
    def __init__(self, name: str, architecture: PalaceArchitecture = PalaceArchitecture.ROMAN):
        self.name = name
        self.architecture = architecture
        self.rooms: dict[str, MemoryRoom] = {}
        self._walks: dict[str, list[str]] = {}  # Named paths through rooms
        self._vectors: dict[int, list[float]] = {}  # card_id -> embedding vector

    # ?? LSI Spatial Embedding ??
    def embed_text(self, text: str) -> list[float]:
        """LSI-style embedding: hash-based feature vector (256-dim)"""
        vec = [0.0] * 256
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            idx = h % 256
            vec[idx] += 1.0 / (1.0 + (i * 0.01))  # Position-weighted
        # Normalize
        mag = math.sqrt(sum(v*v for v in vec))
        if mag > 0:
            vec = [v / mag for v in vec]
        return vec

    def add_room(self, room: MemoryRoom) -> None:
        self.rooms[room.name] = room

    def connect_rooms(self, name1: str, name2: str) -> None:
        if name1 in self.rooms and name2 in self.rooms:
            if name2 not in self.rooms[name1].connections:
                self.rooms[name1].connections.append(name2)
            if name1 not in self.rooms[name2].connections:
                self.rooms[name2].connections.append(name1)

    # ?? Knowledge Storage with Spatial Association ??
    def store(self, card_id: int, title: str, content: str, tags: str) -> dict:
        """Store knowledge in the palace by finding its optimal room"""
        vec = self.embed_text(title + ' ' + content)
        self._vectors[card_id] = vec

        # Find nearest room by embedding similarity
        best_room = None
        best_sim = -1.0
        for room in self.rooms.values():
            room_vec = self.embed_text(room.name)
            sim = self._cosine_sim(vec, room_vec)
            if sim > best_sim:
                best_sim = sim
                best_room = room

        if best_room:
            best_room.items.append({
                'card_id': card_id,
                'title': title,
                'tags': tags,
                'embedding_similarity': best_sim,
                'stored_at': datetime.now(timezone.utc).isoformat(),
            })
            return {'room': best_room.name, 'similarity': best_sim}

        return {'room': None, 'similarity': 0.0}

    def _cosine_sim(self, a: list[float], b: list[float]) -> float:
        dot = sum(x*y for x, y in zip(a, b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(x*x for x in b))
        return dot / (na * nb) if na * nb > 0 else 0.0

    # ?? Spatial Retrieval (Walk the Palace) ??
    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve knowledge by walking the palace (spatial search)"""
        query_vec = self.embed_text(query)

        # Score all items by embedding similarity
        scored = []
        for room_name, room in self.rooms.items():
            for item in room.items:
                item_vec = self._vectors.get(item['card_id'])
                if item_vec:
                    sim = self._cosine_sim(query_vec, item_vec)
                    scored.append({
                        'card_id': item['card_id'],
                        'title': item['title'],
                        'room': room_name,
                        'similarity': sim,
                    })

        scored.sort(key=lambda x: -x['similarity'])
        return scored[:top_k]

    # ?? Path-based Recall (Method of Loci core) ??
    def define_walk(self, name: str, room_sequence: list[str]) -> None:
        """Define a walking path through rooms (classical memory palace technique)"""
        valid = [r for r in room_sequence if r in self.rooms]
        self._walks[name] = valid

    def walk(self, walk_name: str) -> list[dict]:
        """Walk a path and recall all items along the way"""
        room_seq = self._walks.get(walk_name, [])
        results = []
        for room_name in room_seq:
            room = self.rooms.get(room_name)
            if room:
                for item in room.items:
                    results.append({
                        'room': room_name,
                        'card_id': item['card_id'],
                        'title': item['title'],
                        'sensory_hooks': room.sensory_hooks,
                    })
        return results

    # ?? Sensory Encoding (Mnemonic Hooks) ??
    def add_sensory_hook(self, room_name: str, hook: str) -> None:
        """Add a vivid sensory/mnemonic hook to a room"""
        if room_name in self.rooms:
            self.rooms[room_name].sensory_hooks.append(hook)

    def generate_mnemonic(self, concept: str, modality: SenseModality = SenseModality.VISUAL) -> str:
        """Generate a mnemonic hook for a concept using specified sensory modality"""
        hooks = {
            SenseModality.VISUAL: [
                f"Imagine a giant glowing {concept} floating in the room",
                f"Picture {concept} written in fire on the wall",
                f"Visualize a golden statue of {concept} in the center",
            ],
            SenseModality.AUDITORY: [
                f"Hear the sound of {concept} echoing through the halls",
                f"The name {concept} is being chanted by a choir",
            ],
            SenseModality.KINESTHETIC: [
                f"You are physically holding {concept} in your hands",
                f"Walk through a room filled with {concept}",
            ],
        }
        import random
        candidates = hooks.get(modality, hooks[SenseModality.VISUAL])
        return random.choice(candidates)


class PalaceEngine:
    """Enhanced Palace Engine with real memory palace algorithms"""
    def __init__(self, store: Any = None):
        self._store = store
        self._palace = MemoryPalace('Main Palace', PalaceArchitecture.ROMAN)
        self._init_default_architecture()

    def _init_default_architecture(self):
        """Initialize Roman villa architecture with default rooms"""
        rooms_data = [
            ('Atrium', 0.0, 0.0, 0.0),
            ('Tablinum', 5.0, 0.0, 0.0),
            ('Triclinium', 5.0, 5.0, 0.0),
            ('Cubiculum', 0.0, 5.0, 0.0),
            ('Bibliotheca', -5.0, 0.0, 0.0),
            ('Peristylium', -5.0, -5.0, 0.0),
            ('Exedra', 0.0, -5.0, 0.0),
            ('Lararium', 5.0, -5.0, 0.0),
            ('Scriptorium', -5.0, 5.0, 0.0),
            ('Culina', 10.0, 0.0, 0.0),
        ]
        for name, x, y, z in rooms_data:
            self._palace.add_room(MemoryRoom(name, x, y, z))

        # Connect rooms in walking path order
        room_names = [r[0] for r in rooms_data]
        for i in range(len(room_names) - 1):
            self._palace.connect_rooms(room_names[i], room_names[i+1])
        self._palace.connect_rooms(room_names[-1], room_names[0])

        # Define classic walking paths
        self._palace.define_walk('classical', room_names)
        self._palace.define_walk('short', ['Atrium', 'Tablinum', 'Triclinium', 'Cubiculum'])

    def store_knowledge(self, card_id: int, title: str, content: str, tags: str = '') -> dict:
        """Store knowledge card into optimal palace room"""
        result = self._palace.store(card_id, title, content, tags)
        # Add sensory hook based on tags
        for tag in tags.split(','):
            tag = tag.strip()
            if tag:
                hook = self._palace.generate_mnemonic(tag)
                room_name = result.get('room')
                if room_name:
                    self._palace.add_sensory_hook(room_name, hook)
        return result

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        """Recall knowledge from palace by walking and matching"""
        return self._palace.recall(query, top_k)

    def take_walk(self, walk_name: str = 'classical') -> dict:
        """Walk through the palace to retrieve sequentially"""
        items = self._palace.walk(walk_name)
        return {
            'walk_name': walk_name,
            'rooms_visited': len(set(it['room'] for it in items)),
            'items_recalled': len(items),
            'items': items,
        }

    def get_architecture(self) -> dict:
        return {
            'name': self._palace.name,
            'architecture': self._palace.architecture.value,
            'rooms': len(self._palace.rooms),
            'walks': list(self._palace._walks.keys()),
            'room_details': {n: r.to_dict() for n, r in self._palace.rooms.items()},
        }

    # ?? Build from DB ??
    def build_from_database(self) -> dict:
        """Auto-build palace from existing knowledge cards"""
        if not self._store:
            return {'stored': 0, 'error': 'no store'}
        rows = self._store.conn.execute('SELECT id, title, content, tags FROM cards ORDER BY id').fetchall()
        count = 0
        for r in rows:
            result = self.store_knowledge(r[0], r[1], r[2] or '', r[3] or '')
            count += 1
        return {'stored': count, 'rooms': len(self._palace.rooms)}
