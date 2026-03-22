"""Feature engineering for Mule account detection.

Reads cleaned sheets from data/mule_data_cleaned.xlsx, creates
engineered features and flags per the 5W1H rules, and writes a
feature-rich transactions sheet to data/mule_data_features.xlsx.

Usage: python scripts/feature_engineering.py
"""

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
    
    # แปลง Timestamp ให้ชัวร์ก่อนคำนวณ
    tx['transaction_timestamp'] = pd.to_datetime(tx['transaction_timestamp'], errors='coerce')
    
    # --- 1. Merge Account Data ---
    # ดึงข้อมูลจาก dim_accounts มาประกอบ (เฉพาะคอลัมน์ที่จำเป็น)
    acct_lookup = dim_accounts[['account_id', 'avg_tx_vol_last_3m', 'is_mule_label', 'mule_type']].copy()
    tx = tx.merge(acct_lookup, how='left', left_on='sender_account_id', right_on='account_id')

    # --- 2. Dormancy Spike (WHAT) ---
    tx['avg_tx_vol_last_3m_safe'] = tx['avg_tx_vol_last_3m'].replace({0: 1}).fillna(1)
    tx['spike_ratio'] = tx['amount'] / tx['avg_tx_vol_last_3m_safe']
    tx['is_dormancy_spike'] = tx['spike_ratio'] > 5.0

    # --- 3. Zero-Balance Cashout (WHY) ---
    # เช็กว่าหลังโอน เงินเหลือติดบัญชีน้อยกว่า 2% ของยอดที่โอนไปหรือไม่
    tx['is_zero_balance_cashout'] = (tx['sender_balance_after'] / tx['amount'].replace({0: np.nan})) < 0.02
    tx['is_zero_balance_cashout'] = tx['is_zero_balance_cashout'].fillna(False)

    # --- 4. Shared Device & IP (WHERE) ---
    # นับจำนวนบัญชีที่ไม่ซ้ำกัน ต่อ 1 Device
    device_map = tx.groupby('device_id')['sender_account_id'].nunique()
    tx['distinct_accounts_per_device'] = tx['device_id'].map(device_map).fillna(0)
    
    # นับจำนวนบัญชีที่ไม่ซ้ำกัน ต่อ 1 IP
    ip_map = tx.groupby('ip_address')['sender_account_id'].nunique()
    tx['distinct_accounts_per_ip'] = tx['ip_address'].map(ip_map).fillna(0)
    
    tx['is_shared_device'] = (tx['distinct_accounts_per_device'] > 3) | (tx['distinct_accounts_per_ip'] > 3)

    # --- 5. Dwell Time & Pass-through (WHEN) ---
    # ค้นหาเวลาที่เงินเข้าบัญชีนี้ล่าสุด (ไม่ว่าจะโอนเข้าหรือโอนออก) 
    # เพื่อดูว่าเงินแช่อยู่ในบัญชีนานแค่ไหนก่อนจะถูกโอนออกครั้งนี้
    tx = tx.sort_values(['sender_account_id', 'transaction_timestamp'])
    
    # สร้างคอลัมน์เวลาของรายการก่อนหน้าในบัญชีเดียวกัน
    tx['prev_tx_timestamp'] = tx.groupby('sender_account_id')['transaction_timestamp'].shift(1)
    
    # คำนวณส่วนต่างเวลาเป็นนาที
    tx['dwell_time_mins'] = (tx['transaction_timestamp'] - tx['prev_tx_timestamp']).dt.total_seconds() / 60.0
    
    # บัญชีม้ามักจะโอนออกไวมาก (Pass-through)
    tx['is_pass_through'] = (tx['dwell_time_mins'] < 5.0) & (tx['dwell_time_mins'].notna())

    # ลบคอลัมน์ขยะออก
    if 'account_id' in tx.columns:
        tx = tx.drop(columns=['account_id', 'avg_tx_vol_last_3m_safe'])

    # เปลี่ยนค่าว่างใน mule_type ให้เป็น "None" หรือ "Normal"
    tx['mule_type'] = tx['mule_type'].fillna('None')

    # (แถม) ถ้าอยากให้ is_mule_label ดูง่ายขึ้น เปลี่ยน NaN เป็น False
    tx['is_mule_label'] = tx['is_mule_label'].fillna(False)

    return tx


def main():
    sheets = safe_read_sheets(INPUT_FILE)

    # Expecting these sheet names
    expected = ['dim_customers', 'dim_accounts', 'dim_devices', 'fact_transactions']
    for name in expected:
        if name not in sheets:
            print(f"Warning: expected sheet '{name}' not found in {INPUT_FILE}")

    fact = sheets.get('fact_transactions', pd.DataFrame())
    dim_accounts = sheets.get('dim_accounts', pd.DataFrame())

    print(f"Read fact_transactions rows={len(fact)}, dim_accounts rows={len(dim_accounts)}")

    features = engineer_features(fact, dim_accounts)

    # Write to output Excel with a single sheet
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        features.to_excel(writer, sheet_name='fact_transactions_features', index=False)

    print(f"Feature file written to: {OUTPUT_FILE}; rows={len(features)}")


if __name__ == '__main__':
    main()
