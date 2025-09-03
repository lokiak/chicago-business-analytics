"""
Utility functions for Chicago SMB Market Radar analysis notebooks.

This module provides reusable functions for data analysis, visualization,
and business intelligence tasks across all notebooks.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def week_start(date):
    """Get the Monday of the week for a given date."""
    return date - timedelta(days=date.weekday())

def load_sheet_data(sheet, worksheet_name: str, parse_dates: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Load data from a Google Sheets worksheet into a pandas DataFrame.

    Args:
        sheet: Google Sheets object
        worksheet_name: Name of the worksheet
        parse_dates: List of column names to parse as dates

    Returns:
        pandas.DataFrame: Loaded data
    """
    try:
        ws = sheet.worksheet(worksheet_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data)

        # Parse dates if specified
        if parse_dates:
            for col in parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

        print(f"✅ Loaded {len(df)} rows from '{worksheet_name}'")
        return df

    except Exception as e:
        print(f"❌ Error loading '{worksheet_name}': {e}")
        return pd.DataFrame()

def get_data_summary(df: pd.DataFrame, name: str) -> None:
    """
    Print a comprehensive summary of the loaded dataset.

    Args:
        df: pandas.DataFrame
        name: Dataset name for display
    """
    print(f"\n📊 {name} Dataset Summary")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    if not df.empty:
        print(f"\n📋 Column Information:")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            print(f"   {col}: {dtype} ({null_count:,} nulls, {null_pct:.1f}%)")

    print("\n" + "="*50)

def assess_data_quality(df: pd.DataFrame, name: str) -> None:
    """
    Perform comprehensive data quality assessment.

    Args:
        df: pandas.DataFrame
        name: Dataset name for display
    """
    print(f"\n🔍 Data Quality Assessment: {name}")
    print("="*50)

    if df.empty:
        print("❌ Dataset is empty")
        return

    # Basic statistics
    print(f"📊 Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

    # Missing data analysis
    missing_data = df.isnull().sum()
    missing_pct = (missing_data / len(df)) * 100

    print(f"\n📋 Missing Data Summary:")
    for col in df.columns:
        if missing_data[col] > 0:
            print(f"   {col}: {missing_data[col]:,} ({missing_pct[col]:.1f}%)")

    # Duplicate analysis
    duplicates = df.duplicated().sum()
    print(f"\n🔄 Duplicates: {duplicates:,} ({duplicates/len(df)*100:.1f}%)")

    # Date range analysis (if date columns exist)
    date_cols = df.select_dtypes(include=['datetime64[ns]']).columns
    if len(date_cols) > 0:
        print(f"\n📅 Date Range Analysis:")
        for col in date_cols:
            if not df[col].isnull().all():
                min_date = df[col].min()
                max_date = df[col].max()
                print(f"   {col}: {min_date} to {max_date}")

    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(f"\n🔢 Numeric Columns Summary:")
        for col in numeric_cols:
            if not df[col].isnull().all():
                mean_val = df[col].mean()
                std_val = df[col].std()
                print(f"   {col}: mean={mean_val:.2f}, std={std_val:.2f}")

    print("\n" + "="*50)

def create_time_series_plot(df: pd.DataFrame, date_col: str, value_col: str,
                           group_col: Optional[str] = None, title: str = "Time Series Plot") -> None:
    """
    Create a time series plot for the given data.

    Args:
        df: pandas.DataFrame with time series data
        date_col: Name of the date column
        value_col: Name of the value column to plot
        group_col: Optional column to group by (for multiple lines)
        title: Plot title
    """
    plt.figure(figsize=(12, 6))

    if group_col and group_col in df.columns:
        # Multiple lines for different groups
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group]
            plt.plot(group_data[date_col], group_data[value_col],
                    label=group, marker='o', markersize=3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        # Single line
        plt.plot(df[date_col], df[value_col], marker='o', markersize=3)

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(date_col.replace('_', ' ').title())
    plt.ylabel(value_col.replace('_', ' ').title())
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def create_distribution_plot(df: pd.DataFrame, col: str, title: str = None,
                           top_n: int = 10) -> None:
    """
    Create a distribution plot for categorical data.

    Args:
        df: pandas.DataFrame
        col: Column name to plot
        title: Plot title
        top_n: Number of top categories to show
    """
    if title is None:
        title = f"Distribution of {col.replace('_', ' ').title()}"

    # Get top categories
    top_categories = df[col].value_counts().head(top_n)

    plt.figure(figsize=(12, 6))
    top_categories.plot(kind='bar')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(col.replace('_', ' ').title())
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def calculate_weekly_aggregations(df: pd.DataFrame, date_col: str,
                                group_cols: List[str], value_col: str = "count") -> pd.DataFrame:
    """
    Calculate weekly aggregations from daily data.

    Args:
        df: pandas.DataFrame with daily data
        date_col: Name of the date column
        group_cols: List of columns to group by
        value_col: Name of the value column to aggregate

    Returns:
        pandas.DataFrame: Weekly aggregated data
    """
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
    df_copy['week_start'] = df_copy[date_col].apply(week_start)

    # Group by week and other columns, sum the values
    weekly_df = df_copy.groupby(['week_start'] + group_cols, dropna=False, as_index=False)[value_col].sum()

    return weekly_df

def calculate_trend_metrics(df: pd.DataFrame, group_cols: List[str],
                          value_col: str, baseline_weeks: int = 13) -> pd.DataFrame:
    """
    Calculate trend metrics including rolling averages and momentum indices.

    Args:
        df: pandas.DataFrame with weekly data
        group_cols: List of columns to group by
        value_col: Name of the value column
        baseline_weeks: Number of weeks for baseline calculation

    Returns:
        pandas.DataFrame: Data with trend metrics added
    """
    df_copy = df.copy().sort_values('week_start')

    # Calculate rolling averages and standard deviations
    df_copy['avg_13w'] = (
        df_copy.groupby(group_cols)[value_col]
         .rolling(window=baseline_weeks, min_periods=1).mean()
         .reset_index(level=group_cols, drop=True)
    )

    df_copy['std_13w'] = (
        df_copy.groupby(group_cols)[value_col]
         .rolling(window=baseline_weeks, min_periods=1).std()
         .reset_index(level=group_cols, drop=True)
         .fillna(0.0)
    )

    # Calculate week-over-week change
    df_copy['wow'] = df_copy.groupby(group_cols)[value_col].pct_change().replace([np.inf, -np.inf], np.nan)

    # Calculate momentum index (z-score)
    df_copy['momentum_index'] = (df_copy[value_col] - df_copy['avg_13w']) / df_copy['std_13w'].replace(0, 1.0)

    return df_copy

def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str, value_col: str,
                  title: str = "Heatmap") -> None:
    """
    Create a heatmap visualization.

    Args:
        df: pandas.DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        value_col: Column for values
        title: Plot title
    """
    # Pivot the data for heatmap
    pivot_df = df.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc='sum')

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_df, annot=True, fmt='.0f', cmap='YlOrRd', cbar_kws={'label': value_col})
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(x_col.replace('_', ' ').title())
    plt.ylabel(y_col.replace('_', ' ').title())
    plt.tight_layout()
    plt.show()

