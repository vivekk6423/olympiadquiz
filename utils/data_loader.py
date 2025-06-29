import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Dict, Any
import requests
import json

@st.cache_data(ttl=3600)
def load_csv_data(file_path: str) -> pd.DataFrame:
    """
    Load CSV data with caching
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        pandas DataFrame
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data with caching
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing JSON data
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading JSON: {str(e)}")
        return {}

@st.cache_data(ttl=900)
def fetch_api_data(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Fetch data from API with caching
    
    Args:
        url: API endpoint URL
        headers: Optional headers for the request
        
    Returns:
        Dictionary containing API response
    """
    try:
        response = requests.get(url, headers=headers or {}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching API data: {str(e)}")
        return {}

def generate_sample_data(rows: int = 100) -> pd.DataFrame:
    """
    Generate sample data for testing
    
    Args:
        rows: Number of rows to generate
        
    Returns:
        pandas DataFrame with sample data
    """
    np.random.seed(42)
    
    data = {
        'id': range(1, rows + 1),
        'date': pd.date_range('2024-01-01', periods=rows, freq='D'),
        'category': np.random.choice(['A', 'B', 'C', 'D'], rows),
        'value': np.random.normal(100, 25, rows),
        'count': np.random.poisson(10, rows),
        'is_active': np.random.choice([True, False], rows, p=[0.8, 0.2])
    }
    
    return pd.DataFrame(data)

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DataFrame by handling missing values and duplicates
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Remove duplicates
    df_clean = df.drop_duplicates()
    
    # Handle missing values
    for column in df_clean.columns:
        if df_clean[column].dtype in ['int64', 'float64']:
            df_clean[column] = df_clean[column].fillna(df_clean[column].median())
        else:
            df_clean[column] = df_clean[column].fillna('Unknown')
    
    return df_clean

def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to DataFrame
    
    Args:
        df: Input DataFrame
        filters: Dictionary of column names and filter values
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if column in filtered_df.columns:
            if isinstance(value, list):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            elif isinstance(value, tuple) and len(value) == 2:
                # Range filter
                filtered_df = filtered_df[
                    (filtered_df[column] >= value[0]) & 
                    (filtered_df[column] <= value[1])
                ]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df
