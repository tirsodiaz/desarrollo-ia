# SPEC-01 — Overview

## Project

**Atrium** is a console file manager using Miller Columns, built with Rust and crossterm.

## Purpose

Provide structured, context-preserving navigation of the local filesystem in a terminal environment. The Miller Columns model keeps three levels visible simultaneously, eliminating blind navigation.

## User stories

| ID  | Story |
|-----|-------|
| HU1 | As a user, I want to navigate the filesystem clearly so I always know where I am. |
| HU2 | As a user, I want to see the parent, current, and next level at once to keep context. |
| HU3 | As a user, I want full keyboard navigation with minimal friction. |
| HU4 | As a user, I want to see the contents of a directory before entering it. |
| HU5 | As a user, I want to understand the hierarchy without building it mentally. |

## Scope (MVP)

**In scope:**
- Keyboard navigation
- Three-column structured display with Unicode box-drawing and emoji indicators
- Dynamic content update on navigation
- Local filesystem representation

**Out of scope:**
- File operations (copy, move, delete)
- Mouse support
- Multiple simultaneous panels
- Advanced rendering (images, PDFs)
- External system integration
- Configurable or dynamic layouts

## Fundamental principle

> The center column defines where the user is, the left column shows where they came from, and the right column shows where they can go.

## Stack

- Rust (stable)
- [crossterm](https://github.com/crossterm-rs/crossterm) for raw terminal control, keyboard input, and ANSI color
- No GUI or TUI framework dependencies
