"""
Streamlit UI for Swine Farm AI Agent with Interactive Charts
Supports both text analysis and chart visualization
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, '/tmp/swine_alert-main/agentkit_python/')

from workflow_unified import run_unified_workflow, UnifiedWorkflowInput
from chart_renderer import render_chart, add_threshold_lines
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container


st.set_page_config(
    page_title="Swine Farm AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===== SESSION STATE =====

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "force_workflow" not in st.session_state:
    st.session_state.force_workflow = None  # Can be "chart" or "text"


# ===== MAIN UI =====

st.title("🐷 Swine Farm AI Assistant")
st.markdown("**Powered by OpenAI Agent SDK • Real Snowflake Data • Interactive Charts with Plotly**")


# ===== SIDEBAR =====

with st.sidebar:
    st.header("⚙️ System Info")
    st.success("✅ Agent SDK Active")
    st.info("🛡️ Prompt & SQL Injection Detection")
    st.info("📊 Interactive Charts Enabled")

    st.markdown("---")

    st.header("💾 Database Connection")

    database_mode = st.radio(
        "Select database:",
        ["Snowflake (Production)", "SQLite (Local Testing)"],
        help="Snowflake requires network access. Use SQLite for local testing if you have network policy restrictions."
    )

    use_local_db = (database_mode == "SQLite (Local Testing)")

    if use_local_db:
        st.warning("⚠️ Using local SQLite database. Make sure you have created swine_data.db in the data/ folder.")
    else:
        st.info("💾 Snowflake Connection Enabled")

    st.markdown("---")

    st.header("🎨 Visualization Mode")

    workflow_mode = st.radio(
        "Select mode:",
        ["Auto-detect", "Force Charts", "Force Text"],
        help="Auto-detect uses AI to determine if you want a chart or text. Force mode overrides detection."
    )

    use_mcp = st.checkbox(
        "Use MCP Server (experimental)",
        value=False,
        help="Enable MCP server for chart specification generation"
    )

    if use_mcp:
        mcp_url = st.text_input(
            "MCP Server URL",
            value="http://localhost:8000",
            help="Enter the URL of your MCP server"
        )
    else:
        mcp_url = None

    st.markdown("---")

    st.header("📊 Database")
    st.markdown("""
    **Table:** `SWINE_ALERT`

     **Key Metrics:**
    - 🔴 Mortality (DC_PERCENT, YTD_PERCENT)
    - 🌡️ Temperature (MIN/MAX_INDOOR_TEMPERATURE)
    - 🦠 Disease tracking (PNEUMONIA, DIARRHEA, FEVER, etc.)
    - 🍽️ Feed efficiency (FEED_INTAKE_ACTUAL vs STD)
    - 🛡️ Biosecurity (R1/R2 inspections)
    - 📍 Farm tracking (FARM_NAME, BARN_NAME, FLOCK_CODE)
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ===== CHAT INTERFACE =====

# Create a container for messages
messages_container = st.container()

with messages_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("type") == "chart":
                # Render chart message
                st.markdown(message.get("text", ""))
                if "chart_figure" in message:
                    st.plotly_chart(message["chart_figure"], use_container_width=True)
                if "expanders" in message:
                    for expander_data in message["expanders"]:
                        with st.expander(expander_data["title"]):
                            if expander_data["type"] == "sql":
                                st.code(expander_data["content"], language="sql")
                            elif expander_data["type"] == "dataframe":
                                st.dataframe(expander_data["content"], use_container_width=True)
                            elif expander_data["type"] == "json":
                                st.json(expander_data["content"])
                            elif expander_data["type"] == "metrics":
                                cols = st.columns(len(expander_data["content"]))
                                for idx, (label, value) in enumerate(expander_data["content"].items()):
                                    cols[idx].metric(label, value)
            else:
                # Regular text message
                st.markdown(message["content"])


# ===== RESULT OUTPUT FUNCTIONS =====

