
import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import set_frozen, format_cell_range, CellFormat, NumberFormat
import pandas as pd
from gspread.utils import rowcol_to_a1

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def open_sheet(sheet_id: str, creds_path: str):
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id)

def upsert_worksheet(sh, title: str, rows: int = 1000, cols: int = 26):
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=rows, cols=cols)
    return ws

def overwrite_with_dataframe(ws, df: pd.DataFrame):
    # Convert Timestamps to strings to avoid JSON serialization issues
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == 'datetime64[ns]' or 'datetime' in str(df_clean[col].dtype):
            df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')

    values = [list(df_clean.columns)] + df_clean.astype(object).where(pd.notnull(df_clean), "").values.tolist()
    ws.update(values)
    set_frozen(ws, rows=1, cols=0)
    headers = list(df_clean.columns)
    for idx, col in enumerate(headers, start=1):
        sample = df_clean[col].dropna().head(1)
        if not sample.empty:
            v = sample.iloc[0]
            if hasattr(v, "to_pydatetime") or "date" in col.lower() or "week" in col.lower():
                fmt = CellFormat(numberFormat=NumberFormat(type="DATE", pattern="yyyy-mm-dd"))
                format_cell_range(ws, f"{rowcol_to_a1(2, idx)}:{rowcol_to_a1(10000, idx)}", fmt)
            elif isinstance(v, (int, float)):
                fmt = CellFormat(numberFormat=NumberFormat(type="NUMBER", pattern="0.00"))
                format_cell_range(ws, f"{rowcol_to_a1(2, idx)}:{rowcol_to_a1(10000, idx)}", fmt)

def append_to_worksheet(ws, df: pd.DataFrame):
    """
    Append new data to existing worksheet without overwriting.
    Assumes the worksheet already has headers that match the DataFrame.
    """
    if df.empty:
        return

    # Clean the dataframe for sheets compatibility
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == 'datetime64[ns]' or 'datetime' in str(df_clean[col].dtype):
            df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')

    # Get current row count to know where to append
    current_data = ws.get_all_values()
    last_row = len(current_data)

    # Convert dataframe to list of lists (no headers since they exist)
    new_values = df_clean.astype(object).where(pd.notnull(df_clean), "").values.tolist()

    # Append the new data starting from the next empty row
    if new_values:
        ws.append_rows(new_values)
        print(f"✅ Appended {len(new_values)} new rows to worksheet")

def upsert_to_worksheet(ws, df: pd.DataFrame, key_columns: list):
    """
    Upsert data to worksheet - update existing records and insert new ones.

    Args:
        ws: gspread worksheet
        df: pandas DataFrame with new/updated data
        key_columns: list of column names that uniquely identify records
    """
    if df.empty:
        return

    print(f"🔄 Upserting data using key columns: {key_columns}")

    # Get existing data
    try:
        existing_data = ws.get_all_records()
        existing_df = pd.DataFrame(existing_data)
    except:
        # If worksheet is empty or has no data, just overwrite
        overwrite_with_dataframe(ws, df)
        return

    if existing_df.empty:
        overwrite_with_dataframe(ws, df)
        return

    # Clean both dataframes for comparison
    df_clean = df.copy()
    existing_clean = existing_df.copy()

    for col in df_clean.columns:
        if df_clean[col].dtype == 'datetime64[ns]' or 'datetime' in str(df_clean[col].dtype):
            df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')

    # Convert key columns to strings for reliable comparison
    for col in key_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str)
        if col in existing_clean.columns:
            existing_clean[col] = existing_clean[col].astype(str)

    # Create composite key for matching
    df_clean['_merge_key'] = df_clean[key_columns].apply(lambda x: '|'.join(x.astype(str)), axis=1)
    existing_clean['_merge_key'] = existing_clean[key_columns].apply(lambda x: '|'.join(x.astype(str)), axis=1)

    # Find new records (not in existing data)
    new_records = df_clean[~df_clean['_merge_key'].isin(existing_clean['_merge_key'])]

    # Find updated records (exist but may have changed)
    existing_keys = existing_clean['_merge_key'].tolist()
    updated_records = df_clean[df_clean['_merge_key'].isin(existing_keys)]

    # Remove merge key before saving
    new_records = new_records.drop(columns=['_merge_key'])
    updated_records = updated_records.drop(columns=['_merge_key'])
    existing_clean = existing_clean.drop(columns=['_merge_key'])

    print(f"   📊 Found {len(new_records)} new records")
    print(f"   📊 Found {len(updated_records)} potentially updated records")

    # For simplicity, we'll rebuild the entire sheet with merged data
    # More efficient implementations could update specific rows
    if not new_records.empty or not updated_records.empty:
        # Merge existing with updates, preferring new data
        merged_df = pd.concat([existing_clean, new_records], ignore_index=True)

        # Update existing records with new values
        for _, new_row in updated_records.iterrows():
            key_match = True
            for key_col in key_columns:
                if key_col in merged_df.columns:
                    mask = merged_df[key_col].astype(str) == str(new_row[key_col])
                    key_match = key_match & mask

            if key_match.any():
                # Update the matching row(s) with new data
                for col in new_row.index:
                    if col in merged_df.columns:
                        merged_df.loc[key_match, col] = new_row[col]

        # Write the merged data back
        overwrite_with_dataframe(ws, merged_df)
        print(f"✅ Upserted data successfully")
    else:
        print(f"ℹ️  No new or updated records found")

def get_date_filtered_data(df: pd.DataFrame, date_column: str, days_back: int) -> pd.DataFrame:
    """
    Filter dataframe to only include records from the last N days.
    Useful for incremental data loading.

    Args:
        df: pandas DataFrame
        date_column: name of date column to filter on
        days_back: number of days to look back

    Returns:
        Filtered DataFrame
    """
    from datetime import datetime, timedelta

    if date_column not in df.columns:
        print(f"⚠️  Date column '{date_column}' not found")
        return df

    # Convert to datetime if not already
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_back)

    # Filter data
    filtered_df = df_copy[df_copy[date_column] >= cutoff_date]

    print(f"📅 Filtered to {len(filtered_df)} records from last {days_back} days")
    return filtered_df
