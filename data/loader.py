import pandas as pd

def load_sigint_csv(path, time_col="time"):
    def dedup_columns(df):
        counts = {}
        new_cols = []
        for col in df.columns:
            if col in counts:
                counts[col] += 1
                new_cols.append(f"{col}.{counts[col]}")
            else:
                counts[col] = 0
                new_cols.append(col)
        df.columns = new_cols
        return df

    df = pd.read_csv(path)
    df = dedup_columns(df)

    # Choose the first column that starts with the expected time_col name
    time_candidates = [col for col in df.columns if col.startswith(time_col)]
    if not time_candidates:
        raise ValueError(f"No column starting with '{time_col}' found in: {df.columns.tolist()}")

    df[time_candidates[0]] = pd.to_datetime(df[time_candidates[0]])

    return df
