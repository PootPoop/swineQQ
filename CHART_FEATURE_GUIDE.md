# Interactive Chart Feature Guide

## Overview

The Swine Farm AI Assistant now supports **interactive chart visualization** using a multi-agent architecture. Users can request charts/graphs by using keywords like "chart", "graph", "plot", "visualize" in their queries.

## Architecture

### Agent-Based Workflow

The chart feature uses **separate specialized agents** for different tasks:

```
User Query
    ↓
[Agent 1] → Intent Detection
    ↓
    ├─→ "chart" detected → Chart Workflow
    │       ↓
    │   [Agent 2] → SQL Query Generation (chart-optimized)
    │       ↓
    │   [Agent 3] → Execute Query on Snowflake
    │       ↓
    │   [Agent 4] → Chart Specification Generation
    │       ↓
    │   Render Interactive Chart (Plotly)
    │
    └─→ "text" detected → Text Analysis Workflow
            ↓
        [Original workflow for text-based analysis]
```

### Key Components

#### 1. **chart_agents.py**
Contains all chart-specific AI agents:
- `detect_chart_intent()` - Agent 1: Determines if user wants a chart
- `generate_chart_sql()` - Agent 2: Creates chart-optimized SQL queries
- `generate_chart_specification()` - Agent 3: Determines chart type and configuration
- `generate_chart_specification_mcp()` - Agent 3 (MCP variant): Uses MCP server for chart specs

#### 2. **workflow_chart.py**
Orchestrates the chart generation workflow:
- Executes security checks
- Coordinates agent calls
- Handles Snowflake query execution
- Returns chart data + specification

#### 3. **chart_renderer.py**
Renders interactive Plotly charts:
- Supports 7 chart types: line, bar, scatter, multi_line, grouped_bar, pie, heatmap
- Automatic color schemes and styling
- Threshold line support for KPI visualization
- Responsive and interactive

#### 4. **workflow_unified.py**
Main router that:
- Calls Agent 1 for intent detection
- Routes to chart or text workflow
- Supports force modes (force chart/text)
- Backward compatible with existing code

#### 5. **streamlit_app.py**
Enhanced UI with:
- Auto-detection mode (default)
- Force chart/force text modes
- Chart quick action buttons
- Interactive chart display
- Expandable sections for SQL, data, and specs

## Usage

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy from .env.example)
cp .env.example .env

# Edit .env with your credentials:
# - OPENAI_API_KEY
# - JAPFA_ACCOUNT, JAPFA_USER, JAPFA_PASSWORD, etc.

# Run the Streamlit app
streamlit run streamlit_app.py
```

### Chart Query Examples

#### Time Series Charts
```
"Show me a chart of mortality trends over the last 30 days"
"Plot temperature changes for the past week"
"Visualize disease trends over the last 2 weeks"
```

#### Comparison Charts
```
"Compare pneumonia rates across top 5 farms"
"Show me a bar chart of mortality by farm"
"Graph feed efficiency across different barns"
```

#### Correlation Charts
```
"Plot temperature variance vs mortality correlation"
"Show the relationship between feed intake and weight gain"
"Scatter plot of indoor temperature vs disease rate"
```

#### Multi-Metric Charts
```
"Visualize pneumonia, diarrhea, and fever trends together"
"Compare multiple disease indicators over time"
"Show mortality, temperature, and feed metrics on one chart"
```

### Workflow Modes

The sidebar offers 3 modes:

1. **Auto-detect** (Default)
   - AI determines if you want a chart or text
   - Uses keywords: "chart", "graph", "plot", "visualize", "show me", "trend", "compare"
   - Confidence-based routing

2. **Force Charts**
   - All queries generate charts
   - Useful when you want to visualize everything

3. **Force Text**
   - All queries return text analysis
   - Useful when you need detailed explanations

### Quick Action Buttons

The UI includes 6 quick action buttons:

**Text Queries:**
- 🚨 High Mortality
- 🦠 Disease Outbreaks
- 🌡️ Temperature Issues

**Chart Queries:**
- 📈 Mortality Trends
- 📊 Disease Comparison
- 🔥 Temp vs Mortality

## Chart Types

### 1. Line Chart
**Use for:** Time series, trends over time
```
Example: "Plot mortality trends over the last month"
```

### 2. Multi-Line Chart
**Use for:** Comparing multiple metrics over time
```
Example: "Show pneumonia, diarrhea, and fever trends together"
```

### 3. Bar Chart
**Use for:** Categorical comparisons, rankings
```
Example: "Compare mortality rates across farms"
```

### 4. Grouped Bar Chart
**Use for:** Multi-category comparisons
```
Example: "Compare disease rates by farm and barn"
```

### 5. Scatter Plot
**Use for:** Correlation analysis
```
Example: "Plot temperature vs mortality correlation"
```

### 6. Pie Chart
**Use for:** Proportions, distribution breakdowns
```
Example: "Show me mortality distribution by farm as a pie chart"
Example: "Pie chart of disease cases by type"
```

### 7. Heatmap
**Use for:** Matrix data, intensity visualization
```
Example: "Show disease distribution across farms and time"
```

## MCP Server Integration (Optional)

The system supports **MCP (Model Context Protocol) servers** for chart specification generation.

### Setting Up MCP Server

1. Enable in sidebar: Check "Use MCP Server (experimental)"
2. Enter MCP server URL (default: `http://localhost:8000`)
3. The system will use MCP for Agent 3 (chart specification)