def render_text_result(result, duration):
    """Render text analysis workflow result"""
    if result.get("success"):
        # Display analysis
        analysis = result.get("analysis", "No analysis available")
        st.markdown(analysis)

        # Show SQL query
        if result.get("sql_query"):
            with st.expander("📝 Generated SQL Query"):
                st.code(result["sql_query"], language="sql")

        # Show raw results
        if result.get("raw_results"):
            with st.expander(f"📊 Raw Query Results ({len(result['raw_results'])} rows)"):
                df = pd.DataFrame(result["raw_results"])
                st.dataframe(df, use_container_width=True)

        # Show security checks
        if result.get("security_checks"):
            with st.expander("🛡️ Security Checks"):
                checks = result["security_checks"]

                # OpenAI Moderation
                if "openai_moderation" in checks:
                    st.success("✅ Content Safety: Passed")

                # Jailbreak Detection
                if "jailbreak_detection" in checks:
                    jb = checks["jailbreak_detection"]
                    confidence = jb.get("confidence", 0)
                    st.success(f"✅ Injection Detection: Safe (confidence: {confidence:.2%})")

        # Performance stats
        with st.expander("⚡ Performance"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Duration", f"{duration:.2f}s")
            col2.metric("Rows", len(result.get("raw_results", [])))
            if result.get("security_checks"):
                col3.metric("Security", "✅ Passed")

        # Add to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": analysis,
            "type": "text"
        })

    else:
        # Error handling
        error_msg = result.get("error", "Unknown error")
        st.error(f"❌ Error: {error_msg}")

        # Show security block reason if applicable
        if result.get("reason"):
            reason = result.get("reason")
            details = result.get("details", {})

            st.warning(f"🛡️ Security Alert: {reason}")

            with st.expander("🔍 Details"):
                st.json(details)

        # Show failed SQL if available
        if result.get("sql_query"):
            with st.expander("❌ Failed SQL Query"):
                st.code(result["sql_query"], language="sql")

        # Add error to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Error: {error_msg}",
            "type": "text"
        })


def render_chart_result(result, duration):
    """Render chart visualization workflow result"""
    if result.get("success"):
        chart_spec = result.get("chart_spec", {})
        raw_results = result.get("raw_results", [])

        # Create chart
        try:
            fig = render_chart(chart_spec, raw_results)

            # Add threshold lines for mortality charts
            if "mortality" in chart_spec.get("title", "").lower() or "dc_percent" in str(chart_spec.get("y_axis", "")).lower():
                fig = add_threshold_lines(fig, {
                    "Critical (5%)": 5.0,
                    "Warning (3%)": 3.0
                })

            # Display chart
            st.plotly_chart(fig, use_container_width=True)

            # Chart description
            st.markdown(f"**Chart Type:** {chart_spec['chart_type'].title()}")
            st.markdown(f"**Reasoning:** {chart_spec.get('reasoning', 'N/A')}")

        except Exception as e:
            st.error(f"❌ Chart rendering failed: {str(e)}")
            st.markdown("**Raw data:**")
            df = pd.DataFrame(raw_results)
            st.dataframe(df, use_container_width=True)
            fig = None

        # Expandable sections
        expanders = []

        # Show SQL query
        if result.get("sql_query"):
            with st.expander("📝 Generated SQL Query"):
                st.code(result["sql_query"], language="sql")
            expanders.append({
                "title": "📝 Generated SQL Query",
                "type": "sql",
                "content": result["sql_query"]
            })

        # Show raw data
        if raw_results:
            with st.expander(f"📊 Raw Data ({len(raw_results)} rows)"):
                df = pd.DataFrame(raw_results)
                st.dataframe(df, use_container_width=True)
            expanders.append({
                "title": f"📊 Raw Data ({len(raw_results)} rows)",
                "type": "dataframe",
                "content": df
            })

        # Show chart specification
        with st.expander("🎨 Chart Specification"):
            st.json(chart_spec)
        expanders.append({
            "title": "🎨 Chart Specification",
            "type": "json",
            "content": chart_spec
        })

        # Performance stats
        with st.expander("⚡ Performance"):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Duration", f"{duration:.2f}s")
            col2.metric("Rows", len(raw_results))
            col3.metric("Chart Type", chart_spec.get("chart_type", "N/A").title())
            col4.metric("Database", result.get("database", "Snowflake"))

            # Show security status
            st.success("🛡️ Security: Passed")
        expanders.append({
            "title": "⚡ Performance",
            "type": "metrics",
            "content": {
                "Duration": f"{duration:.2f}s",
                "Rows": len(raw_results),
                "Chart Type": chart_spec.get("chart_type", "N/A").title(),
                "Database": result.get("database", "Snowflake"),
                "Security": "✅ Passed"
            }
        })

        # Add to history
        st.session_state.messages.append({
            "role": "assistant",
            "type": "chart",
            "text": f"**{chart_spec.get('title', 'Chart')}**\n\n{chart_spec.get('reasoning', '')}",
            "chart_figure": fig,
            "expanders": expanders
        })

    else:
        # Error handling
        error_msg = result.get("error", "Unknown error")
        st.error(f"❌ Error: {error_msg}")

        # Show suggestion if available (e.g., network policy workaround)
        if result.get("suggestion"):
            st.info(f"💡 Suggestion: {result['suggestion']}")

        # Special handling for network policy errors
        if "network policy" in error_msg.lower() or "failed to connect" in error_msg.lower():
            st.warning("🔒 **Snowflake Network Policy Error**")
            st.markdown("""
            Your IP address is not whitelisted in Snowflake's network policy.

            **Solutions:**
            1. **Use Local SQLite Mode** (recommended for testing):
               - Go to sidebar → **Database Connection** → Select **"SQLite (Local Testing)"**
               - Make sure you have a `data/swine_data.db` file

            2. **Contact Snowflake Admin**:
               - Ask to whitelist your IP address
               - Or get VPN access to an allowed network

            3. **Use VPN** if your organization provides one
            """)

        if result.get("sql_query"):
            with st.expander("❌ Failed SQL Query"):
                st.code(result["sql_query"], language="sql")

        # Add error to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Error: {error_msg}",
            "type": "text"
        })


