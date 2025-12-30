"""
Main dashboard navigation and routing
Professional e-commerce analytics platform with dynamic dark theme
"""
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
from product_performance_metrics import product_performance_metrics
from sales_performance_metrics import sales_performance_metrics
from benchmarking_and_customer_insights import benchmarking_and_customer_insights
from cortex_analyst import cortex_analyst

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Retail Intelligence Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define color schemes for each dashboard
DASHBOARD_THEMES = {
    "Sales Performance": {
        "primary": "#10b981",  # Green
        "secondary": "#059669",
        "gradient": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "icon": "#86efac"
    },
    "Product Analytics": {
        "primary": "#3b82f6",  # Blue
        "secondary": "#2563eb",
        "gradient": "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
        "icon": "#93c5fd"
    },
    "Benchmarking & Insights": {
        "primary": "#8b5cf6",  # Purple
        "secondary": "#7c3aed",
        "gradient": "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)",
        "icon": "#c4b5fd"
    },
    "AI Assistant": {
        "primary": "#f59e0b",  # Amber
        "secondary": "#d97706",
        "gradient": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "icon": "#fcd34d"
    }
}

# Initialize session state for selected dashboard
if 'selected_dashboard' not in st.session_state:
    st.session_state.selected_dashboard = "Sales Performance"

# Get current theme
current_theme = DASHBOARD_THEMES[st.session_state.selected_dashboard]