### MCP Server API

Your MCP server should expose:

**Endpoint:** `POST /generate-chart-spec`

**Request:**
```json
{
  "query": "Show me mortality trends",
  "sql": "SELECT date, AVG(dc_percent) ...",
  "results": [...],
  "columns": ["date", "avg_mortality"]
}
```

**Response:**
```json
{
  "chart_type": "line",
  "x_axis": "date",
  "y_axis": "avg_mortality",
  "title": "Mortality Trends",
  "x_label": "Date",
  "y_label": "Mortality %",
  "color_by": null,
  "height": 450,
  "show_legend": false,
  "reasoning": "Time series data - line chart shows trend"
}
```

### Fallback Behavior

If MCP server is unavailable or errors:
- System automatically falls back to OpenAI-based chart specification
- No disruption to user experience
- Warning logged to console

## File Structure

```
swineQQ/
├── chart_agents.py              # Chart-specific AI agents
├── workflow_chart.py            # Chart workflow orchestrator
├── chart_renderer.py            # Plotly chart rendering
├── workflow_unified.py          # Main router (chart vs text)
├── streamlit_app.py            # Enhanced Streamlit UI
├── requirements.txt             # Dependencies
├── CHART_FEATURE_GUIDE.md      # This file
│
├── workflow.py                  # Original text workflow (from git history)
├── guardrails_advanced.py      # Security checks (from git history)
├── database.py                  # SQLite mirror for local testing
└── .env                         # Environment variables (not committed)
```

## Key Features

### Security
- Same multi-layer security checks as text workflow
- OpenAI Moderation API
- HuggingFace Jailbreak Detection
- SQL injection prevention (SELECT-only queries)

### Performance
- Optimized SQL queries for chart data
- Automatic result limiting (default: 50 rows for charts)
- Efficient data aggregation
- Fast Plotly rendering

### User Experience
- Auto-detection with confidence scoring
- Visual feedback (spinner, progress indicators)
- Expandable sections for SQL, data, specs
- Interactive charts (zoom, pan, hover)
- Threshold lines for KPI monitoring

## Customization

### Adding New Chart Types

1. Update `chart_renderer.py`:
```python
def create_custom_chart(df, x_col, y_col, title, x_label, y_label):
    # Your implementation
    return fig
```

2. Update `CHART_SPECIFICATION_PROMPT` in `chart_agents.py` to include new type

3. Add routing in `render_chart()` function

### Modifying Prompts

All agent prompts are in `chart_agents.py`:
- `CHART_DETECTION_PROMPT` - Intent classification
- `CHART_SQL_PROMPT` - SQL generation
- `CHART_SPECIFICATION_PROMPT` - Chart type selection

Edit these to customize agent behavior.

### Threshold Lines

Add custom thresholds in `streamlit_app.py`:

```python
# Add threshold lines for mortality charts
if "mortality" in chart_spec.get("title", "").lower():
    fig = add_threshold_lines(fig, {
        "Critical (5%)": 5.0,
        "Warning (3%)": 3.0,
        "Excellent (2%)": 2.0
    })
```

## Troubleshooting

### Charts Not Rendering

1. Check console for errors
2. Verify `plotly` is installed: `pip install plotly==6.3.1`
3. Check that query returned data (see "Raw Data" expander)
4. Verify column names match chart spec

### Intent Detection Issues

If queries are misclassified:
1. Use "Force Charts" or "Force Text" mode
2. Add more explicit keywords: "show me a chart", "plot this"
3. Adjust confidence threshold in `detect_chart_intent()`

### MCP Server Errors

If MCP server fails:
1. System automatically falls back to OpenAI
2. Check MCP server logs
3. Verify endpoint is accessible
4. Check request/response format matches spec

### Snowflake Connection Issues

1. Verify `.env` credentials
2. Test with text workflow first
3. Check network connectivity
4. Review Snowflake error messages in console

## Performance Tips

1. **Limit data**: Use date ranges in queries ("last 30 days")
2. **Aggregate**: Use GROUP BY for large datasets
3. **Index columns**: Ensure REPORT_DATE, FARM_NAME are indexed
4. **Cache**: Streamlit caches repeated queries automatically

## Advanced Usage

### Programmatic Access

```python
from workflow_unified import UnifiedWorkflowInput, run_unified_workflow

# Force chart generation
result = run_unified_workflow(UnifiedWorkflowInput(
    input_as_text="Show mortality trends",
    force_chart=True
))

if result["success"]:
    chart_spec = result["chart_spec"]
    data = result["raw_results"]
    # Use chart_spec and data
```

### Custom SQL Queries

```python
from chart_agents import generate_chart_specification
from chart_renderer import render_chart

# Your custom SQL result
data = [{"date": "2025-01-01", "mortality": 3.2}, ...]

# Generate chart spec
spec = generate_chart_specification(
    "Show mortality over time",
    "SELECT date, mortality FROM ...",
    data
)

# Render
fig = render_chart(spec.model_dump(), data)
```

## Next Steps

1. **Add more chart types**: Pie charts, area charts, box plots
2. **Export functionality**: Download charts as PNG/PDF
3. **Dashboard mode**: Multi-chart layouts
4. **Real-time updates**: Live data streaming
5. **Chart sharing**: Generate shareable links

## Support

For issues or questions:
1. Check this guide first
2. Review error messages in Streamlit console
3. Check agent prompts in `chart_agents.py`
4. Test with quick action buttons first

## License

Same as main project.