def process_user_query(prompt):
    """Process a user query through the unified workflow"""
    # Determine force flags based on workflow mode
    force_chart = workflow_mode == "Force Charts"
    force_text = workflow_mode == "Force Text"

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with messages_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process with agent
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent analyzing..."):
                start_time = datetime.now()

                workflow_input = UnifiedWorkflowInput(
                    input_as_text=prompt,
                    force_chart=force_chart,
                    force_text=force_text,
                    use_mcp_server=use_mcp,
                    mcp_server_url=mcp_url,
                    use_local_db=use_local_db
                )

                result = run_unified_workflow(workflow_input)
                duration = (datetime.now() - start_time).total_seconds()

            # Render based on workflow type
            if result.get("workflow_type") == "chart":
                render_chart_result(result, duration)
            else:
                render_text_result(result, duration)


# ===== CHAT INPUT =====

# Process pending query from quick buttons
if st.session_state.pending_query:
    prompt = st.session_state.pending_query
    st.session_state.pending_query = None  # Clear it
    process_user_query(prompt)


# Chat input
if prompt := st.chat_input("Ask about swine farm data or request a chart..."):
    process_user_query(prompt)


# ===== QUICK ACTION BUTTONS =====

with stylable_container(
    key="bottom_content",
    css_styles="""
    {
        position: fixed;
        bottom: 100px;
        left: 0;
        width: 90%;
        display: flex;
        justify-content: center;
        box-sizing: border-box;
        margin-left: 5%;
        margin-right: 5%;
        padding-bottom: 10px;
    }
    """,
):
    st.markdown("**Quick Actions:**")

    # Row 1: Text queries
    col1, col2, col3 = st.columns([1, 1, 1], gap="small")

    with col1:
        if st.button("🚨 High Mortality", use_container_width=True):
            st.session_state.pending_query = "Show me farms where DC_PERCENT is above 5%"
            st.rerun()

    with col2:
        if st.button("🦠 Disease Outbreaks", use_container_width=True):
            st.session_state.pending_query = "Which barns have PNEUMONIA_PERCENT or DIARRHEA_PERCENT above 10%?"
            st.rerun()

    with col3:
        if st.button("🌡️ Temperature Issues", use_container_width=True):
            st.session_state.pending_query = "Which farms have indoor temperature variance greater than 10 degrees?"
            st.rerun()

    # Row 2: Chart queries
    col4, col5, col6 = st.columns([1, 1, 1], gap="small")

    with col4:
        if st.button("📈 Mortality Trends", use_container_width=True):
            st.session_state.pending_query = "Show me a chart of mortality trends over the last 30 days"
            st.rerun()

    with col5:
        if st.button("📊 Disease Comparison", use_container_width=True):
            st.session_state.pending_query = "Visualize disease trends (pneumonia, diarrhea, fever) for the past 2 weeks"
            st.rerun()

    with col6:
        if st.button("🔥 Temp vs Mortality", use_container_width=True):
            st.session_state.pending_query = "Plot temperature variance vs mortality correlation"
            st.rerun()


# ===== FOOTER =====
# Note: Footer removed to prevent overlap with quick action buttons and chat input
# The information is already shown in the sidebar and page title