# Custom CSS for professional dark theme
st.markdown(f"""
<style>
    /* ==================== SIDEBAR DARK THEME ==================== */
    
    /* Main sidebar background */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid #2d2d44;
    }}
    
    /* Sidebar content */
    section[data-testid="stSidebar"] > div {{
        background-color: transparent;
    }}
    
    /* Remove default sidebar styling */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {{
        background-color: transparent;
    }}
    
    /* Scrollbar for sidebar */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {{
        width: 8px;
        background-color: transparent;
    }}
    
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
        background-color: #3d3d5c;
        border-radius: 10px;
    }}
    
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {{
        background-color: #4d4d6c;
    }}
    
    /* Sidebar text elements */
    section[data-testid="stSidebar"] .element-container {{
        color: #e0e0e0;
    }}
    
    section[data-testid="stSidebar"] p {{
        color: #b0b0c0;
    }}
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
    }}
    
    /* Horizontal divider in sidebar */
    section[data-testid="stSidebar"] hr {{
        border-color: #2d2d44;
        margin: 15px 0;
    }}
    
    /* Sidebar expander */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {{
        background-color: #252541;
        color: #e0e0e0;
        border: 1px solid #3d3d5c;
        border-radius: 8px;
    }}
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {{
        background-color: #2d2d50;
        border-color: {current_theme['primary']};
    }}
    
    section[data-testid="stSidebar"] .streamlit-expanderContent {{
        background-color: #1e1e32;
        border: 1px solid #3d3d5c;
        border-top: none;
    }}
    
    /* ==================== MAIN CONTENT STYLING ==================== */
    
    /* Main metrics cards */
    div[data-testid="stMetricValue"] {{
        font-size: 28px;
        font-weight: 600;
        color: {current_theme['primary']};
    }}
    
    div[data-testid="stMetricDelta"] {{
        font-size: 16px;
    }}
    
    /* Headers */
    h1 {{
        color: {current_theme['primary']};
        font-weight: 700;
        margin-bottom: 20px;
    }}
    
    h2 {{
        color: #2c3e50;
        font-weight: 600;
        margin-top: 30px;
        padding-bottom: 8px;
        border-bottom: 3px solid {current_theme['primary']};
    }}
    
    h3 {{
        color: #34495e;
        font-weight: 600;
        margin-top: 25px;
    }}
    
    /* Dataframes */
    .dataframe {{
        font-size: 14px;
    }}
    
    /* Info boxes */
    .stAlert {{
        border-radius: 8px;
        border-left: 5px solid {current_theme['primary']};
    }}
    
    /* Success boxes */
    .stSuccess {{
        background-color: rgba(16, 185, 129, 0.1);
        border-left-color: #10b981;
    }}
    
    /* Warning boxes */
    .stWarning {{
        background-color: rgba(245, 158, 11, 0.1);
        border-left-color: #f59e0b;
    }}
    
    /* Error boxes */
    .stError {{
        background-color: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
    }}
    
    /* Info boxes */
    .stInfo {{
        background-color: rgba(59, 130, 246, 0.1);
        border-left-color: #3b82f6;
    }}
    
    /* Reduce whitespace */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 1rem;
        max-width: 95%;
    }}
    
    /* Buttons */
    .stButton>button {{
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    /* Primary button styling based on theme */
    .stButton>button[kind="primary"] {{
        background: {current_theme['gradient']};
        border: none;
        color: white;
    }}
    
    /* Selectbox */
    .stSelectbox {{
        margin-bottom: 10px;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {current_theme['gradient']};
        color: white;
    }}
    
    /* Plotly charts */
    .js-plotly-plot {{
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# Sidebar with enhanced dark theme navigation
with st.sidebar:
    # Logo/Title with dynamic color
    st.markdown(f"""
        <div style='text-align: center; padding: 20px 0; background: {current_theme['gradient']}; border-radius: 12px; margin-bottom: 20px;'>
            <h1 style='color: white; margin: 0; font-size: 42px;'>📊</h1>
            <h3 style='color: white; margin: 5px 0; font-weight: 600;'>Retail Intel Hub</h3>
            <p style='color: rgba(255,255,255,0.8); font-size: 12px; margin: 0;'>Business Intelligence Platform</p>
        </div>
    """, unsafe_allow_html=True)

    # Navigation menu with dynamic dark theme
    selection = option_menu(
        menu_title=None,
        options=["Sales Performance", "Product Analytics",
                 "Benchmarking & Insights", "AI Assistant"],
        icons=["graph-up-arrow", "box-seam", "bar-chart-line", "robot"],
        default_index=["Sales Performance", "Product Analytics",
                       "Benchmarking & Insights", "AI Assistant"].index(st.session_state.selected_dashboard),
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent"
            },
            "icon": {
                "color": current_theme['icon'],
                "font-size": "20px"
            },
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "4px 0",
                "padding": "14px 18px",
                "border-radius": "10px",
                "color": "#b0b0c0",
                "background-color": "transparent",
                "transition": "all 0.3s ease",
                "--hover-color": "#252541",
            },
            "nav-link-selected": {
                "background": current_theme['gradient'],
                "color": "white",
                "font-weight": "600",
                "box-shadow": f"0 4px 12px {current_theme['primary']}40",
                "border": "none",
            },
        }
    )

    # Update session state
    if selection != st.session_state.selected_dashboard:
        st.session_state.selected_dashboard = selection
        st.rerun()

    st.markdown("<hr style='margin: 20px 0; border-color: #2d2d44;'>",
                unsafe_allow_html=True)

    # Dashboard info with dark theme
    st.markdown(f"""
        <div style='background-color: #252541; padding: 15px; border-radius: 10px; border: 1px solid #3d3d5c;'>
            <h3 style='color: {current_theme['primary']}; margin: 0 0 10px 0; font-size: 16px;'>📅 Dashboard Info</h3>
            <p style='color: #e0e0e0; margin: 5px 0; font-size: 13px;'><strong>Last Updated:</strong><br/>{datetime.now().strftime('%b %d, %Y at %I:%M %p')}</p>
            <p style='color: #e0e0e0; margin: 5px 0; font-size: 13px;'><strong>Data Refresh:</strong> Real-time</p>
            <p style='color: #e0e0e0; margin: 5px 0; font-size: 13px;'><strong>Coverage:</strong> Last 24 months</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 20px 0; border-color: #2d2d44;'>",
                unsafe_allow_html=True)

    # Quick stats or help with dark theme
    with st.expander("ℹ️ Need Help?"):
        st.markdown("""
        <div style='color: #e0e0e0;'>
            <p style='font-weight: 600; color: white; margin-bottom: 10px;'>Navigation Tips:</p>
            <ul style='line-height: 1.8;'>
                <li>Use filters to drill down into data</li>
                <li>Hover over charts for detailed info</li>
                <li>Click metrics to see trends</li>
                <li>Export data directly from tables</li>
            </ul>
        """, unsafe_allow_html=True)
        st.markdown("""
            <p style='font-weight: 600; color: white; margin: 15px 0 10px 0;'>Quick Actions:</p>
            <ul style='line-height: 1.8;'>
                <li>📊 View real-time dashboards</li>
                <li>🤖 Ask AI for insights</li>
                <li>📈 Track performance metrics</li>
                <li>💰 Monitor competitor pricing</li>
            </ul>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <hr style='border-color: #3d3d5c; margin: 15px 0;'/>
            """, unsafe_allow_html=True)
        st.markdown(f"""
            <p style='font-size: 12px; color: #888;'>
                <strong>Support:</strong> support@retail.com<br/>
                <strong>Version:</strong> 2.0.1
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Status indicator
    st.markdown(f"""
        <div style='margin-top: 20px; text-align: center;'>
            <div style='display: inline-flex; align-items: center; background-color: #252541; padding: 8px 16px; border-radius: 20px; border: 1px solid #3d3d5c;'>
                <div style='width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite;'></div>
                <span style='color: #10b981; font-size: 12px; font-weight: 600;'>LIVE</span>
            </div>
        </div>
        
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
        </style>
    """, unsafe_allow_html=True)

# Route to selected page
if selection == "Sales Performance":
    sales_performance_metrics()
elif selection == "Product Analytics":
    product_performance_metrics()
elif selection == "Benchmarking & Insights":
    benchmarking_and_customer_insights()
elif selection == "AI Assistant":
    cortex_analyst()

# Footer with theme color
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #7f8c8d; padding: 20px 0;'>
        <div style='display: inline-block; padding: 10px 20px; background: {current_theme['gradient']}; border-radius: 8px; margin-bottom: 10px;'>
            <small style='color: white; font-weight: 600;'>Powered by Snowflake & Streamlit</small>
        </div>
        <br/>
        <small>© 2025 Retail Intelligence Hub | Version 2.0</small>
    </div>
""", unsafe_allow_html=True)
