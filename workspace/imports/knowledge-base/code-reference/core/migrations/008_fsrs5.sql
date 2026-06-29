-- Migration 008: FSRS-5 columns for cards table
-- Adds difficulty, lapses, last_review_at for FSRS-5 algorithm

ALTER TABLE cards ADD COLUMN difficulty REAL DEFAULT 5.0;
ALTER TABLE cards ADD COLUMN lapses INTEGER DEFAULT 0;
ALTER TABLE cards ADD COLUMN last_review_at TEXT;
