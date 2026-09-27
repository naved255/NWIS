from __future__ import annotations
from typing import Optional, Tuple
import pandas as pd
from sklearn.model_selection import train_test_split


def temporal_split(df: pd.DataFrame, time_column: Optional[str], test_size: float,
                   validation_size: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split chronologically into train/validation/test to prevent future leakage."""
    if time_column and time_column in df.columns:
        work = df.copy()
        work[time_column] = pd.to_datetime(work[time_column], errors="coerce", utc=True)
        if work[time_column].notna().all():
            work = work.sort_values(time_column).reset_index(drop=True)
            n = len(work)
            test_n = max(1, int(round(n * test_size)))
            val_n = max(1, int(round(n * validation_size)))
            if test_n + val_n >= n:
                raise ValueError("Dataset is too small for requested temporal validation/test sizes")
            return work.iloc[: n-test_n-val_n], work.iloc[n-test_n-val_n:n-test_n], work.iloc[n-test_n:]

    # Explicit fallback for data without usable time. This is reproducible but less robust.
    train, temp = train_test_split(df, test_size=test_size + validation_size, random_state=42, stratify=None)
    relative_test = test_size / (test_size + validation_size)
    val, test = train_test_split(temp, test_size=relative_test, random_state=42, stratify=None)
    return train, val, test
