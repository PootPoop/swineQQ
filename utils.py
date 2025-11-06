"""
Utility functions for Agent workflow
"""
import re
from typing import Optional


def extract_sql_from_markdown(text: str) -> str:
    """
    Extract SQL query from markdown code block or plain text
    
    Args:
        text: Response text from agent that may contain SQL
        
    Returns:
        Extracted SQL query string
        
    Raises:
        ValueError: If no SQL query found
    """
    # Try markdown code block first
    sql_match = re.search(r'```sql\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()
    
    # Try any code block
    code_match = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
    if code_match:
        potential_sql = code_match.group(1).strip()
        if 'SELECT' in potential_sql.upper():
            return potential_sql
    
    # Try to find SELECT statement directly
    select_match = re.search(r'(SELECT\s+.*?;)', text, re.DOTALL | re.IGNORECASE)
    if select_match:
        return select_match.group(1).strip()
    
    # Last resort: if text contains SELECT and FROM
    if 'SELECT' in text.upper() and 'FROM' in text.upper():
        # Clean up the text
        cleaned = text.strip()
        if not cleaned.endswith(';'):
            cleaned += ';'
        return cleaned
    
    raise ValueError(f"Could not extract SQL query from response: {text[:200]}...")


def format_results_for_display(results: list) -> str:
    """Format query results for display in conversation"""
    if not results:
        return "Query returned 0 rows."
    
    return f"Query returned {len(results)} rows:\n{str(results[:5])}{'...' if len(results) > 5 else ''}"