import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any
import yaml
import os
from datetime import datetime, timedelta

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.warning(f"Config file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        st.error(f"Error parsing config file: {str(e)}")
        return {}

def format_number(number: float, format_type: str = "standard") -> str:
    """
    Format numbers for display
    
    Args:
        number: Number to format
        format_type: Type of formatting (standard, currency, percentage)
        
    Returns:
        Formatted string
    """
    if format_type == "currency":
        return f"${number:,.2f}"
    elif format_type == "percentage":
        return f"{number:.1%}"
    elif format_type == "standard":
        if abs(number) >= 1_000_000:
            return f"{number/1_000_000:.1f}M"
        elif abs(number) >= 1_000:
            return f"{number/1_000:.1f}K"
        else:
            return f"{number:,.0f}"
    return str(number)

def create_metric_cards(metrics: Dict[str, Dict[str, Any]], cols: int = 4):
    """
    Create metric cards in columns
    
    Args:
        metrics: Dictionary of metric data
        cols: Number of columns
    """
    columns = st.columns(cols)
    
    for i, (key, data) in enumerate(metrics.items()):
        with columns[i % cols]:
            st.metric(
                label=data.get('label', key),
                value=data.get('value', 0),
                delta=data.get('delta', None)
            )

def create_download_button(data: pd.DataFrame, filename: str, file_format: str = "csv"):
    """
    Create a download button for data
    
    Args:
        data: DataFrame to download
        filename: Name of the file
        file_format: Format (csv, json, excel)
    """
    if file_format == "csv":
        csv = data.to_csv(index=False)
        st.download_button(
            label=f"Download {filename}.csv",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )
    elif file_format == "json":
        json_str = data.to_json(orient='records', indent=2)
        st.download_button(
            label=f"Download {filename}.json",
            data=json_str,
            file_name=f"{filename}.json",
            mime="application/json"
        )
    elif file_format == "excel":
        # Note: This requires openpyxl or xlsxwriter
        buffer = pd.ExcelWriter(f"{filename}.xlsx", engine='xlsxwriter')
        data.to_excel(buffer, index=False)
        buffer.close()

def create_sidebar_filters(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    """
    Create sidebar filters for DataFrame columns
    
    Args:
        df: DataFrame to create filters for
        columns: List of column names to create filters for
        
    Returns:
        Dictionary of filter values
    """
    filters = {}
    
    st.sidebar.header("Filters")
    
    for column in columns:
        if column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                min_val = float(df[column].min())
                max_val = float(df[column].max())
                filters[column] = st.sidebar.slider(
                    f"{column}",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val)
                )
            elif df[column].dtype == 'object':
                unique_values = df[column].unique().tolist()
                filters[column] = st.sidebar.multiselect(
                    f"{column}",
                    options=unique_values,
                    default=unique_values
                )
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                min_date = df[column].min().date()
                max_date = df[column].max().date()
                filters[column] = st.sidebar.date_input(
                    f"{column}",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
    
    return filters

def show_dataframe_info(df: pd.DataFrame):
    """
    Display DataFrame information
    
    Args:
        df: DataFrame to analyze
    """
    with st.expander("📊 Dataset Information"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        st.subheader("Column Information")
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes,
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum(),
            'Unique Values': df.nunique()
        })
        st.dataframe(info_df, use_container_width=True)

def add_custom_css():
    """Add custom CSS styling"""
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
    
    .stSidebar > div {
        background-color: #f8f9fa;
    }
    
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)

def create_progress_bar(current: int, total: int, text: str = "Progress"):
    """
    Create a progress bar
    
    Args:
        current: Current progress value
        total: Total value
        text: Progress text
    """
    progress = current / total if total > 0 else 0
    st.progress(progress)
    st.text(f"{text}: {current}/{total} ({progress:.1%})")

def validate_uploaded_file(uploaded_file, allowed_types: List[str] = None) -> bool:
    """
    Validate uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        allowed_types: List of allowed file extensions
        
    Returns:
        Boolean indicating if file is valid
    """
    if uploaded_file is None:
        return False
    
    if allowed_types:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in allowed_types:
            st.error(f"File type not allowed. Allowed types: {', '.join(allowed_types)}")
            return False
    
    return True
