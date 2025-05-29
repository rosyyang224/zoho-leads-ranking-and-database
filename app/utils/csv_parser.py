import pandas as pd

def parse_csv(file_stream):
    df = pd.read_csv(file_stream)
    df.columns = df.columns.str.strip()
    return df
