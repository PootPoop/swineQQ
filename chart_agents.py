"""
Chart-Specific Agents for Swine Farm AI Assistant
Handles detection, SQL generation, and chart specification for data visualization
"""
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Literal
import os
from dotenv import load_dotenv

# Load environment variables (handle encoding errors on Windows)
try:
    load_dotenv()
except UnicodeDecodeError:
    print("⚠️ Warning: .env file has encoding issues. Please save it as UTF-8.")
    print("   Using environment variables from system instead.")
except Exception as e:
    print(f"⚠️ Warning: Could not load .env file: {e}")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# ===== PROMPTS =====

CHART_DETECTION_PROMPT = """You are a chart intent classifier for a swine farm analytics system.

Your role is to determine if the user wants to visualize data as a chart/graph, or if they want a text-based analysis.

**Chart Keywords:** chart, graph, plot, visualize, visualization, show me a, display, trend, over time, compare, comparison

**Chart Intent Examples:**
- "Show me a chart of mortality rates by farm"
- "Plot temperature trends over the last week"
- "Visualize disease outbreaks across barns"
- "Graph the feed efficiency comparison"
- "I want to see mortality trends"

**Text Analysis Examples:**
- "What are the farms with high mortality?"
- "Tell me about temperature issues"
- "Which barns have disease problems?"
- "Explain the feed efficiency data"

**Output Format:**
Respond with ONLY a JSON object:
```json
{
  "intent": "chart" or "text",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}
```

**Examples:**

Input: "Show me a chart of DC_PERCENT by farm"
Output:
```json
{
  "intent": "chart",
  "confidence": 0.95,
  "reasoning": "User explicitly requests a chart visualization"
}
```

Input: "Which farms have high mortality?"
Output:
```json
{
  "intent": "text",
  "confidence": 0.90,
  "reasoning": "User wants factual information, not visualization"
}
```

Input: "Plot pneumonia rates over time"
Output:
```json
{
  "intent": "chart",
  "confidence": 0.98,
  "reasoning": "User wants to visualize temporal trends using 'plot' keyword"
}
```
"""


