"""
Cortex AI Assistant - Natural Language Query Interface
Chat with your data using Snowflake Cortex Analyst
"""
from typing import Any, Dict, List
import pandas as pd
import requests
import streamlit as st
from datetime import datetime
from db_connection import init_connection
import os

# Custom CSS for enhanced chat interface


def load_css():
    st.markdown("""
    <style>
        /* ==================== CHAT INTERFACE DARK THEME ==================== */
        
        /* Main chat container */
        .stChatMessage {
            border-radius: 12px;
            padding: 18px;
            margin: 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* User message - Gradient style */
        .stChatMessage[data-testid="user-message"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
        }
        
        /* Assistant message - Light background with dark text */
        .stChatMessage[data-testid="assistant-message"] {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            color: #2c3e50;
        }
        
        /* Make sure all text in assistant messages is dark */
        .stChatMessage[data-testid="assistant-message"] p,
        .stChatMessage[data-testid="assistant-message"] span,
        .stChatMessage[data-testid="assistant-message"] div {
            color: #2c3e50 !important;
        }
        
        /* ==================== CHAT INPUT - FIXED BORDER ==================== */
        
        /* Main chat input container */
        .stChatInput {
            padding: 0 !important;
        }
        
        /* The actual input field */
        .stChatInput input {
            color: #e0e0e0 !important;
            background-color: transparent !important;
            border: none !important;
            padding: 14px 20px !important;
        }
        
        /* Input placeholder */
        .stChatInput input::placeholder {
            color: #888899 !important;
        }
        
        /* Input focus state */
        .stChatInput input:focus {
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Chat input button (send button) */
        .stChatInput button {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
            border: none !important;
            color: white !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            margin-right: 4px !important;
        }
        
        .stChatInput button:hover {
            background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
            transform: scale(1.05);
        }
        
        /* ==================== DATAFRAME STYLING ==================== */
        
        /* Dataframe container - Dark theme */
        .stDataFrame {
            background-color: #1e1e2e;
            border-radius: 8px;
            border: 1px solid #3d3d5c;
            overflow: hidden;
        }
        
        /* DataFrame itself */
        div[data-testid="stDataFrame"] > div {
            background-color: #1e1e2e !important;
        }
        
        /* Table headers */
        .stDataFrame thead tr th {
            background-color: #2d2d44 !important;
            color: #f59e0b !important;
            font-weight: 600;
            border-bottom: 2px solid #f59e0b !important;
            padding: 12px 8px;
        }
        
        /* Table body */
        .stDataFrame tbody tr td {
            background-color: #252541 !important;
            color: #e0e0e0 !important;
            border-bottom: 1px solid #3d3d5c !important;
            padding: 10px 8px;
        }
        
        /* Alternating row colors */
        .stDataFrame tbody tr:nth-child(even) td {
            background-color: #2a2a46 !important;
        }
        
        /* Hover effect on rows */
        .stDataFrame tbody tr:hover td {
            background-color: #2d2d50 !important;
        }
        
        /* ==================== TABS STYLING - DARK THEME ==================== */
        
        /* Tab list container */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            border-bottom: 2px solid #3d3d5c;
        }
        
        /* Individual tabs - Dark theme */
        .stTabs [data-baseweb="tab"] {
            background-color: #2d2d44;
            border-radius: 8px 8px 0 0;
            padding: 12px 24px;
            font-weight: 500;
            color: #b0b0c0;
            border: 1px solid #3d3d5c;
            border-bottom: none;
            transition: all 0.3s ease;
        }
        
        /* Tab hover effect */
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #34344d;
            color: #f59e0b;
        }
        
        /* Active/Selected tab - Amber gradient */
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white !important;
            border-color: #f59e0b;
            box-shadow: 0 -2px 8px rgba(245, 158, 11, 0.3);
        }
        
        /* Tab content area - Dark theme */
        .stTabs [data-baseweb="tab-panel"] {
            background-color: #1e1e2e;
            padding: 20px;
            border-radius: 0 8px 8px 8px;
            border: 1px solid #3d3d5c;
            border-top: none;
        }
        
        /* Make sure content inside tabs is visible */
        .stTabs [data-baseweb="tab-panel"] * {
            color: #e0e0e0;
        }
        
        /* ==================== SQL EXPANDER ==================== */
        
        /* Expander header */
        .streamlit-expanderHeader {
            background-color: #2d2d44;
            color: #f59e0b;
            border: 1px solid #3d3d5c;
            border-radius: 8px;
            padding: 12px 16px;
            font-weight: 600;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #34344d;
            border-color: #f59e0b;
        }
        
        /* Expander content */
        .streamlit-expanderContent {
            background-color: #1e1e2e;
            border: 1px solid #3d3d5c;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }
        
        /* Code block inside expander */
        .streamlit-expanderContent pre {
            background-color: #252541 !important;
            color: #e0e0e0 !important;
            border: 1px solid #3d3d5c;
            border-radius: 6px;
            padding: 16px;
        }
        
        .streamlit-expanderContent code {
            color: #86efac !important;
        }
        
        /* ==================== METRICS ==================== */
        
        /* Metric container */
        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        /* Metric label */
        div[data-testid="stMetricLabel"] {
            color: #5a5a5a;
            font-weight: 600;
        }
        
        /* Metric value */
        div[data-testid="stMetricValue"] {
            color: #f59e0b;
            font-size: 32px;
            font-weight: 700;
        }
        
        /* ==================== BUTTONS ==================== */
        
        /* Suggestion buttons */
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            background-color: white;
            color: #2c3e50;
            padding: 10px 20px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            border-color: #f59e0b;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }
        
        /* Secondary button type */
        .stButton > button[kind="secondary"] {
            background-color: #f8f9fa;
            border: 1px solid #d0d0d0;
        }
        
        /* ==================== LOADING SPINNER ==================== */
        
        .stSpinner > div {
            border-color: #f59e0b transparent transparent transparent;
        }
        
        /* ==================== CHARTS - DARK THEME ==================== */
        
        /* Chart container */
        .stPlotlyChart, .js-plotly-plot {
            background-color: #252541;
            border-radius: 8px;
            border: 1px solid #3d3d5c;
            padding: 10px;
        }
        
        /* Line and bar charts - Dark theme */
        .stLineChart, .stBarChart {
            background-color: #252541;
            border-radius: 8px;
            border: 1px solid #3d3d5c;
            padding: 15px;
        }
        
        /* Chart canvas */
        .stLineChart canvas, .stBarChart canvas {
            background-color: #252541 !important;
        }
        
        /* ==================== ALERTS ==================== */
        
        /* Warning messages */
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .stWarning {
            background-color: #fff3cd;
            border-left-color: #f59e0b;
            color: #856404;
        }
        
        .stError {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        
        .stSuccess {
            background-color: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        
        .stInfo {
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
            color: #0c5460;
        }
        
        /* ==================== SCROLLBAR ==================== */
        
        /* Custom scrollbar for data tables */
        .stDataFrame ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
            background-color: #2d2d44;
        }
        
        .stDataFrame ::-webkit-scrollbar-thumb {
            background-color: #f59e0b;
            border-radius: 4px;
        }
        
        .stDataFrame ::-webkit-scrollbar-thumb:hover {
            background-color: #d97706;
        }
    </style>
    """, unsafe_allow_html=True)


