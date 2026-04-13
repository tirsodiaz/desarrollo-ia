from datetime import UTC
from pathlib import Path

from app.pipeline.contracts import PipelineEnvelope, PipelineStatus
from app.pipeline.engine import PipelineEngine, build_pipeline
from app.pipeline.stages import BaseStage


def test_engine_runs_all_stages() -> None:
    execution_order: list[str] = []

    class TrackingStage:
        def __init__(self, label: str):
            self.name = label

        def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
            execution_order.append(self.name)
            return envelope

    engine = PipelineEngine([TrackingStage("a"), TrackingStage("b"), TrackingStage("c")])
    envelope = PipelineEnvelope(source_file=Path("test.json"))

    result = engine.run(envelope)

    assert execution_order == ["a", "b", "c"]
    assert result.status == PipelineStatus.SUCCESS
    assert result.detected_at.tzinfo is UTC
    assert result.started_at is not None
    assert result.started_at.tzinfo is UTC
    assert result.completed_at is not None
    assert result.completed_at.tzinfo is UTC


def test_engine_stops_on_error() -> None:
    execution_order: list[str] = []

    class FailingStage:
        name = "failing"

        def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
            envelope.status = PipelineStatus.ERROR
            envelope.failed_stage = "failing"
            envelope.error_message = "something broke"
            return envelope

    class NeverRunStage:
        name = "never"

        def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
            execution_order.append("never")
            return envelope

    engine = PipelineEngine([FailingStage(), NeverRunStage()])

    result = engine.run(PipelineEnvelope(source_file=Path("test.json")))

    assert result.status == PipelineStatus.ERROR
    assert result.failed_stage == "failing"
    assert "never" not in execution_order


def test_correlation_id_preserved() -> None:
    class EchoStage:
        name = "echo"

        def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
            return envelope

    engine = PipelineEngine([EchoStage()])
    envelope = PipelineEnvelope(source_file=Path("f.json"))
    original_id = envelope.correlation_id

    result = engine.run(envelope)

    assert result.correlation_id == original_id


def test_unique_correlation_ids() -> None:
    ids = {PipelineEnvelope(source_file=Path("f.json")).correlation_id for _ in range(100)}

    assert len(ids) == 100


def test_envelope_detected_at_is_utc() -> None:
    envelope = PipelineEnvelope(source_file=Path("f.json"))

    assert envelope.detected_at.tzinfo is UTC


def test_stub_pipeline() -> None:
    engine = build_pipeline()
    envelope = PipelineEnvelope(source_file=Path("test.json"))

    result = engine.run(envelope)

    assert result.status == PipelineStatus.SUCCESS


def test_base_stage_fail_sets_all_error_fields_correctly() -> None:
    class ConcreteStage(BaseStage):
        name = "test_stage"

    stage = ConcreteStage()
    envelope = PipelineEnvelope(source_file=Path("f.json"))

    result = stage._fail(envelope, code="ERR001", message="test error")

    assert result.status == PipelineStatus.ERROR
    assert result.failed_stage == "test_stage"
    assert result.error_code == "ERR001"
    assert result.error_message == "test error"