CHART_SQL_PROMPT = """You are a translator between natural language and SQL queries optimized for chart visualization.

Your role is to transform a chart visualization request into a SQL query that returns data suitable for plotting.

<full_ontology>
version: 1.1
namespace: swine_farm_ontology

entities:
  jini_swine_dataset:
    table: SWINE_ALERT
    description: >
      Main integrated dataset for swine farm operations, environmental metrics,
      mortality data, disease indicators, and biosecurity checks.

    key_columns_for_charts:
      # Time/Date fields for trend analysis
      REPORT_DATE: {type: TIMESTAMP, description: "Date when report was created - use for time series"}
      START_DATE: {type: STRING, description: "Start date of reporting period"}
      END_DATE: {type: STRING, description: "End date of reporting period"}

      # Grouping/Category fields
      FARM_NAME: {type: STRING, description: "Farm identifier - use for categorical grouping"}
      BARN_NAME: {type: STRING, description: "Barn identifier - use for categorical grouping"}
      OPERATION: {type: STRING, description: "Operational unit - use for regional grouping"}
      FARM_TYPE: {type: STRING, description: "Farm type for comparison"}

      # Numeric metrics for Y-axis
      DC_PERCENT: {type: FLOAT, description: "Death/culling % (Primary KPI)"}
      YTD_PERCENT: {type: FLOAT, description: "Year-to-date mortality %"}
      PNEUMONIA_PERCENT: {type: FLOAT, description: "Pneumonia incidence %"}
      DIARRHEA_PERCENT: {type: FLOAT, description: "Diarrhea incidence %"}
      FEVER_PERCENT: {type: FLOAT, description: "Fever incidence %"}
      MIN_INDOOR_TEMPERATURE: {type: FLOAT, description: "Minimum indoor temp (°C)"}
      MAX_INDOOR_TEMPERATURE: {type: FLOAT, description: "Maximum indoor temp (°C)"}
      FEED_INTAKE_ACTUAL: {type: FLOAT, description: "Actual feed intake (kg/day)"}
      FEED_INTAKE_STD: {type: FLOAT, description: "Standard feed intake (kg/day)"}

      # Count fields
      DC_HEAD: {type: INTEGER, description: "Death count"}
      BEGIN_POP: {type: INTEGER, description: "Starting population"}
      PNEUMONIA_COUNT: {type: INTEGER, description: "Pneumonia case count"}
      DIARRHEA_COUNT: {type: INTEGER, description: "Diarrhea case count"}
</full_ontology>

**CHART-OPTIMIZED SQL RULES:**

1. **Time Series Queries** (trends over time):
   - ALWAYS use REPORT_DATE for time-based charts
   - Format: `DATE(REPORT_DATE)` for daily aggregation
   - Order by date: `ORDER BY REPORT_DATE ASC`
   - Include date range filters when possible

2. **Categorical Comparisons** (bar charts, comparisons):
   - Group by categorical fields (FARM_NAME, BARN_NAME, OPERATION)
   - Use aggregate functions: AVG(), SUM(), COUNT(), MAX()
   - Limit to top N results: `LIMIT 10` (adjustable)

3. **Correlation/Scatter Plots**:
   - Select 2-3 numeric columns for X/Y axes
   - Include identifying column (FARM_NAME) for point labels

4. **Multi-metric Charts**:
   - Select multiple related metrics for comparison
   - Keep column names clear for legend labels

5. **Performance**:
   - Use LIMIT clause (default 50 for charts, max 200)
   - Avoid SELECT * - choose specific columns
   - Use WHERE clauses to filter relevant data

**OUTPUT FORMAT:**
Return ONLY the SQL query in a markdown code block:

```sql
SELECT
    DATE(report_date) as date,
    farm_name,
    AVG(dc_percent) as avg_mortality
FROM swine_alert
WHERE report_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(report_date), farm_name
ORDER BY date ASC
LIMIT 50;
```

**EXAMPLE QUERIES:**

User: "Show me mortality trends over the last month"
```sql
SELECT
    DATE(report_date) as date,
    AVG(dc_percent) as avg_mortality_percent
FROM swine_alert
WHERE report_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(report_date)
ORDER BY date ASC;
```

User: "Compare pneumonia rates across top 5 farms"
```sql
SELECT
    farm_name,
    AVG(pneumonia_percent) as avg_pneumonia,
    COUNT(*) as record_count
FROM swine_alert
WHERE pneumonia_percent IS NOT NULL
GROUP BY farm_name
ORDER BY avg_pneumonia DESC
LIMIT 5;
```

User: "Plot temperature vs mortality correlation"
```sql
SELECT
    farm_name,
    AVG(max_indoor_temperature - min_indoor_temperature) as temp_variance,
    AVG(dc_percent) as avg_mortality
FROM swine_alert
WHERE max_indoor_temperature IS NOT NULL
  AND min_indoor_temperature IS NOT NULL
GROUP BY farm_name
LIMIT 30;
```

User: "Visualize disease trends for the past 2 weeks"
```sql
SELECT
    DATE(report_date) as date,
    AVG(pneumonia_percent) as pneumonia,
    AVG(diarrhea_percent) as diarrhea,
    AVG(fever_percent) as fever
FROM swine_alert
WHERE report_date >= CURRENT_DATE - INTERVAL '14 days'
GROUP BY DATE(report_date)
ORDER BY date ASC;
```

Generate ONLY the SQL query. Do NOT include explanations outside the code block.
"""


