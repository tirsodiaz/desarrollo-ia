---
name: ingest-movie-review
description: "Ingest an informal movie review from ClickUp into structured data in SQLite without inventing facts."
argument-hint: "Provide a ClickUp task ID or ask to pick the newest editorial input task."
agent: movie-editor
---
Read one informal ClickUp task containing a movie review request and convert it into a structured record in SQLite.

Requirements:
- Identify movie title.
- Detect year only if explicitly present or strongly supported by the text.
- Separate factual metadata from opinion text.
- Never invent missing facts.
- If year is uncertain, set it as null or mark it as uncertain in notes.

Procedure:
1. Fetch the source task from ClickUp (task ID if provided; otherwise locate a relevant pending editorial task).
2. Parse fields from free text: title, possible year, review text, optional rating, and confidence notes.
3. Inspect SQLite schema first and adapt to existing columns.
4. Insert a new record in SQLite with traceability to the ClickUp task ID.
5. Return a short confirmation including inserted fields and any uncertainty flags.

Output format:
- Source task: <id>
- Inserted movie: <title>
- Year: <value or null>
- Review text summary: <1-2 lines>
- Uncertainty: <none or details>
