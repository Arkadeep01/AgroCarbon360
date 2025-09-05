# ml_models/pipelines/utils.py
import pandas as pd
import os
import re


def read_any_table(path: str, sheet_name=None, encoding: str = "utf-8"):
    """
    Reads a dataset whether it's CSV or Excel (.xls, .xlsx).
    Detects Excel content even if the extension is misleading (like .csv).
    """
    # Try Excel first (if file is actually a ZIP/OpenXML container)
    try:
        df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
        # If sheet_name is None and multiple sheets exist, take the first one
        if isinstance(df, dict):
            df = list(df.values())[0]
        return df
    except Exception:
        pass  # not Excel, continue

    ext = os.path.splitext(path)[-1].lower()

    if ext in [".csv", ".txt"]:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            for enc in ["latin1", "utf-16", "utf-8-sig"]:
                try:
                    return pd.read_csv(path, encoding=enc)
                except Exception:
                    continue
            raise
        except pd.errors.ParserError:
            # fallback for weird delimiters
            return pd.read_csv(path, sep=None, engine="python")

    raise ValueError(f"Unsupported or unreadable file format: {path}")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes column names: lowercase, underscores.
    """
    df = df.copy()
    df.columns = [re.sub(r"\s+", "_", str(c).strip().lower()) for c in df.columns]
    return df


def choose_target(df: pd.DataFrame, candidates) -> str | None:
    """
    Pick the first available target column from candidate list.
    """
    cols = set([c.lower() for c in df.columns])
    for c in candidates:
        if c.lower() in cols:
            return c.lower()
    for c in df.columns:
        if "ch4" in c.lower():
            return c
    return None


def summarize_df(df: pd.DataFrame, name="Dataset"):
    """
    Prints a quick summary of dataset.
    """
    print(f"\n=== {name} ===")
    print(f"Shape: {df.shape}")
    print("Columns:", df.columns.tolist()[:12], "..." if df.shape[1] > 12 else "")
    print("Missing values:", df.isnull().sum().sum())
    print("===================")
