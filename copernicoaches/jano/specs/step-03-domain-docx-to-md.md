# Step 03 — Domain: DOCX → Markdown Converter

## Goal
Implement the pure conversion logic from a DOCX document object to a Markdown string.

## File
`jano/src/jano/domain/docx_to_md.py`

## Dependencies
- `python-docx` (`docx.Document`)
- `jano.domain.models` (`ConversionResult`, `ConversionWarning`)

## Public interface

```python
def convert_docx_to_md(document: Document) -> ConversionResult:
    ...
```

- Input: a `python-docx` `Document` object (already loaded, no file I/O here)
- Output: `ConversionResult` with `content: str` (Markdown text) and `warnings`

## Element mapping

| DOCX element          | Markdown output                        |
|-----------------------|----------------------------------------|
| Heading 1–6           | `#` … `######` prefix                 |
| Normal paragraph      | Plain text paragraph (blank line sep.) |
| Bold run              | `**text**`                             |
| Italic run            | `*text*`                               |
| Bold+italic run       | `***text***`                           |
| Hyperlink             | `[text](url)`                          |
| Bulleted list (lvl 0) | `- item`                               |
| Numbered list (lvl 0) | `1. item`                              |
| Nested lists (lvl 1+) | Indent with 2 spaces per level         |
| Table                 | GFM pipe table                         |
| Block quote           | `> text` (detect via style name)       |
| Code block            | ` ```text``` ` fenced block            |

## Unsupported elements (emit warning, preserve text)
- Images → warning `element_type="image"`, text fallback `[image]`
- Complex table borders/shading → warning, render content only
- Custom styles not matching known names → warning, render as paragraph

## Acceptance criteria
- Unit test: heading levels 1–3 produce correct `#` prefixes
- Unit test: bold/italic inline formatting is wrapped correctly
- Unit test: a simple table produces valid GFM
- Unit test: an image paragraph produces a warning with `element_type="image"`
- No file I/O inside this module
