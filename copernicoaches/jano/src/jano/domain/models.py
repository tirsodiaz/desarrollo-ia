from dataclasses import dataclass, field
from enum import Enum


class ConversionDirection(Enum):
    DOCX_TO_MD = "docx_to_md"
    MD_TO_DOCX = "md_to_docx"


@dataclass
class ConversionWarning:
    element_type: str
    description: str


@dataclass
class ConversionResult:
    content: str | bytes
    warnings: list[ConversionWarning] = field(default_factory=list)
