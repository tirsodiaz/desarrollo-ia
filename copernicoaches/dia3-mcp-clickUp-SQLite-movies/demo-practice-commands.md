# Demo - Practice Commands (Copilot + ClickUp + SQLite)

This document is a runnable demo for the exercise implemented in this workspace.

## Goal

Demonstrate the progression:
1. Prompt command (single task)
2. Custom agent (specialized behavior)
3. Skill (full workflow)

## Copilot Customizations Included

Workspace files already created:
- `.github/prompts/ingest-movie-review.prompt.md`
- `.github/prompts/update-movie-review.prompt.md`
- `.github/prompts/draft-article.prompt.md`
- `.github/agents/movie-editor.agent.md`
- `.github/skills/publish-movie-review/SKILL.md`

## Preconditions

- ClickUp MCP server is configured in `.vscode/mcp.json`
- SQLite MCP server is available and connected
- Database file exists at `dia3/movies.db`
- At least one informal movie-review task exists in ClickUp

## Part A - Prompt Commands

Run these commands in Copilot Chat using `/`.

### 1) Ingest review into SQLite

Command:

```text
/ingest-movie-review 869xxxxxx
```

Expected result:
- Reads one informal ClickUp task
- Extracts movie data without inventing facts
- Inserts structured row into SQLite
- Returns uncertainty flags when needed

### 2) Update an existing movie review

Command:

```text
/update-movie-review 869xxxxxx
```

Expected result:
- Locates existing movie in SQLite
- Applies only justified corrections
- Returns before -> after change log

### 3) Draft editorial article

Command:

```text
/draft-article Blade Runner
```

Expected result:
- Reads structured data from SQLite
- Produces editorial draft text
- Does not modify database

## Part B - Custom Agent

Agent name: `movie-editor`

How to use:
1. Open agent picker in Copilot Chat
2. Select `movie-editor`
3. Re-run `/draft-article` or other command

What should improve:
- Better fact/opinion separation
- Clear uncertainty handling
- More consistent editorial tone

## Part C - Skill (Full Pipeline)

Skill command:

```text
/publish-movie-review 869xxxxxx
```

Expected end-to-end flow:
1. Read informal input from ClickUp
2. Upsert structured data in SQLite
3. Retrieve final structured record
4. Generate editorial article
5. Publish result back to ClickUp
6. Mark source as processed (if applicable)

## Suggested Demo Script (10 minutes)

1. Show an informal ClickUp task (messy input)
2. Run `/ingest-movie-review`
3. Show record created/updated in SQLite
4. Run `/draft-article` and read output
5. Switch to `movie-editor` agent and run again
6. Compare baseline vs specialized output
7. Run `/publish-movie-review` to complete pipeline

## Evaluation Checklist

- No invented factual data
- Uncertainty explicitly marked
- Traceability to source task ID
- Minimal and justified DB updates
- Editorial output coherent and publishable

## Example Inputs for Class

Use intentionally imperfect tasks like:
- "Nueva peli: Alien. Muy tensa. Creo que del 79. Hacer review."
- "Corregir Blade Runner: no era 1981, era 1982."
- "The Thing, atmosfera increible, nota 5/5, revisar anio."

## Common Pitfalls

- Updating fields without enough evidence
- Mixing opinion and facts in the same DB field
- Forgetting to keep source task traceability
- Drafting article from memory instead of SQLite
