import pandas as pd
import kagglehub, os, shutil
import numpy as np
from pathlib import Path

def from_root(*path_parts) -> Path:
    """Return path from project root"""
    return Path(__file__).resolve().parent.parent.joinpath(*path_parts)

if __name__ == "__main__":
    # Download dataset from Kaggle
    path = kagglehub.dataset_download("asaniczka/forex-exchange-rate-since-2004-updated-daily")
    print(f"Dataset extracted to: {path}")

    # Read the CSV
    csv_path = Path(path) / "daily_forex_rates.csv"
    df = pd.read_csv(csv_path, index_col=0).reset_index()

    # Transform data
    df['date'] = pd.to_datetime(df['date'])
    df['currency_name'] = np.where(df['currency']=='CNH', "Chinese Yuan",
                          np.where(df['currency']=='STN', "Sao Tomean Dobra",
                          np.where(df['currency']=='XCG', "Caribbean guilder",
                          np.where(df['currency']=='MRU', "Mauritanian Ouguiya", df['currency_name']))))
    df['options'] = df['currency_name'] + " (" + df['currency'] + ")"

    # Ensure output directory exists
    output_dir = from_root("streamlit", "assets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as pickle
    output_file = output_dir / "rates.pkl"
    df[['date','currency','base_currency','currency_name','options','exchange_rate']].to_pickle(output_file)
    print(f"✅ Pickle saved at {output_file}")

    # Delete Kaggle dataset folder
    shutil.rmtree(path)
    print(f"🗑️ Deleted folder: {path}")