def save_analysis_results(df: pd.DataFrame, filename: str, data_dir: str = '../data/processed') -> None:
    """
    Save analysis results to pickle file for later use.

    Args:
        df: pandas.DataFrame to save
        filename: Name of the file (without extension)
        data_dir: Directory to save the file
    """
    from pathlib import Path

    # Create directory if it doesn't exist
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    # Save the dataframe
    file_path = data_path / f"{filename}.pkl"
    df.to_pickle(file_path)
    print(f"✅ Analysis results saved to {file_path}")

def load_analysis_results(filename: str, data_dir: str = '../data/processed') -> pd.DataFrame:
    """
    Load analysis results from pickle file with enhanced compatibility handling.

    Args:
        filename: Name of the file (without extension)
        data_dir: Directory containing the file

    Returns:
        pandas.DataFrame: Loaded data
    """
    from pathlib import Path
    import sys
    import types

    file_path = Path(data_dir) / f"{filename}.pkl"

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return pd.DataFrame()

    try:
        # First, try normal loading
        df = pd.read_pickle(file_path)
        print(f"✅ Loaded analysis results from {file_path}")
        return df

    except (ModuleNotFoundError, AttributeError) as e:
        # Handle numpy compatibility issues
        if "numpy._core" in str(e) or "_core" in str(e):
            print(f"🔧 Applying numpy compatibility fix for {file_path}")

            try:
                # Apply numpy._core compatibility mapping
                import numpy as np
                if 'numpy._core' not in sys.modules:
                    core_module = types.ModuleType('numpy._core')
                    core_module.numeric = np.core.numeric
                    if hasattr(np.core, 'multiarray'):
                        core_module.multiarray = np.core.multiarray
                    if hasattr(np.core, 'umath'):
                        core_module.umath = np.core.umath

                    sys.modules['numpy._core'] = core_module
                    sys.modules['numpy._core.numeric'] = np.core.numeric
                    if hasattr(np.core, 'multiarray'):
                        sys.modules['numpy._core.multiarray'] = np.core.multiarray
                    if hasattr(np.core, 'umath'):
                        sys.modules['numpy._core.umath'] = np.core.umath

                # Try loading again with compatibility fix
                df = pd.read_pickle(file_path)
                print(f"✅ Loaded analysis results from {file_path} (with compatibility fix)")

                # Suggest refreshing the cache
                print(f"💡 Tip: Consider refreshing this cache file with: python scripts/refresh_pickle_cache.py")
                return df

            except Exception as fix_error:
                print(f"❌ Failed to load {file_path} even with compatibility fix: {fix_error}")
                return pd.DataFrame()
        else:
            print(f"❌ Failed to load {file_path}: {e}")
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ Unexpected error loading {file_path}: {e}")
        return pd.DataFrame()

def print_insights_summary(insights: Dict[str, any]) -> None:
    """
    Print a formatted summary of key insights.

    Args:
        insights: Dictionary of insights to display
    """
    print("\n" + "="*60)
    print("🔍 KEY INSIGHTS SUMMARY")
    print("="*60)

    for category, data in insights.items():
        print(f"\n📊 {category.upper()}")
        print("-" * 40)

        if isinstance(data, dict):
            for key, value in data.items():
                print(f"   {key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(f"   • {item}")
        else:
            print(f"   {data}")

    print("\n" + "="*60)
