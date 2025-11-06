"""
Unified Workflow for Swine Farm AI Assistant
Routes user queries to either text analysis or chart visualization workflows
"""
from pydantic import BaseModel
from chart_agents import detect_chart_intent
from workflow_chart import run_chart_workflow, ChartWorkflowInput
from typing import Optional
import os


# Import the original text workflow
try:
    from workflow import run_workflow as run_text_workflow, WorkflowInput
except ImportError:
    # Fallback if workflow.py is not in the same directory
    import sys
    sys.path.insert(0, '/tmp/swine_alert-main/agentkit_python/')
    from workflow import run_workflow as run_text_workflow, WorkflowInput


class UnifiedWorkflowInput(BaseModel):
    input_as_text: str
    force_chart: bool = False  # Force chart workflow even if not detected
    force_text: bool = False   # Force text workflow even if chart detected
    use_mcp_server: bool = False
    mcp_server_url: Optional[str] = None
    use_local_db: bool = False  # Use local SQLite instead of Snowflake


def run_unified_workflow(workflow_input: UnifiedWorkflowInput):
    """
    Main entry point for processing user queries

    This function:
    1. Detects user intent (chart vs text)
    2. Routes to appropriate workflow
    3. Returns results with workflow metadata

    Args:
        workflow_input: UnifiedWorkflowInput with user query and options

    Returns:
        dict with workflow results and metadata
    """
    user_input = workflow_input.input_as_text

    # Check for forced routing
    if workflow_input.force_chart:
        print("🎨 Forcing chart workflow...")
        intent = "chart"
        confidence = 1.0
    elif workflow_input.force_text:
        print("📝 Forcing text workflow...")
        intent = "text"
        confidence = 1.0
    else:
        # Agent 1: Detect intent
        print("🔍 Step 1: Detecting user intent (chart vs text)...")
        try:
            chart_intent = detect_chart_intent(user_input)
            intent = chart_intent.intent
            confidence = chart_intent.confidence

            print(f"Intent: {intent} (confidence: {confidence:.2%})")
            print(f"Reasoning: {chart_intent.reasoning}")

        except Exception as e:
            print(f"⚠️ Intent detection failed: {e}, defaulting to text workflow")
            intent = "text"
            confidence = 0.5

    # Route to appropriate workflow
    if intent == "chart":
        print("📊 Routing to CHART workflow...")

        # Try to import local version if use_local_db is True
        if workflow_input.use_local_db:
            try:
                from workflow_chart_local import run_chart_workflow as run_chart_local, ChartWorkflowInput as LocalInput
                chart_input = LocalInput(
                    input_as_text=user_input,
                    use_mcp_server=workflow_input.use_mcp_server,
                    mcp_server_url=workflow_input.mcp_server_url,
                    use_local_db=True
                )
                result = run_chart_local(chart_input)
            except Exception as e:
                print(f"⚠️ Local SQLite mode failed: {e}, falling back to Snowflake")
                chart_input = ChartWorkflowInput(
                    input_as_text=user_input,
                    use_mcp_server=workflow_input.use_mcp_server,
                    mcp_server_url=workflow_input.mcp_server_url
                )
                result = run_chart_workflow(chart_input)
        else:
            chart_input = ChartWorkflowInput(
                input_as_text=user_input,
                use_mcp_server=workflow_input.use_mcp_server,
                mcp_server_url=workflow_input.mcp_server_url
            )
            result = run_chart_workflow(chart_input)

        result["intent_confidence"] = confidence

    else:
        print("📝 Routing to TEXT workflow...")
        text_input = WorkflowInput(input_as_text=user_input)
        result = run_text_workflow(text_input)
        result["workflow_type"] = "text"
        result["intent_confidence"] = confidence

    return result


# Backward compatibility: allow direct import of run_workflow
def run_workflow(workflow_input):
    """
    Backward-compatible function that wraps UnifiedWorkflowInput

    This allows existing code to work without changes
    """
    if isinstance(workflow_input, WorkflowInput):
        unified_input = UnifiedWorkflowInput(input_as_text=workflow_input.input_as_text)
    elif isinstance(workflow_input, UnifiedWorkflowInput):
        unified_input = workflow_input
    else:
        # Assume it's a dict or similar
        unified_input = UnifiedWorkflowInput(input_as_text=str(workflow_input))

    return run_unified_workflow(unified_input)
