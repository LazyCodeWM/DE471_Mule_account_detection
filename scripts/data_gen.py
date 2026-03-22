import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import faker
from faker import Faker
import os


######### Configuration #########
TOTAL_TX = 20000      
FRAUD_PCT = 0.05
FRAUD_TX = int(TOTAL_TX * FRAUD_PCT)  

NUM_ACCOUNTS = 6000   
NUM_CUSTOMERS = 5000  
NUM_DEVICES = 2400    

START_DATE = datetime.now() - timedelta(days=30)
END_DATE = datetime.now()

DIRTY_PCT = 0.04  
DIRTY_ROWS = max(1, int(TOTAL_TX * DIRTY_PCT))

fake = Faker()
random.seed(42)
np.random.seed(42)


######### Helpers #########

def random_timestamp_between(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def gen_ip():
    return fake.ipv4()


######### Build dim_customers #########

occupations = [
    "Teacher", "Engineer", "Unemployed", "Doctor", "Programmer",
    "Driver", "Sales", "Housewife", "Student",
]

normal_provinces = [
    "Bangkok", "Samut Prakan", "Nonthaburi", "Pathum Thani", "Phra Nakhon Si Ayutthaya", 
    "Ang Thong", "Lopburi", "Sing Buri", "Chai Nat", "Saraburi", "Chonburi", "Rayong", 
    "Chachoengsao", "Prachinburi", "Nakhon Nayok", "Nakhon Ratchasima", "Yasothon", 
    "Chaiyaphum", "Nong Bua Lam Phu", "Khon Kaen", "Udon Thani", "Maha Sarakham", 
    "Roi Et", "Kalasin", "Sakon Nakhon", "Lamphun", "Lampang", "Phrae", "Nakhon Sawan", 
    "Uthai Thani", "Kamphaeng Phet", "Sukhothai", "Phichit", "Phetchabun", "Suphan Buri", 
    "Nakhon Pathom", "Samut Sakhon", "Samut Songkhram", "Nakhon Si Thammarat", "Krabi", 
    "Phang Nga", "Phuket", "Surat Thani", "Trang", "Phatthalung", "Pattani"
]

high_risk_border_provinces = [
    "Ubon Ratchathani", "Si Sa Ket", "Surin", "Buri Ram", "Sa Kaeo", "Chanthaburi", "Trat",
    "Chiang Rai", "Phayao", "Nan", "Uttaradit", "Loei", "Nong Khai", "Bueng Kan", 
    "Nakhon Phanom", "Mukdahan", "Amnat Charoen", "Phitsanulok",
    "Mae Hong Son", "Chiang Mai", "Prachuap Khiri Khan", "Phetchaburi", "Ratchaburi", 
    "Kanchanaburi", "Tak", "Ranong", "Chumphon",
    "Satun", "Songkhla", "Yala", "Narathiwat"
]

rest_prob = 0.70
other_prob = rest_prob / (len(normal_provinces) - 1)
province_weights = [0.30] + [other_prob] * (len(normal_provinces) - 1)

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    age = int(np.random.normal(36, 10))
    if random.random() < 0.01:
        age = random.choice([-5, 150])

    cust = {
        "customer_id": f"C{100000 + i}",
        "age": age,
        "occupation": random.choice(occupations),
        "risk_segment": random.choice(["Low", "Medium", "High"]),
        "kyc_status": random.choice(["Verified", "Unverified", "Pending"]),
        "registered_province": np.random.choice(normal_provinces, p=province_weights),
    }
    customers.append(cust)

dim_customers = pd.DataFrame(customers)


######### Build dim_accounts #########

accounts = []
account_balances = {}

for i in range(1, NUM_ACCOUNTS + 1):
    customer = dim_customers.sample(1).iloc[0]
    account_id = f"A{200000 + i}"
    account_age_days = int(abs(np.random.exponential(365)))
    avg_tx_vol = float(max(0, np.random.lognormal(7, 1)))
    balance = float(max(0, np.random.normal(10000, 20000)))

    acc = {
        "account_id": account_id,
        "customer_id": customer["customer_id"],
        "account_status": random.choice(["Active", "Closed", "Dormant"]),
        "account_age_days": account_age_days,
        "avg_tx_vol_last_3m": round(avg_tx_vol, 2),
        "is_mule_label": False,  
        "mule_type": "None",
    }
    accounts.append(acc)
    account_balances[account_id] = balance

dim_accounts = pd.DataFrame(accounts)

for idx in dim_accounts.sample(frac=0.02, random_state=1).index:
    orig = dim_accounts.at[idx, "account_status"]
    dim_accounts.at[idx, "account_status"] = random.choice(["active", "ACT", "Actv"]) if orig == "Active" else orig


######### Build dim_devices #########

device_types = ["Android", "iOS", "Windows", "macOS", "Linux", "Other"]
devices = []
for i in range(1, NUM_DEVICES + 1):
    devices.append(
        {
            "device_id": f"D{300000 + i}",
            "device_type": random.choice(device_types),
            "is_jailbroken_rooted": random.random() < 0.08,
        }
    )

dim_devices = pd.DataFrame(devices)

# ==============================================================================
# 🔥 [แก้ไขใหม่] แยก Device ID ระหว่างม้า กับ คนปกติ อย่างเด็ดขาด
# ==============================================================================
all_device_ids = dim_devices["device_id"].tolist()

# ดึง 50 เครื่องแรกมาเป็น "เครื่องเฉพาะสำหรับแก๊งม้า" เท่านั้น
mule_devices = all_device_ids[:50]

# เครื่องที่เหลือทั้งหมด เป็นของ "คนปกติ"
normal_devices = all_device_ids[50:]

# สร้าง IP ปลอมสำหรับแก๊งม้าโดยเฉพาะ (สัก 20 IPs)
mule_ips = [gen_ip() for _ in range(20)]
# ==============================================================================

######### Choose mule accounts #########

num_mule_accounts = int(NUM_ACCOUNTS * 0.04) 
mule_accounts = list(dim_accounts.sample(n=num_mule_accounts, random_state=2)["account_id"])

half_mules = num_mule_accounts // 2
mule_types = ["Burner"] * half_mules + ["Sleeper"] * (num_mule_accounts - half_mules)

for acc_id, mtype in zip(mule_accounts, mule_types):
    dim_accounts.loc[dim_accounts["account_id"] == acc_id, "is_mule_label"] = True
    dim_accounts.loc[dim_accounts["account_id"] == acc_id, "mule_type"] = mtype
    if mtype == "Sleeper":
        dim_accounts.loc[dim_accounts["account_id"] == acc_id, "avg_tx_vol_last_3m"] = float(np.random.uniform(100, 900))

mule_customer_ids = dim_accounts.loc[dim_accounts["account_id"].isin(mule_accounts), "customer_id"].unique()
for idx in dim_customers[dim_customers["customer_id"].isin(mule_customer_ids)].index:
    if random.random() < 0.8:
        dim_customers.at[idx, "registered_province"] = np.random.choice(high_risk_border_provinces)
    else:
        dim_customers.at[idx, "registered_province"] = np.random.choice(normal_provinces, p=province_weights)

######### Prepare transaction timeline #########

timestamps = [random_timestamp_between(START_DATE, END_DATE) for _ in range(TOTAL_TX)]
timestamps.sort()

fraud_indices = set(random.sample(range(TOTAL_TX), FRAUD_TX))
transactions = []

def make_transaction(tx_id, ts, sender, receiver, device_id, amount, ip, channel, is_vpn=False, transaction_province=None):
    global account_balances
    sender_prev = account_balances.get(sender, 0.0)
    receiver_prev = account_balances.get(receiver, 0.0)

    sender_after = round(sender_prev - amount, 2)
    receiver_after = round(receiver_prev + amount, 2)

    account_balances[sender] = sender_after
    account_balances[receiver] = receiver_after

    if transaction_province is None:
        transaction_province = np.random.choice(normal_provinces, p=province_weights)

    return {
        "transaction_id": tx_id,
        "transaction_timestamp": ts,
        "sender_account_id": sender,
        "receiver_account_id": receiver,
        "device_id": device_id,
        "amount": round(amount, 2),
        "sender_balance_after": sender_after,
        "receiver_balance_after": receiver_after,
        "ip_address": ip,
        "is_vpn_or_tor": is_vpn,
        "transaction_province": transaction_province,
        "channel": channel,
    }

######### Pre-generate pools #########
all_accounts = list(dim_accounts["account_id"])
non_mule_accounts = [a for a in all_accounts if a not in mule_accounts]
channels = ["Mobile", "Online", "ATM", "Branch"]

# ==============================================================================
# 🔥 [แก้ไขใหม่] Shared Device สำหรับม้า ต้องมาจากสระ mule_devices
# ==============================================================================
shared_device = random.choice(mule_devices)
shared_ip = random.choice(mule_ips)


######### Construct fraud transactions to meet scenarios #########

planned_fraud_tx = []  

# 1) Smurfing
smurf_mules = mule_accounts[:30]
for mule in smurf_mules:
    center_ts = random_timestamp_between(START_DATE, END_DATE)
    senders = random.sample(non_mule_accounts, 8)
    for s in senders:
        ts = center_ts + timedelta(seconds=random.randint(-900, 900))
        tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
        tx = make_transaction(
            tx_id=str(uuid.uuid4()),
            ts=ts,
            sender=s,
            receiver=mule,
            device_id=random.choice(mule_devices), # 🔥 เปลี่ยนเป็น mule_devices
            amount=random.uniform(100, 500),
            ip=random.choice(mule_ips),            # 🔥 เปลี่ยนเป็น mule_ips
            channel="Mobile",
            is_vpn=random.random() < 0.05,
            transaction_province=tprov,
        )
        planned_fraud_tx.append(tx)

# 2) Dormancy Spike
sleeper_mules = [m for m in mule_accounts if dim_accounts.loc[dim_accounts["account_id"] == m, "mule_type"].iloc[0] == "Sleeper"]
for mule in sleeper_mules[:50]:
    avg = float(dim_accounts.loc[dim_accounts["account_id"] == mule, "avg_tx_vol_last_3m"].iloc[0])
    spike_amount = max(2000, avg * 6.0)
    ts = random_timestamp_between(START_DATE, END_DATE)
    sender = random.choice(non_mule_accounts)
    tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
    tx_in = make_transaction(str(uuid.uuid4()), ts, sender, mule, random.choice(mule_devices), spike_amount, random.choice(mule_ips), "Online", transaction_province=tprov)
    planned_fraud_tx.append(tx_in)

# 3) Shared Device/IP
for _ in range(15):
    day_center = START_DATE + timedelta(days=random.randint(0, 29))
    # 🔥 เปลี่ยนเป็นใช้บัญชีม้าในการแชร์เครื่องแทนที่จะเป็นบัญชีคนปกติ
    mules_shared = random.sample(mule_accounts, min(5, len(mule_accounts)))
    for m in mules_shared:
        ts = day_center + timedelta(seconds=random.randint(0, 86399))
        tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
        tx = make_transaction(str(uuid.uuid4()), ts, random.choice(non_mule_accounts), m, shared_device, random.uniform(50, 2000), shared_ip, "Mobile", transaction_province=tprov)
        planned_fraud_tx.append(tx)

# 4) Pass-through
pass_through_mules = mule_accounts[30:90]
for mule in pass_through_mules:
    recv_sender = random.choice(non_mule_accounts)
    incoming_amount = random.uniform(20000, 80000)
    ts_in = random_timestamp_between(START_DATE, END_DATE)
    tprov_in = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
    tx_in = make_transaction(str(uuid.uuid4()), ts_in, recv_sender, mule, random.choice(mule_devices), incoming_amount, random.choice(mule_ips), "Online", transaction_province=tprov_in)
    planned_fraud_tx.append(tx_in)

    outgoing_amount = incoming_amount * random.uniform(0.98, 0.999)
    ts_out = ts_in + timedelta(seconds=random.randint(10, 299))
    wash_receiver = random.choice(non_mule_accounts)
    tprov_out = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
    tx_out = make_transaction(str(uuid.uuid4()), ts_out, mule, wash_receiver, random.choice(mule_devices), outgoing_amount, random.choice(mule_ips), "Online", transaction_province=tprov_out)
    planned_fraud_tx.append(tx_out)

# 5) Remaining fraud transactions
remaining_needed = FRAUD_TX - len(planned_fraud_tx)
if remaining_needed > 0:
    for _ in range(remaining_needed):
        mule = random.choice(mule_accounts)
        if random.random() < 0.6:
            sender = mule
            receiver = random.choice(non_mule_accounts)
            amount = random.uniform(500, 50000)
        else:
            sender = random.choice(non_mule_accounts)
            receiver = mule
            amount = random.uniform(100, 50000)

        tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
        tx = make_transaction(str(uuid.uuid4()), random_timestamp_between(START_DATE, END_DATE), sender, receiver, random.choice(mule_devices), amount, random.choice(mule_ips), random.choice(channels), transaction_province=tprov)
        planned_fraud_tx.append(tx)

if len(planned_fraud_tx) != FRAUD_TX:
    if len(planned_fraud_tx) > FRAUD_TX:
        planned_fraud_tx = planned_fraud_tx[:FRAUD_TX]
    else:
        while len(planned_fraud_tx) < FRAUD_TX:
            mule = random.choice(mule_accounts)
            tx = make_transaction(str(uuid.uuid4()), random_timestamp_between(START_DATE, END_DATE), random.choice(non_mule_accounts), mule, random.choice(mule_devices), random.uniform(100, 10000), random.choice(mule_ips), random.choice(channels))
            planned_fraud_tx.append(tx)


######### Build normal transactions for remaining slots #########
all_tx_records = []

fraud_positions = sorted(random.sample(range(TOTAL_TX), FRAUD_TX))
fraud_iter = iter(planned_fraud_tx)

for i, ts in enumerate(timestamps):
    if i in fraud_positions:
        tx = next(fraud_iter)
        all_tx_records.append(tx)
    else:
        sender = random.choice(non_mule_accounts)
        receiver = random.choice(non_mule_accounts)
        while receiver == sender:
            receiver = random.choice(non_mule_accounts)

        amount = float(max(0, np.random.exponential(3000)))
        # 🔥 ใช้ normal_devices และ gen_ip() ปกติสำหรับคนทั่วไป
        tx = make_transaction(str(uuid.uuid4()), ts, sender, receiver, random.choice(normal_devices), amount, gen_ip(), random.choice(channels), is_vpn=(random.random() < 0.02))
        all_tx_records.append(tx)


fact_transactions = pd.DataFrame(all_tx_records)


######### Dirty data injection #########
dirty_idx = set(random.sample(range(len(fact_transactions)), DIRTY_ROWS))

num_missing_occ = max(1, int(0.04 * len(dim_customers)))
for idx in random.sample(list(dim_customers.index), num_missing_occ):
    dim_customers.at[idx, "occupation"] = None

for idx in dirty_idx:
    fact_transactions.at[idx, "ip_address"] = None

for idx in random.sample(range(len(fact_transactions)), max(1, int(0.005 * len(fact_transactions)))):
    fact_transactions.at[idx, "amount"] = -abs(fact_transactions.at[idx, "amount"])

dup_rows = fact_transactions.sample(3, random_state=7)
fact_transactions = pd.concat([fact_transactions, dup_rows], ignore_index=True)


######### Final data hygiene touches #########
fact_transactions["transaction_timestamp"] = pd.to_datetime(fact_transactions["transaction_timestamp"])
used_mules = set(dim_accounts.loc[dim_accounts["is_mule_label"], "account_id"].tolist())
fact_transactions = fact_transactions.sample(frac=1, random_state=11).reset_index(drop=True)


######### Export to Excel #########
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "mule_account_mock_data.xlsx")
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    dim_customers.to_excel(writer, sheet_name="dim_customers", index=False)
    dim_accounts.to_excel(writer, sheet_name="dim_accounts", index=False)
    dim_devices.to_excel(writer, sheet_name="dim_devices", index=False)
    fact_transactions.to_excel(writer, sheet_name="fact_transactions", index=False)

print(f"Done — generated {len(fact_transactions)} transactions ({FRAUD_TX} flagged as fraud in account labels). Excel written to {output_file}")