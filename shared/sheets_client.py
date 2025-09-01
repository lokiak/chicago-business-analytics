
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