CHART_SPECIFICATION_PROMPT = """You are a data visualization expert specializing in agricultural and livestock analytics.

Your role is to analyze SQL query results and determine the optimal chart type and configuration for Plotly visualization.

**Available Chart Types:**
1. **line** - Time series, trends over time
2. **bar** - Categorical comparisons, rankings
3. **scatter** - Correlations, relationships between variables
4. **multi_line** - Multiple metrics over time
5. **grouped_bar** - Multi-category comparisons
6. **pie** - Proportions, distribution breakdowns
7. **heatmap** - Matrix data, correlation matrices

**Chart Selection Guidelines:**

**Use LINE charts when:**
- Data has a date/time column
- Showing trends or changes over time
- Single metric progression

**Use MULTI_LINE charts when:**
- Multiple metrics over the same time period
- Comparing different categories over time
- Disease trends (pneumonia, diarrhea, fever together)

**Use BAR charts when:**
- Comparing categorical data (farms, barns)
- Showing rankings (top 10 farms by mortality)
- Single metric across categories

**Use GROUPED_BAR charts when:**
- Comparing multiple metrics across categories
- Side-by-side comparisons
- Multi-period comparisons by category

**Use SCATTER charts when:**
- Showing correlation between 2 numeric variables
- Identifying outliers
- Relationship analysis (temperature vs mortality)

**Use PIE charts when:**
- Showing proportions or percentages
- Comparing parts of a whole
- Distribution breakdown (e.g., mortality by farm, cases by type)
- Limited number of categories (ideally 3-8)
- Want to emphasize percentage composition

**Use HEATMAP charts when:**
- Matrix-style data
- Showing patterns across 2 dimensions
- Intensity visualization

**OUTPUT FORMAT:**
Return ONLY a JSON object:

```json
{
  "chart_type": "line|bar|scatter|multi_line|grouped_bar|pie|heatmap",
  "x_axis": "column_name",
  "y_axis": "column_name|[column1, column2, ...]",
  "title": "Descriptive chart title",
  "x_label": "X-axis label",
  "y_label": "Y-axis label",
  "color_by": "column_name (optional)",
  "height": 400-600,
  "show_legend": true|false,
  "reasoning": "Why this chart type was chosen"
}
```

**EXAMPLES:**

Input SQL Result Columns: [date, avg_mortality_percent]
Input Original Query: "Show me mortality trends over the last month"
Output:
```json
{
  "chart_type": "line",
  "x_axis": "date",
  "y_axis": "avg_mortality_percent",
  "title": "Mortality Trends - Last 30 Days",
  "x_label": "Date",
  "y_label": "Mortality Rate (%)",
  "color_by": null,
  "height": 450,
  "show_legend": false,
  "reasoning": "Time series data with single metric - line chart shows trend clearly"
}
```

Input SQL Result Columns: [farm_name, avg_pneumonia, record_count]
Input Original Query: "Compare pneumonia rates across top 5 farms"
Output:
```json
{
  "chart_type": "bar",
  "x_axis": "farm_name",
  "y_axis": "avg_pneumonia",
  "title": "Top 5 Farms by Pneumonia Rate",
  "x_label": "Farm",
  "y_label": "Pneumonia Rate (%)",
  "color_by": null,
  "height": 400,
  "show_legend": false,
  "reasoning": "Categorical comparison with ranking - bar chart is ideal for comparing farms"
}
```

Input SQL Result Columns: [farm_name, temp_variance, avg_mortality]
Input Original Query: "Plot temperature vs mortality correlation"
Output:
```json
{
  "chart_type": "scatter",
  "x_axis": "temp_variance",
  "y_axis": "avg_mortality",
  "title": "Temperature Variance vs Mortality Correlation",
  "x_label": "Temperature Variance (°C)",
  "y_label": "Average Mortality (%)",
  "color_by": "farm_name",
  "height": 500,
  "show_legend": true,
  "reasoning": "Correlation analysis between two numeric variables - scatter plot shows relationship and outliers"
}
```

Input SQL Result Columns: [date, pneumonia, diarrhea, fever]
Input Original Query: "Visualize disease trends for the past 2 weeks"
Output:
```json
{
  "chart_type": "multi_line",
  "x_axis": "date",
  "y_axis": ["pneumonia", "diarrhea", "fever"],
  "title": "Disease Trends - Last 14 Days",
  "x_label": "Date",
  "y_label": "Incidence Rate (%)",
  "color_by": null,
  "height": 500,
  "show_legend": true,
  "reasoning": "Multiple disease metrics over time - multi-line chart allows comparison of trends"
}
```

Input SQL Result Columns: [farm_name, total_mortality_count]
Input Original Query: "Show me mortality distribution by farm as a pie chart"
Output:
```json
{
  "chart_type": "pie",
  "x_axis": "farm_name",
  "y_axis": "total_mortality_count",
  "title": "Mortality Distribution by Farm",
  "x_label": "Farm",
  "y_label": "Deaths",
  "color_by": null,
  "height": 500,
  "show_legend": true,
  "reasoning": "Distribution breakdown showing each farm's proportion of total mortality - pie chart emphasizes percentage composition"
}
```

Analyze the query results and return the optimal chart specification.
"""


# ===== AGENT CLASSES =====

class ChartIntent(BaseModel):
    intent: Literal["chart", "text"]
    confidence: float
    reasoning: str


