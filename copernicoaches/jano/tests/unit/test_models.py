from jano.domain.models import ConversionDirection, ConversionResult, ConversionWarning


def test_conversion_warning_fields():
    w = ConversionWarning(element_type="image", description="no image support")
    assert w.element_type == "image"
    assert w.description == "no image support"


def test_conversion_result_defaults():
    r = ConversionResult(content="hello")
    assert r.content == "hello"
    assert r.warnings == []


def test_conversion_result_with_warnings():
    w = ConversionWarning("image", "lost")
    r = ConversionResult(content=b"bytes", warnings=[w])
    assert len(r.warnings) == 1
    assert r.warnings[0].element_type == "image"


def test_direction_enum():
    assert ConversionDirection.DOCX_TO_MD.value == "docx_to_md"
    assert ConversionDirection.MD_TO_DOCX.value == "md_to_docx"
