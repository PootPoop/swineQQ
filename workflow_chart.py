"""
Chart Workflow for Swine Farm AI Assistant
Orchestrates chart-specific agents for data visualization
"""
from pydantic import BaseModel
from chart_agents import (
    detect_chart_intent,
    generate_chart_sql,
    generate_chart_specification,
    generate_chart_specification_mcp
)
from guardrails_advanced import run_security_checks
import os
from typing import Optional


# ===== DATABASE EXECUTION =====

def execute_snowflake_query(sql_query: str) -> list:
    """Execute query on Snowflake database"""
    import snowflake.connector

    config = {
        'account': os.getenv('JAPFA_ACCOUNT'),
        'user': os.getenv('JAPFA_USER'),
        'password': os.getenv('JAPFA_PASSWORD'),
        'database': os.getenv('JAPFA_DATABASE'),
        'schema': os.getenv('JAPFA_SCHEMA'),
        'warehouse': os.getenv('JAPFA_WAREHOUSE'),
        'role': os.getenv('JAPFA_ROLE', 'PUBLIC')
    }

    conn = snowflake.connector.connect(**config)

    try:
        cursor = conn.cursor(snowflake.connector.DictCursor)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()


# ===== WORKFLOW =====

class ChartWorkflowInput(BaseModel):
    input_as_text: str
    use_mcp_server: bool = False
    mcp_server_url: Optional[str] = None


def run_chart_workflow(workflow_input: ChartWorkflowInput):
    """
    Execute the chart generation workflow with multiple specialized agents

    Workflow Steps:
    1. Security checks (same as text workflow)
    2. Generate chart-optimized SQL query (Agent 2)
    3. Execute query on Snowflake
    4. Generate chart specification (Agent 3, optionally via MCP)
    5. Return chart data + specification for rendering

    Args:
        workflow_input: ChartWorkflowInput with user query

    Returns:
        dict with success status, chart data, and specification
    """
    user_input = workflow_input.input_as_text

    print("🛡️ Step 1: Multi-layer security checks...")
    security_result = run_security_checks(user_input, jailbreak_threshold=0.5)
    if security_result.get("blocked"):
        return {
            "success": False,
            "error": f"Security check failed: {security_result['reason']}",
            "details": security_result
        }

    print("📊 Step 2: Generating chart-optimized SQL query...")
    try:
        sql_query = generate_chart_sql(user_input)
        print(f"Generated SQL:\n{sql_query}\n")
    except Exception as e:
        return {
            "success": False,
            "error": f"SQL generation failed: {str(e)}"
        }

    print("💾 Step 3: Executing query on Snowflake...")
    try:
        results = execute_snowflake_query(sql_query)
        print(f"Retrieved {len(results)} rows")

        if not results:
            return {
                "success": False,
                "error": "Query returned no results",
                "sql_query": sql_query
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Query execution failed: {str(e)}",
            "sql_query": sql_query
        }

    print("🎨 Step 4: Generating chart specification...")
    try:
        if workflow_input.use_mcp_server:
            chart_spec = generate_chart_specification_mcp(
                user_input,
                sql_query,
                results,
                workflow_input.mcp_server_url
            )
            print("Used MCP server for chart specification")
        else:
            chart_spec = generate_chart_specification(
                user_input,
                sql_query,
                results
            )
            print("Used OpenAI for chart specification")

        print(f"Chart Type: {chart_spec.chart_type}")
        print(f"Title: {chart_spec.title}")

    except Exception as e:
        return {
            "success": False,
            "error": f"Chart specification failed: {str(e)}",
            "sql_query": sql_query,
            "raw_results": results
        }

    print("✅ Chart workflow complete!")

    return {
        "success": True,
        "workflow_type": "chart",
        "sql_query": sql_query,
        "raw_results": results,
        "chart_spec": chart_spec.model_dump(),
        "security_checks": security_result,
        "row_count": len(results)
    }
