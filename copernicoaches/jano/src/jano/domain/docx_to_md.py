from __future__ import annotations

from docx import Document
from docx.oxml.ns import qn

from jano.domain.models import ConversionResult, ConversionWarning

# DOCX paragraph style names that map to Markdown headings
_HEADING_STYLES = {
    "heading 1": 1,
    "heading 2": 2,
    "heading 3": 3,
    "heading 4": 4,
    "heading 5": 5,
    "heading 6": 6,
}

# Style names treated as block-quote
_QUOTE_STYLES = {"quote", "intense quote", "block text"}

# Style names treated as code block
_CODE_STYLES = {"code", "code block", "html code", "macro text"}

# List style name fragments
_BULLET_STYLE_FRAGMENTS = {"list bullet", "list paragraph"}
_NUMBER_STYLE_FRAGMENTS = {"list number"}


def _style_name(paragraph) -> str:
    return (paragraph.style.name or "").lower()


def _run_text(run) -> str:
    """Return run text with inline Markdown formatting applied."""
    text = run.text
    if not text:
        return ""
    bold = run.bold
    italic = run.italic
    if bold and italic:
        return f"***{text}***"
    if bold:
        return f"**{text}**"
    if italic:
        return f"*{text}*"
    return text


def _paragraph_inline(paragraph) -> str:
    """Collect all runs plus hyperlinks into an inline Markdown string."""
    parts: list[str] = []
    for child in paragraph._p:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "r":
            # Iterate runs of the paragraph to find matching element
            for run in paragraph.runs:
                if run._r is child:
                    parts.append(_run_text(run))
                    break
        elif tag == "hyperlink":
            # Extract relationship ID and display text
            rel_id = child.get(qn("r:id"))
            display = "".join(r.text or "" for r in child.findall(f".//{qn('w:t')}"))
            bold = any(
                r.find(qn("w:b")) is not None for r in child.findall(f".//{qn('w:r')}")
            )
            italic = any(
                r.find(qn("w:i")) is not None for r in child.findall(f".//{qn('w:r')}")
            )
            if rel_id and paragraph.part.rels.get(rel_id):
                url = paragraph.part.rels[rel_id].target_ref
                if bold and italic:
                    display = f"***{display}***"
                elif bold:
                    display = f"**{display}**"
                elif italic:
                    display = f"*{display}*"
                parts.append(f"[{display}]({url})")
            else:
                parts.append(display)
    return "".join(parts)


def _has_image(paragraph) -> bool:
    return bool(paragraph._p.findall(f".//{qn('a:blip')}"))


def _list_level(paragraph) -> int:
    """Return 0-based nesting level for list paragraphs."""
    ilvl = paragraph._p.find(f".//{qn('w:ilvl')}")
    if ilvl is not None:
        val = ilvl.get(qn("w:val"))
        if val is not None:
            return int(val)
    return 0


def _is_numbered(paragraph) -> bool:
    style = _style_name(paragraph)
    if any(f in style for f in _NUMBER_STYLE_FRAGMENTS):
        return True
    # Check numFmt via numPr
    numPr = paragraph._p.find(f".//{qn('w:numPr')}")
    if numPr is not None:
        numId_elem = numPr.find(qn("w:numId"))
        if numId_elem is not None:
            num_id = numId_elem.get(qn("w:val"), "0")
            if num_id != "0":
                # Try to look up numFmt
                try:
                    numbering = (
                        paragraph.part.numbering_part.numbering_definitions._numbering
                    )
                    for num in numbering.findall(qn("w:num")):
                        if num.get(qn("w:numId")) == num_id:
                            abstract_id = num.find(qn("w:abstractNumId")).get(
                                qn("w:val")
                            )
                            for abstract in numbering.findall(qn("w:abstractNum")):
                                if abstract.get(qn("w:abstractNumId")) == abstract_id:
                                    lvl = _list_level(paragraph)
                                    for lvl_elem in abstract.findall(qn("w:lvl")):
                                        if lvl_elem.get(qn("w:ilvl")) == str(lvl):
                                            fmt = lvl_elem.find(qn("w:numFmt"))
                                            if fmt is not None:
                                                val = fmt.get(qn("w:val"), "")
                                                return val not in (
                                                    "bullet",
                                                    "none",
                                                )
                except Exception:
                    pass
    return False


def _is_list_paragraph(paragraph) -> bool:
    style = _style_name(paragraph)
    return (
        any(f in style for f in _BULLET_STYLE_FRAGMENTS)
        or any(f in style for f in _NUMBER_STYLE_FRAGMENTS)
        or paragraph._p.find(f".//{qn('w:numPr')}") is not None
    )


def _table_to_md(table) -> str:
    rows = table.rows
    if not rows:
        return ""
    lines: list[str] = []
    for i, row in enumerate(rows):
        cells = [cell.text.replace("\n", " ").strip() for cell in row.cells]
        lines.append("| " + " | ".join(cells) + " |")
        if i == 0:
            lines.append("| " + " | ".join("---" for _ in cells) + " |")
    return "\n".join(lines)


def convert_docx_to_md(document: Document) -> ConversionResult:
    warnings: list[ConversionWarning] = []
    blocks: list[str] = []

    body_children = list(document.element.body)

    # Track numbered list counters per level
    numbered_counters: dict[int, int] = {}

    for child in body_children:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag == "tbl":
            # Find corresponding Table object
            for table in document.tables:
                if table._tbl is child:
                    blocks.append(_table_to_md(table))
                    numbered_counters.clear()
                    break
            continue

        if tag != "p":
            continue

        # Find matching paragraph object
        paragraph = None
        for p in document.paragraphs:
            if p._p is child:
                paragraph = p
                break
        if paragraph is None:
            continue

        style = _style_name(paragraph)

        # Image check
        if _has_image(paragraph):
            warnings.append(
                ConversionWarning(
                    element_type="image",
                    description=(
                        "Image element cannot be converted to Markdown;"
                        " replaced with [image]."
                    ),
                )
            )
            blocks.append("[image]")
            continue

        # Heading
        if style in _HEADING_STYLES:
            level = _HEADING_STYLES[style]
            text = paragraph.text.strip()
            if text:
                blocks.append(f"{'#' * level} {text}")
            numbered_counters.clear()
            continue

        # Quote / blockquote
        if style in _QUOTE_STYLES:
            inline = _paragraph_inline(paragraph).strip()
            if inline:
                blocks.append(f"> {inline}")
            continue

        # Code block
        if style in _CODE_STYLES:
            blocks.append(f"```\n{paragraph.text}\n```")
            continue

        # List
        if _is_list_paragraph(paragraph):
            level = _list_level(paragraph)
            indent = "  " * level
            inline = _paragraph_inline(paragraph).strip()
            if _is_numbered(paragraph):
                numbered_counters[level] = numbered_counters.get(level, 0) + 1
                # Reset deeper levels
                for k in list(numbered_counters.keys()):
                    if k > level:
                        del numbered_counters[k]
                blocks.append(f"{indent}{numbered_counters[level]}. {inline}")
            else:
                numbered_counters.clear()
                blocks.append(f"{indent}- {inline}")
            continue

        # Horizontal rule (empty paragraph with border or "---" style)
        if style in {"horizontal line", "line"}:
            blocks.append("---")
            continue

        # Normal paragraph
        numbered_counters.clear()
        inline = _paragraph_inline(paragraph).strip()
        if inline:
            blocks.append(inline)

    return ConversionResult(content="\n\n".join(blocks) + "\n", warnings=warnings)
