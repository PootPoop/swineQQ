"""
Chart Workflow for Swine Farm AI Assistant (Local SQLite Version)
For testing without Snowflake access
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
import sqlite3
from pathlib import Path


# ===== DATABASE EXECUTION (SQLite) =====

def execute_sqlite_query(sql_query: str) -> list:
    """Execute query on local SQLite database"""
    db_path = Path(__file__).parent / "data" / "swine_data.db"

    if not db_path.exists():
        raise FileNotFoundError(
            f"SQLite database not found at {db_path}. "
            "Please create it using database.py or use Snowflake connection."
        )

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries

    try:
        cursor = conn.cursor()

        # Convert Snowflake SQL to SQLite compatible SQL
        sqlite_query = sql_query.replace("SWINE_ALERT", "swine_alert")

        # Handle DATE() function differences
        sqlite_query = sqlite_query.replace("DATE(report_date)", "date(report_date)")

        # Handle INTERVAL syntax (Snowflake to SQLite)
        import re
        sqlite_query = re.sub(
            r"CURRENT_DATE - INTERVAL '(\d+) days'",
            r"date('now', '-\1 days')",
            sqlite_query
        )

        cursor.execute(sqlite_query)

        # Convert Row objects to dictionaries
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    finally:
        cursor.close()
        conn.close()


# ===== WORKFLOW =====

class ChartWorkflowInput(BaseModel):
    input_as_text: str
    use_mcp_server: bool = False
    mcp_server_url: Optional[str] = None
    use_local_db: bool = False  # New flag for local testing


def run_chart_workflow(workflow_input: ChartWorkflowInput):
    """
    Execute the chart generation workflow with multiple specialized agents

    Can use either Snowflake (production) or SQLite (local testing)
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

    print("💾 Step 3: Executing query on database...")
    try:
        # Use local SQLite if specified, otherwise Snowflake
        if workflow_input.use_local_db:
            print("   Using local SQLite database...")
            results = execute_sqlite_query(sql_query)
        else:
            print("   Using Snowflake database...")
            # Import here to avoid circular dependency
            from workflow_chart import execute_snowflake_query
            results = execute_snowflake_query(sql_query)

        print(f"Retrieved {len(results)} rows")

        if not results:
            return {
                "success": False,
                "error": "Query returned no results",
                "sql_query": sql_query
            }
    except Exception as e:
        error_msg = str(e)

        # Detect Snowflake network policy error
        if "Network policy is required" in error_msg or "Failed to connect" in error_msg:
            return {
                "success": False,
                "error": "Snowflake network policy error: Your IP address is not whitelisted",
                "sql_query": sql_query,
                "suggestion": "Contact your Snowflake admin to whitelist your IP, use VPN, or enable local SQLite mode in the sidebar"
            }

        return {
            "success": False,
            "error": f"Query execution failed: {error_msg}",
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
        "row_count": len(results),
        "database": "SQLite (Local)" if workflow_input.use_local_db else "Snowflake (Production)"
    }