def send_message(prompt: str) -> Dict[str, Any]:
    """Calls the Snowflake Cortex Analyst REST API and returns the response"""
    try:
        request_body = {
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }],
            "semantic_view": f"{os.getenv('DATABASE')}.{os.getenv('SCHEMA')}.{os.getenv('SEMANTIC_VIEW')}"
        }

        resp = requests.post(
            url=f"https://{os.getenv('HOST')}/api/v2/cortex/analyst/message",
            json=request_body,
            headers={
                "Authorization": f'Snowflake Token="{st.session_state.CONN.rest.token}"',
                "Content-Type": "application/json",
            },
            timeout=30
        )

        request_id = resp.headers.get("X-Snowflake-Request-Id")

        if resp.status_code < 400:
            return {**resp.json(), "request_id": request_id}
        else:
            raise Exception(
                f"Failed request (id: {request_id}) with status {resp.status_code}: {resp.text}"
            )
    except requests.exceptions.Timeout:
        raise Exception(
            "Request timed out. Please try again with a simpler query.")
    except Exception as e:
        raise Exception(f"Error communicating with Cortex Analyst: {str(e)}")


def display_content(content: List[Dict[str, str]], role: str) -> None:
    """Displays content within appropriate chat message container"""
    with st.chat_message(role):
        for item in content:
            if item["type"] == "text":
                st.markdown(item["text"])

            elif item["type"] == "suggestions":
                st.markdown("**💡 Suggested follow-up questions:**")
                for suggestion in item.get("suggestions", []):
                    if st.button(f"➤ {suggestion}", key=f"suggestion_{hash(suggestion)}"):
                        process_message(prompt=suggestion)
                        st.rerun()

            elif item["type"] == "sql":
                with st.expander("📊 View SQL Query", expanded=False):
                    st.code(item["statement"], language="sql")

                with st.spinner("🔄 Executing query..."):
                    try:
                        # Set row limits
                        MAX_DISPLAY_ROWS = 1000  # Maximum rows to display
                        MAX_CHART_ROWS = 100     # Maximum rows for charts

                        df = pd.read_sql(
                            item["statement"], st.session_state.CONN)

                        total_rows = len(df)

                        if df.empty:
                            st.warning("Query returned no results.")

                        elif len(df.index) == 1 and len(df.columns) == 1:
                            # Single value result - display as metric
                            value = df.iloc[0, 0]
                            st.metric(
                                label=df.columns[0],
                                value=f"{value:,.2f}" if isinstance(
                                    value, (int, float)) else value
                            )

                        else:
                            # Show warning if results are large
                            if total_rows > MAX_DISPLAY_ROWS:
                                st.warning(f"""
                                ⚠️ **Large Result Set Detected!**  
                                Query returned **{total_rows:,} rows**. Displaying first **{MAX_DISPLAY_ROWS:,} rows** only.  
                                💡 **Tip:** Refine your question to get more specific results.
                                """)
                                df_display = df.head(MAX_DISPLAY_ROWS)
                            else:
                                df_display = df

                            # Info banner showing row count
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.info(
                                    f"📊 Showing **{len(df_display):,}** of **{total_rows:,}** rows")
                            with col2:
                                # Download button for full dataset
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=csv,
                                    file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    key=f"download_{hash(item['statement'])}"
                                )
                            with col3:
                                if total_rows > MAX_DISPLAY_ROWS:
                                    st.caption(
                                        f"💾 Full dataset: {total_rows:,} rows")

                            # Multiple rows/columns - show in tabs
                            if len(df_display.index) > 1:
                                tab1, tab2, tab3 = st.tabs(
                                    ["📋 Data Table", "📈 Line Chart", "📊 Bar Chart"])

                                with tab1:
                                    # Pagination for table
                                    if total_rows > 50:
                                        st.caption(
                                            "💡 Scroll horizontally/vertically to see all data")

                                    st.dataframe(
                                        df_display,
                                        width='stretch',
                                        height=min(
                                            600, (len(df_display) + 1) * 35)
                                    )

                                # Charts - only show if reasonable number of rows
                                if len(df.columns) > 1:
                                    if total_rows > MAX_CHART_ROWS:
                                        df_chart = df.head(
                                            MAX_CHART_ROWS).set_index(df.columns[0])
                                        chart_warning = f"⚠️ Displaying first {MAX_CHART_ROWS} rows for better visualization"
                                    else:
                                        df_chart = df.set_index(df.columns[0])
                                        chart_warning = None

                                    with tab2:
                                        if chart_warning:
                                            st.caption(chart_warning)
                                        st.line_chart(
                                            df_chart, width='stretch')

                                    with tab3:
                                        if chart_warning:
                                            st.caption(chart_warning)
                                        st.bar_chart(df_chart, width='stretch')
                            else:
                                st.dataframe(df_display, width='stretch')

                    except Exception as e:
                        st.error(f"❌ Error executing SQL: {str(e)}")


