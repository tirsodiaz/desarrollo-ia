---
name: draft-article
description: "Draft an editorial-style movie review article from structured SQLite data without altering stored facts."
argument-hint: "Provide a movie title or database ID to draft from."
agent: movie-editor
---
Generate an editorial review draft from a structured SQLite movie entry.

Requirements:
- Use SQLite as the factual source of truth.
- Keep facts unchanged (title, year, director, rating, language, runtime).
- Clearly separate factual context from opinionated prose.
- Do not write back to SQLite in this command.

Procedure:
1. Retrieve the requested movie record from SQLite.
2. Summarize factual metadata in a concise header.
3. Write a polished editorial draft (short intro, analysis paragraph, conclusion).
4. Add a final "Fact check" section listing fields used.

Output format:
- Headline
- Deck (1 sentence)
- Body (3-5 short paragraphs)
- Fact check bullets
