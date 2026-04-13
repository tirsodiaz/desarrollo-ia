---
name: publish-movie-review
description: 'Use when you need the full movie-review pipeline: read informal ClickUp input, upsert structured SQLite data, draft an editorial article, publish back to ClickUp, and mark source as processed.'
argument-hint: 'Provide the source ClickUp task ID, or ask to process the next pending review task.'
user-invocable: true
disable-model-invocation: false
---
# Publish Movie Review

This skill orchestrates the full editorial workflow for movie reviews.

## When To Use
- A new informal movie review arrives in ClickUp.
- A team needs structured persistence in SQLite.
- A polished article must be published back to ClickUp.

## Inputs
- ClickUp source task ID (preferred), or instructions to find the next pending review task.

## Procedure
1. Read one source task from ClickUp with informal movie review text.
2. Extract title, possible year, and opinion text without inventing facts.
3. Inspect SQLite schema and identify matching movie by title.
4. Insert a new row or update the existing row with traceable changes.
5. Retrieve the structured record from SQLite after upsert.
6. Draft a concise editorial article from the structured data.
7. Publish the final article to ClickUp as a new task/comment.
8. Mark the original input item as processed when workflow rules allow it.

## Guardrails
- Do not invent missing factual values.
- Mark uncertain values explicitly.
- Keep an audit trail by referencing source task ID in outputs.
- Prefer minimal updates over broad rewrites.

## Output
- Source task ID
- Upsert action (insert or update)
- Database fields written
- Generated article text
- Published ClickUp destination (task/comment ID)
- Processing status of original item