def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat"""
    # Add user message to session state
    st.session_state.messages.append({
        "role": "user",
        "content": [{"type": "text", "text": prompt}]
    })

    # Get assistant response
    try:
        with st.spinner("🤔 AI is thinking..."):
            response = send_message(prompt=prompt)
            content = response["message"]["content"]

        # Add assistant message to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": content
        })

    except Exception as e:
        st.error(f"❌ {str(e)}")
        # Add error message to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": [{"type": "text", "text": f"Sorry, I encountered an error: {str(e)}"}]
        })


def cortex_analyst():
    """Main Cortex Analyst chat interface"""

    # Load custom CSS
    load_css()

    # Page header
    st.title("🤖 AI Data Assistant")
    st.markdown("Ask questions about your retail data in natural language")

    # Establish Snowflake connection
    try:
        if "CONN" not in st.session_state:
            st.session_state.CONN = init_connection()
    except Exception as e:
        st.error(f"❌ Failed to connect to Snowflake: {e}")
        st.stop()

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Predefined suggestion prompts
    SUGGESTIONS = [
        "What are the top 10 products by revenue this quarter?",
        "Show me sales trends for the last 6 months",
        "Which customer segment generates the most revenue?",
        "Compare our prices with competitor benchmarks",
        "What is the average order value by payment method?",
        "Show inventory status for products out of stock",
    ]

    # Header actions
    col1, col2, col3 = st.columns([6, 1, 1])

    with col2:
        if st.button("📋 Examples", width='stretch'):
            st.session_state.show_examples = not st.session_state.get(
                'show_examples', False)

    with col3:
        if st.button("🗑️ Clear", width='stretch'):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # Show examples if toggled
    if st.session_state.get('show_examples', False) or len(st.session_state.messages) == 0:
        st.markdown("### 💡 Try asking questions like:")

        cols = st.columns(2)
        for idx, suggestion in enumerate(SUGGESTIONS):
            with cols[idx % 2]:
                if st.button(
                    suggestion,
                    key=f"suggestion_{idx}",
                    width='stretch',
                    type="secondary"
                ):
                    st.session_state.show_examples = False
                    process_message(prompt=suggestion)
                    st.rerun()

        st.markdown("---")

    # Display chat history
    for message in st.session_state.messages:
        display_content(content=message["content"], role=message["role"])

    # Chat input (always at bottom)
    if user_input := st.chat_input("💬 Ask me anything about your retail data..."):
        st.session_state.show_examples = False
        process_message(prompt=user_input)
        st.rerun()

    # Footer with disclaimer
    st.markdown("---")
    st.caption("⚠️ **AI Disclaimer:** Responses are AI-generated. Please verify important information before making business decisions.")
    st.caption(
        f"🕐 Session started: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
