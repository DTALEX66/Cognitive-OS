# Knowledge Integrity Spec

## Integrity Rules

- Facts and memory encodings are separate layers.
- A memory image may change without changing the source fact.
- Fact changes must be marked and reviewed before sharing.
- Route nodes require a question, answer, core fact, and source text where available.

## AI Output Rules

AI generated suggestions are candidates until the user confirms them. Confirmed assets must be written to local route storage and marked with change status.
