from pathlib import Path
import pandas as pd
import numpy as np


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INPUT_FILE = DATA_DIR / "mule_data_cleaned.xlsx"
OUTPUT_FILE = DATA_DIR / "mule_data_features.xlsx"


def safe_read_sheets(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Cleaned input file not found: {path}")
    sheets = pd.read_excel(path, sheet_name=None)
    return sheets


def engineer_features(fact_tx: pd.DataFrame, dim_accounts: pd.DataFrame) -> pd.DataFrame:
    tx = fact_tx.copy()
    
    tx['transaction_timestamp'] = pd.to_datetime(tx['transaction_timestamp'], errors='coerce')
    
    acct_lookup = dim_accounts[['account_id', 'avg_tx_vol_last_3m', 'is_mule_label', 'mule_type']].copy()
    tx = tx.merge(acct_lookup, how='left', left_on='sender_account_id', right_on='account_id')

    tx['avg_tx_vol_last_3m_safe'] = tx['avg_tx_vol_last_3m'].replace({0: 1}).fillna(1)
    tx['spike_ratio'] = tx['amount'] / tx['avg_tx_vol_last_3m_safe']
    tx['is_dormancy_spike'] = tx['spike_ratio'] > 5.0

    tx['is_zero_balance_cashout'] = (tx['sender_balance_after'] / tx['amount'].replace({0: np.nan})) < 0.02
    tx['is_zero_balance_cashout'] = tx['is_zero_balance_cashout'].fillna(False)

    device_map = tx.groupby('device_id')['sender_account_id'].nunique()
    tx['distinct_accounts_per_device'] = tx['device_id'].map(device_map).fillna(0)
    
    ip_map = tx.groupby('ip_address')['sender_account_id'].nunique()
    tx['distinct_accounts_per_ip'] = tx['ip_address'].map(ip_map).fillna(0)
    
    tx['is_shared_device'] = (tx['distinct_accounts_per_device'] > 3) | (tx['distinct_accounts_per_ip'] > 3)

def engineer_features(fact_tx: pd.DataFrame, dim_accounts: pd.DataFrame) -> pd.DataFrame:
    tx = fact_tx.copy()
    
    tx['transaction_timestamp'] = pd.to_datetime(tx['transaction_timestamp'], errors='coerce')
    
    acct_lookup = dim_accounts[['account_id', 'avg_tx_vol_last_3m', 'is_mule_label', 'mule_type']].copy()
    tx = tx.merge(acct_lookup, how='left', left_on='sender_account_id', right_on='account_id')

    tx['avg_tx_vol_last_3m_safe'] = tx['avg_tx_vol_last_3m'].replace({0: 1}).fillna(1)
    tx['spike_ratio'] = tx['amount'] / tx['avg_tx_vol_last_3m_safe']
    tx['is_dormancy_spike'] = tx['spike_ratio'] > 5.0

    tx['is_zero_balance_cashout'] = (tx['sender_balance_after'] / tx['amount'].replace({0: np.nan})) < 0.02
    tx['is_zero_balance_cashout'] = tx['is_zero_balance_cashout'].fillna(False)

    device_map = tx.groupby('device_id')['sender_account_id'].nunique()
    tx['distinct_accounts_per_device'] = tx['device_id'].map(device_map).fillna(0)
    
    ip_map = tx.groupby('ip_address')['sender_account_id'].nunique()
    tx['distinct_accounts_per_ip'] = tx['ip_address'].map(ip_map).fillna(0)
    
    tx['is_shared_device'] = (tx['distinct_accounts_per_device'] > 3) | (tx['distinct_accounts_per_ip'] > 3)

    df_in = tx[['transaction_id', 'receiver_account_id', 'transaction_timestamp']].copy()
    df_in['tx_type'] = 'IN'
    df_in = df_in.rename(columns={'receiver_account_id': 'account_id'})

    df_out = tx[['transaction_id', 'sender_account_id', 'transaction_timestamp']].copy()
    df_out['tx_type'] = 'OUT'
    df_out = df_out.rename(columns={'sender_account_id': 'account_id'})

    ledger = pd.concat([df_in, df_out]).sort_values(['account_id', 'transaction_timestamp'])
    
    ledger['prev_timestamp'] = ledger.groupby('account_id')['transaction_timestamp'].shift(1)
    ledger['prev_tx_type'] = ledger.groupby('account_id')['tx_type'].shift(1)

    ledger['dwell_time_mins_calc'] = np.where(
        (ledger['tx_type'] == 'OUT') & (ledger['prev_tx_type'] == 'IN'),
        (ledger['transaction_timestamp'] - ledger['prev_timestamp']).dt.total_seconds() / 60.0,
        np.nan
    )

    out_ledger = ledger[ledger['tx_type'] == 'OUT'][['transaction_id', 'prev_timestamp', 'dwell_time_mins_calc']]
    tx = tx.merge(out_ledger, on='transaction_id', how='left')

    tx['prev_tx_timestamp'] = tx['prev_timestamp']
    tx['dwell_time_mins'] = tx['dwell_time_mins_calc']
    tx['is_pass_through'] = (tx['dwell_time_mins'] < 5.0) & (tx['dwell_time_mins'].notna())

    tx = tx.drop(columns=['prev_timestamp', 'dwell_time_mins_calc'])
    tx['mule_type'] = tx['mule_type'].fillna('None')
    tx['is_mule_label'] = tx['is_mule_label'].fillna(False)

    if 'account_id' in tx.columns:
        tx = tx.drop(columns=['account_id', 'avg_tx_vol_last_3m_safe'])

    return tx


def main():
    sheets = safe_read_sheets(INPUT_FILE)

    expected = ['dim_customers', 'dim_accounts', 'dim_devices', 'fact_transactions']
    for name in expected:
        if name not in sheets:
            print(f"Warning: expected sheet '{name}' not found in {INPUT_FILE}")

    fact = sheets.get('fact_transactions', pd.DataFrame())
    dim_accounts = sheets.get('dim_accounts', pd.DataFrame())

    print(f"Read fact_transactions rows={len(fact)}, dim_accounts rows={len(dim_accounts)}")

    features = engineer_features(fact, dim_accounts)

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        features.to_excel(writer, sheet_name='fact_transactions_features', index=False)

    print(f"Feature file written to: {OUTPUT_FILE}; rows={len(features)}")


if __name__ == '__main__':
    main()