"""
Centralized database connection module for Snowflake
Reduces code duplication and improves maintainability
"""
import streamlit as st
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


@st.cache_resource
def init_connection():
    """Initialize and cache Snowflake connection"""
    try:
        return snowflake.connector.connect(
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            account=os.getenv("ACCOUNT"),
            warehouse=os.getenv("WAREHOUSE"),
            database=os.getenv("DATABASE"),
            schema=os.getenv("SCHEMA")
        )
    except Exception as e:
        st.error(f"❌ Error connecting to Snowflake: {e}")
        st.stop()


@st.cache_data(ttl=3600)
def run_query(query, params=None):
    """Execute query and return results as DataFrame with 1-hour cache"""
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            results = cur.fetchall()
            return pd.DataFrame(results, columns=columns)
    except Exception as e:
        st.error(f"❌ Error executing query: {e}")
        return None


def get_filter_options(table, column, order_by=None):
    """Helper function to get distinct filter options"""
    order_clause = f"ORDER BY {order_by if order_by else column}"
    query = f"SELECT DISTINCT {column} FROM {table} {order_clause};"
    df = run_query(query)
    if df is not None and not df.empty:
        return df[column].tolist()
    return []
