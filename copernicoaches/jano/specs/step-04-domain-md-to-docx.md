# Step 04 — Domain: Markdown → DOCX Converter

## Goal
Implement the pure conversion logic from a Markdown string to a DOCX document object.

## File
`jano/src/jano/domain/md_to_docx.py`

## Dependencies
- `python-docx` (`docx.Document`)
- `markdown-it-py` (parse Markdown to token tree)
- `jano.domain.models` (`ConversionResult`, `ConversionWarning`)

## Public interface

```python
def convert_md_to_docx(markdown_text: str) -> ConversionResult:
    ...
```

- Input: raw Markdown string
- Output: `ConversionResult` with `content: bytes` (DOCX file bytes) and `warnings`

## Element mapping

| Markdown element        | DOCX output                          |
|-------------------------|--------------------------------------|
| `# H1` … `###### H6`   | `Heading 1` … `Heading 6` style     |
| Plain paragraph         | `Normal` style paragraph             |
| `**bold**`              | Bold run                             |
| `*italic*`              | Italic run                           |
| `***bold+italic***`     | Bold + italic run                    |
| `[text](url)`           | Hyperlink with display text and URL  |
| `- item` / `* item`     | List paragraph (bullet style)        |
| `1. item`               | List paragraph (number style)        |
| Nested lists (indent)   | Increase list level                  |
| GFM pipe table          | DOCX table with header row           |
| `> blockquote`          | `Quote` or `Intense Quote` style     |
| ` ```code block``` `    | `Code` style paragraph (monospace)   |

## Unsupported elements (emit warning)
- Raw HTML in Markdown → warning `element_type="raw_html"`, strip tags and keep text
- Embedded images (`![alt](src)`) → warning `element_type="image"`, insert `[image: alt]` text

## Serialization
- The function must serialize the `Document` to bytes using `io.BytesIO` before returning
- No file paths or file handles are used inside this module

## Acceptance criteria
- Unit test: `# Title` produces a paragraph with `Heading 1` style
- Unit test: `**bold** and *italic*` produces correct run formatting
- Unit test: a GFM table produces a DOCX table with correct row/column count
- Unit test: a fenced code block produces a paragraph with `Code` style
- Unit test: raw HTML emits a warning with `element_type="raw_html"`
- No file I/O inside this module
