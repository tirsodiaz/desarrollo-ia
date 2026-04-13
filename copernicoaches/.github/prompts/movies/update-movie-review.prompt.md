---
name: update-movie-review
description: "Apply corrections from ClickUp to an existing movie record in SQLite while preserving traceability."
argument-hint: "Provide the correction task ID or the movie title to update."
agent: movie-editor
---
Process a new ClickUp correction note and update the matching movie record in SQLite.

Requirements:
- Locate the correct movie row before editing.
- Update only fields justified by the incoming correction.
- Keep previous data unless the new message clearly replaces it.
- Do not overwrite confirmed facts with weaker assumptions.

Procedure:
1. Read correction content from ClickUp task/comment.
2. Resolve the target movie in SQLite by title and context clues.
3. Compare current values against requested changes.
4. Apply minimal updates (for example: year correction, review additions).
5. Return a change log showing before and after values.

Output format:
- Source task/comment: <id>
- Target movie: <title>
- Changes applied:
  - <field>: <old> -> <new>
- Skipped changes: <none or reason>
