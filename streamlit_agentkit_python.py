"""
Streamlit UI for Swine Farm AI Agent
"""
import streamlit as st
import pandas as pd
# from agentkit_python.workflow_okd import run_workflow, WorkflowInput
from workflow import run_workflow, WorkflowInput
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

# Initialize pending_query state
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# ===== MAIN UI =====

st.title("Swine Farm AI Assistant")
st.markdown("**Powered by OpenAI Agent SDK + Real Snowflake Data**")

# ===== SIDEBAR =====

with st.sidebar:
    st.header("⚙️ System Info")
    st.success("✅ Agent SDK Active")
    st.info("💾 Snowflake Connected")
    st.info("🛡️ Prompt & SQL Injection Detection")
    
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
    
    if st.button("🗑️ Clear Chat", width='stretch'):
        st.session_state.messages = []
        st.rerun()

# ===== CHAT INTERFACE =====

# Create a container for messages that will stay above the fixed bottom section
messages_container = st.container()

with messages_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ===== CHAT INPUT =====


def result_output(result, duration):
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
                st.dataframe(df, width='content')
        
        # Show security checks
        if result.get("security_checks"):
            with st.expander("🛡️ Security Checks"):
                checks = result["security_checks"]
                
                # OpenAI Moderation
                if "openai_moderation" in checks:
                    mod = checks["openai_moderation"]
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
        
        # Add to history (ONCE, at the end)
        st.session_state.messages.append({
            "role": "assistant",
            "content": analysis
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
            "content": f"Error: {error_msg}"
        })


# Process pending query from quick buttons
if st.session_state.pending_query:
    prompt = st.session_state.pending_query
    st.session_state.pending_query = None  # Clear it
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with messages_container:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with agent
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent analyzing..."):
                start_time = datetime.now()
                result = run_workflow(WorkflowInput(input_as_text=prompt))
                duration = (datetime.now() - start_time).total_seconds()
            
            result_output(result, duration)


# Chat input
if prompt := st.chat_input("Ask about swine farm data..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with messages_container:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with agent
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent analyzing..."):
                start_time = datetime.now()
                result = run_workflow(WorkflowInput(input_as_text=prompt))
                duration = (datetime.now() - start_time).total_seconds()
            
            result_output(result, duration)



# ===== QUICK QUERIES =====
with stylable_container(
    key="bottom_content",
    css_styles="""
    {
        position: absolute;
        bottom: 130px;
        left: 0;
        width: 90%;
        display: flex;
        justify-content: center;
        box-sizing: border-box;
        margin-left: 5%;
        margin-right: 5%;
    }
    """,
):
    col1, col2, col3 = st.columns([1, 1, 1], gap="small")

    clicked_prompt = None

    
    with col1:
        if st.button("🚨 High Mortality", use_container_width=True):
            clicked_prompt = "Show me farms where DC_PERCENT is above 5%"

    with col2:
        if st.button("🦠 Disease Outbreaks", use_container_width=True):
            clicked_prompt = "Which barns have PNEUMONIA_PERCENT or DIARRHEA_PERCENT above 10%?"

    with col3:
        if st.button("🌡️ Temperature Issues", use_container_width=True):
            clicked_prompt = "Which farms have indoor temperature variance greater than 10 degrees?"


# Immediately process the click
if clicked_prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": clicked_prompt})
    
    with messages_container:
        with st.chat_message("user"):
            st.markdown(clicked_prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent analyzing..."):
                start_time = datetime.now()
                result = run_workflow(WorkflowInput(input_as_text=clicked_prompt))
                duration = (datetime.now() - start_time).total_seconds()
            
            result_output(result, duration)




# ===== FOOTER =====

st.markdown(
    """
    <div style="
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        font-size: 0.8em;
        padding: 8px 0;
        border-top: 1px solid #e6e6e6;
        z-index: 1000;
    ">
        Powered by OpenAI Agent SDK • Real Snowflake Data • Prompt & SQL Injection Detection
    </div>
    """,
    unsafe_allow_html=True,
)
