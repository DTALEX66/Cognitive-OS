-- 014_last_reviewed_at.sql
-- Add last_reviewed_at column to cards table for a_to_b_translator.py

ALTER TABLE cards ADD COLUMN last_reviewed_at TEXT DEFAULT NULL;

CREATE INDEX IF NOT EXISTS idx_cards_last_reviewed ON cards(last_reviewed_at);
