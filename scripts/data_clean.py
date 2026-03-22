"""Data cleansing script for the Mule account detection mock dataset.

Reads the 4 sheets from data/mule_account_mock_data.xlsx, applies
the cleansing rules specified in the project task, prints row
counts before/after, and writes cleaned sheets to
data/mule_data_cleaned.xlsx.

Usage: python scripts/data_clean.py
"""

from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INPUT_FILE = DATA_DIR / "mule_account_mock_data.xlsx"
OUTPUT_FILE = DATA_DIR / "mule_data_cleaned.xlsx"


def clean_dim_customers(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()

	initial = len(df)

	df['age'] = pd.to_numeric(df['age'], errors='coerce')

	if 'occupation' in df.columns:
		df['occupation'] = df['occupation'].fillna('Unknown')

	valid_mask = df['age'].between(0, 100) & df['age'].notna()
	if valid_mask.any():
		median_age = int(df.loc[valid_mask, 'age'].median())
	else:
		median_age = 30

	invalid_mask = ~valid_mask
	num_invalid = int(invalid_mask.sum())
	if num_invalid:
		df.loc[invalid_mask, 'age'] = median_age

	print(f"dim_customers: rows before={initial}, after={len(df)}; ages fixed={num_invalid}")
	return df


def clean_dim_accounts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    initial = len(df)
    
    for col in ['account_id', 'customer_id']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    def standardize_status(val):
        if pd.isna(val) or val == "":
            return "Active"
        s = str(val).strip().lower()
        if 'act' in s: return 'Active'
        if 'dorm' in s: return 'Dormant'
        if 'clos' in s: return 'Closed'
        return s.title()

    if 'account_status' in df.columns:
        df['account_status'] = df['account_status'].apply(standardize_status)

    print(f"dim_accounts: rows before={initial}, after={len(df)}")
    return df


def clean_dim_devices(df: pd.DataFrame) -> pd.DataFrame:
	print(f"dim_devices: rows before={len(df)}, after={len(df)}")
	return df.copy()


def clean_fact_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    initial_rows = len(df)

    id_cols = ['transaction_id', 'sender_account_id', 'receiver_account_id', 'device_id']
    for col in id_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown').astype(str).str.strip()

    if 'ip_address' in df.columns:
        df['ip_address'] = df['ip_address'].fillna('0.0.0.0').astype(str).str.strip()

    num_neg = 0
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        
        neg_mask = df['amount'] < 0
        num_neg = int(neg_mask.sum())
        if num_neg > 0:
            df.loc[neg_mask, 'amount'] = df.loc[neg_mask, 'amount'].abs()

    dropped_dupes = 0
    if 'transaction_id' in df.columns:
        before_drop = len(df)
        df = df.drop_duplicates(subset=['transaction_id'], keep='first')
        dropped_dupes = before_drop - len(df)

    print(f"--- Fact Transactions Cleansing Summary ---")
    print(f"Total rows: {initial_rows} -> {len(df)}")
    print(f"Negative amounts fixed: {num_neg}")
    print(f"Duplicate rows dropped: {dropped_dupes}")
    print(f"-------------------------------------------")
    
    return df


def main():
	if not INPUT_FILE.exists():
		raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

	sheets = pd.read_excel(INPUT_FILE, sheet_name=None)

	expected = ['dim_customers', 'dim_accounts', 'dim_devices', 'fact_transactions']

	cleaned = {}
	for name in expected:
		df = sheets.get(name)
		if df is None:
			print(f"Warning: sheet '{name}' not found in input; creating empty DataFrame.")
			df = pd.DataFrame()

		if name == 'dim_customers':
			cleaned[name] = clean_dim_customers(df)
		elif name == 'dim_accounts':
			cleaned[name] = clean_dim_accounts(df)
		elif name == 'dim_devices':
			cleaned[name] = clean_dim_devices(df)
		elif name == 'fact_transactions':
			cleaned[name] = clean_fact_transactions(df)
		else:
			cleaned[name] = df

	with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
		for name in expected:
			cleaned[name].to_excel(writer, sheet_name=name, index=False)

	print(f"Cleaned data written to: {OUTPUT_FILE}")


if __name__ == '__main__':
	main()

