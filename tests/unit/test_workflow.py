"""
Unit tests for workflow engine.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestWorkflowEngine:
    """Tests for workflow engine functionality."""

    def test_import_workflow_engine(self):
        """Test that workflow engine can be imported."""
        from services.workflow import WorkflowEngine
        assert WorkflowEngine is not None

    def test_workflow_engine_initialization(self):
        """Test WorkflowEngine can be initialized."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()
        assert engine is not None

    def test_create_workflow(self):
        """Test creating a new workflow."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(
            name="test_workflow",
            description="Test workflow"
        )

        assert workflow is not None
        assert workflow.name == "test_workflow"

    def test_add_step_to_workflow(self):
        """Test adding steps to workflow."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="test")

        step = engine.add_step(
            workflow,
            name="extract",
            action="ocr_extract",
            config={"max_tokens": 2048}
        )

        assert step is not None
        assert len(workflow.steps) == 1

    def test_workflow_execution(self):
        """Test workflow execution."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="test")
        engine.add_step(workflow, name="step1", action="process")

        # Mock execution
        result = engine.execute(workflow, input_data={"text": "test"})

        assert result is not None

    def test_workflow_with_conditions(self):
        """Test workflow with conditional branching."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="conditional")

        # Add conditional step
        engine.add_step(
            workflow,
            name="check",
            action="condition",
            config={"field": "confidence", "operator": "gt", "value": 0.8}
        )

        assert len(workflow.steps) == 1

    def test_workflow_serialization(self):
        """Test workflow serialization to dict."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="test")
        engine.add_step(workflow, name="step1", action="process")

        data = workflow.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == "test"
        assert "steps" in data

    def test_workflow_deserialization(self):
        """Test workflow deserialization from dict."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        data = {
            "name": "loaded_workflow",
            "steps": [
                {"name": "step1", "action": "process"}
            ]
        }

        workflow = engine.load_workflow(data)

        assert workflow.name == "loaded_workflow"

    def test_get_workflow_status(self):
        """Test getting workflow execution status."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="test")

        status = engine.get_status(workflow)

        assert status in ["pending", "running", "completed", "failed"]

    def test_cancel_workflow(self):
        """Test canceling a workflow."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="test")

        result = engine.cancel(workflow)

        assert result is True or result is False

    def test_workflow_validation(self):
        """Test workflow validation."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="test")
        engine.add_step(workflow, name="step1", action="process")

        is_valid = engine.validate(workflow)

        assert isinstance(is_valid, bool)


class TestWorkflowSteps:
    """Tests for workflow step types."""

    def test_ocr_step(self):
        """Test OCR processing step."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="ocr_workflow")
        step = engine.add_step(
            workflow,
            name="ocr",
            action="ocr_extract",
            config={"model": "nanonets-ocr-s"}
        )

        assert step.action == "ocr_extract"

    def test_transform_step(self):
        """Test data transformation step."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="transform_workflow")
        step = engine.add_step(
            workflow,
            name="transform",
            action="transform",
            config={"output_format": "json"}
        )

        assert step.action == "transform"

    def test_validate_step(self):
        """Test validation step."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="validate_workflow")
        step = engine.add_step(
            workflow,
            name="validate",
            action="validate",
            config={"schema": "invoice"}
        )

        assert step.action == "validate"

    def test_notify_step(self):
        """Test notification step."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="notify_workflow")
        step = engine.add_step(
            workflow,
            name="notify",
            action="notify",
            config={"channel": "email", "to": "user@example.com"}
        )

        assert step.action == "notify"


class TestWorkflowPipelines:
    """Tests for workflow pipelines."""

    def test_create_pipeline(self):
        """Test creating a multi-step pipeline."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="pipeline")

        engine.add_step(workflow, name="extract", action="ocr_extract")
        engine.add_step(workflow, name="parse", action="parse")
        engine.add_step(workflow, name="validate", action="validate")
        engine.add_step(workflow, name="output", action="format")

        assert len(workflow.steps) == 4

    def test_pipeline_step_order(self):
        """Test that pipeline maintains step order."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        workflow = engine.create_workflow(name="ordered")

        engine.add_step(workflow, name="first", action="a")
        engine.add_step(workflow, name="second", action="b")
        engine.add_step(workflow, name="third", action="c")

        assert workflow.steps[0].name == "first"
        assert workflow.steps[1].name == "second"
        assert workflow.steps[2].name == "third"

    def test_get_available_actions(self):
        """Test getting list of available actions."""
        from services.workflow import WorkflowEngine
        engine = WorkflowEngine()

        actions = engine.get_available_actions()

        assert isinstance(actions, list)
        assert len(actions) > 0
