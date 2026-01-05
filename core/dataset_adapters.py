from typing import Optional

import pandas as pd


def _canon(name: str) -> str:
    cleaned = str(name).strip().lstrip("\ufeff")
    return "".join(ch for ch in cleaned.lower() if ch.isalnum())


def _to_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")




def normalize_gnc_order_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize GnC order line dataset to canonical columns and numeric types.
    """
    rename_map = {}
    canon_map = {
        "itemname": "item_name",
        "description": "description",
        "remark1": "remark_1",
        "qty": "qty",
        "unitpriceusd": "unit_price/usd",
        "amount": "amount",
    }

    for col in df.columns:
        canon = _canon(col)
        if canon in canon_map:
            rename_map[col] = canon_map[canon]

    df_norm = df.rename(columns=rename_map).copy()

    if "qty" in df_norm.columns:
        df_norm["qty"] = _to_numeric(df_norm["qty"])

    if "unit_price/usd" in df_norm.columns:
        df_norm["unit_price/usd"] = _to_numeric(df_norm["unit_price/usd"])

    if "amount" in df_norm.columns:
        df_norm["amount"] = _to_numeric(df_norm["amount"])

    return df_norm


def normalize_df_for_example(df: pd.DataFrame, example_key: Optional[str]) -> Optional[pd.DataFrame]:
    if example_key == "ecommerce_gnc_order":
        return normalize_gnc_order_df(df)
    return None