class ChartSpecification(BaseModel):
    chart_type: Literal["line", "bar", "scatter", "multi_line", "grouped_bar", "pie", "heatmap"]
    x_axis: str
    y_axis: str | list[str]
    title: str
    x_label: str
    y_label: str
    color_by: Optional[str] = None
    height: int = 450
    show_legend: bool = True
    reasoning: str


# ===== AGENT FUNCTIONS =====

def detect_chart_intent(user_query: str) -> ChartIntent:
    """
    Agent 1: Determine if user wants a chart or text analysis

    Args:
        user_query: User's natural language query

    Returns:
        ChartIntent with intent classification and confidence
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CHART_DETECTION_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3
    )

    import json
    import re

    content = response.choices[0].message.content

    # Extract JSON from markdown code block if present
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_match = re.search(r'\{.*?\}', content, re.DOTALL)
        json_str = json_match.group(0) if json_match else content

    result = json.loads(json_str)
    return ChartIntent(**result)


def generate_chart_sql(user_query: str) -> str:
    """
    Agent 2: Generate SQL query optimized for chart data

    Args:
        user_query: User's chart visualization request

    Returns:
        SQL query string
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CHART_SQL_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0.2
    )

    sql_text = response.choices[0].message.content

    # Extract SQL from markdown code block
    import re
    sql_match = re.search(r'```sql\n(.*?)\n```', sql_text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()

    # Try any code block
    code_match = re.search(r'```\n(.*?)\n```', sql_text, re.DOTALL)
    if code_match and 'SELECT' in code_match.group(1).upper():
        return code_match.group(1).strip()

    # Last resort
    if 'SELECT' in sql_text.upper():
        return sql_text.strip()

    raise ValueError(f"Could not extract SQL from response: {sql_text[:200]}")


def generate_chart_specification(
    user_query: str,
    sql_query: str,
    query_results: list
) -> ChartSpecification:
    """
    Agent 3: Generate chart type and configuration specification

    Args:
        user_query: Original user query
        sql_query: Generated SQL query
        query_results: Results from database query

    Returns:
        ChartSpecification with chart type and configuration
    """
    # Extract column names from first result
    if not query_results:
        raise ValueError("No query results to visualize")

    columns = list(query_results[0].keys()) if query_results else []

    context = f"""
Original User Query: {user_query}

SQL Query Executed:
```sql
{sql_query}
```

Result Columns: {columns}
Number of Rows: {len(query_results)}
Sample Data (first 3 rows):
{query_results[:3]}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CHART_SPECIFICATION_PROMPT},
            {"role": "user", "content": context}
        ],
        temperature=0.3
    )

    import json
    import re

    content = response.choices[0].message.content

    # Extract JSON from markdown code block if present
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_match = re.search(r'\{.*?\}', content, re.DOTALL)
        json_str = json_match.group(0) if json_match else content

    result = json.loads(json_str)
    return ChartSpecification(**result)


# ===== MCP SERVER INTEGRATION (Optional) =====

def generate_chart_specification_mcp(
    user_query: str,
    sql_query: str,
    query_results: list,
    mcp_server_url: Optional[str] = None
) -> ChartSpecification:
    """
    Alternative Agent 3 using MCP Server for chart specification

    This function can be used when an MCP server is configured for chart generation.
    Falls back to direct OpenAI call if MCP server is not available.

    Args:
        user_query: Original user query
        sql_query: Generated SQL query
        query_results: Results from database query
        mcp_server_url: Optional MCP server endpoint

    Returns:
        ChartSpecification
    """
    if not mcp_server_url:
        # Fallback to direct OpenAI implementation
        return generate_chart_specification(user_query, sql_query, query_results)

    # TODO: Implement MCP server integration
    # This is a placeholder for future MCP server integration
    try:
        import requests

        payload = {
            "query": user_query,
            "sql": sql_query,
            "results": query_results[:10],  # Send sample
            "columns": list(query_results[0].keys()) if query_results else []
        }

        response = requests.post(
            f"{mcp_server_url}/generate-chart-spec",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            spec_data = response.json()
            return ChartSpecification(**spec_data)
        else:
            print(f"⚠️ MCP server error, falling back to OpenAI: {response.status_code}")
            return generate_chart_specification(user_query, sql_query, query_results)

    except Exception as e:
        print(f"⚠️ MCP server unavailable, falling back to OpenAI: {e}")
        return generate_chart_specification(user_query, sql_query, query_results)
