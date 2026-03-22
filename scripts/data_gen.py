"""
Synthetic data generator for Mule Account Detection project.

Creates 4 DataFrames (dim_customers, dim_accounts, dim_devices, fact_transactions)
and exports them to `mule_account_mock_data.xlsx` with each DF on its own sheet.

Notes/requirements implemented:
- Total transactions: 1000 (approx. cap). Exactly 5% (50) labelled fraudulent in the
  transactions table.
- Fraud scenarios implemented: Smurfing, Dormancy Spike, Shared Device/IP,
  Pass-through (dwell < 5 min), Zero-balance cashout.
- Dirty data: missing values, inconsistent account_status formats, impossible ages,
  negative amounts, and duplicated transactions.

Dependencies: pandas, numpy, faker, openpyxl (for Excel writer)

Run as: python data_gen.py
"""

import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import faker
from faker import Faker
import os


######### Configuration #########
TOTAL_TX = 20000      # จำนวนรายการโอนเงินทั้งหมด 20,000 รายการ
FRAUD_PCT = 0.05
FRAUD_TX = int(TOTAL_TX * FRAUD_PCT)  

NUM_ACCOUNTS = 6000   # จำนวนบัญชีทั้งหมด 6,000 บัญชี
NUM_CUSTOMERS = 5000  # จำนวนลูกค้า 5,000 คน
NUM_DEVICES = 2400    # จำนวนอุปกรณ์ที่ใช้ล็อกอิน 2,400 เครื่อง

START_DATE = datetime.now() - timedelta(days=30)
END_DATE = datetime.now()

DIRTY_PCT = 0.04  # 3-5% dirty rows (choose 4%) of fact_transactions
DIRTY_ROWS = max(1, int(TOTAL_TX * DIRTY_PCT))

fake = Faker()
random.seed(42)
np.random.seed(42)


######### Helpers #########

def random_timestamp_between(start, end):
	"""Return random datetime between start and end."""
	delta = end - start
	return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def gen_ip():
	# Generate realistic IPv4 address (keep simple and localizable)
	return fake.ipv4()


######### Build dim_customers #########

occupations = [
	"Teacher",
	"Engineer",
	"Unemployed",
	"Doctor",
	"Programmer",
	"Driver",
	"Sales",
	"Housewife",
	"Student",
]

# Thai provinces for normal distribution (Bangkok should be most common)
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

# High-risk border provinces used to skew mule accounts and fraudulent transactions
high_risk_border_provinces = [
    # ติดกัมพูชา
    "Ubon Ratchathani", "Si Sa Ket", "Surin", "Buri Ram", "Sa Kaeo", "Chanthaburi", "Trat",
    # ติดลาว (ตัด อุบลราชธานี ที่ซ้ำออก)
    "Chiang Rai", "Phayao", "Nan", "Uttaradit", "Loei", "Nong Khai", "Bueng Kan", 
    "Nakhon Phanom", "Mukdahan", "Amnat Charoen", "Phitsanulok",
    # ติดพม่า (ตัด เชียงราย ที่ซ้ำออก)
    "Mae Hong Son", "Chiang Mai", "Prachuap Khiri Khan", "Phetchaburi", "Ratchaburi", 
    "Kanchanaburi", "Tak", "Ranong", "Chumphon",
    # ติดมาเลเซีย
    "Satun", "Songkhla", "Yala", "Narathiwat"
]

# Probability distribution for normal provinces (Bangkok highest)
# Give Bangkok ~30% probability, rest share remaining 70% equally
rest_prob = 0.70
other_prob = rest_prob / (len(normal_provinces) - 1)
province_weights = [0.30] + [other_prob] * (len(normal_provinces) - 1)

# Alias for backwards-compatibility in code that used `provinces` variable name
provinces = normal_provinces

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
	age = int(np.random.normal(36, 10))
	# keep ages mostly realistic
	if random.random() < 0.01:
		# inject impossible ages in ~1% of customers
		age = random.choice([-5, 150])

	cust = {
		"customer_id": f"C{100000 + i}",
		"age": age,
		"occupation": random.choice(occupations),
		"risk_segment": random.choice(["Low", "Medium", "High"]),
		"kyc_status": random.choice(["Verified", "Unverified", "Pending"]),
		# Assign registered province skewed towards Bangkok for normal users
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
	# avg_tx_vol_last_3m skewed positive; some accounts small
	avg_tx_vol = float(max(0, np.random.lognormal(7, 1)))  # lognormal to span sizes

	# initial balance (for simulation of balances across transactions)
	balance = float(max(0, np.random.normal(10000, 20000)))

	acc = {
		"account_id": account_id,
		"customer_id": customer["customer_id"],
		"account_status": random.choice(["Active", "Closed", "Dormant"]),
		"account_age_days": account_age_days,
		"avg_tx_vol_last_3m": round(avg_tx_vol, 2),
		"is_mule_label": False,  # will flip for mule accounts
		"mule_type": "None",
	}
	accounts.append(acc)
	account_balances[account_id] = balance

dim_accounts = pd.DataFrame(accounts)

# Inject inconsistent account_status formatting in ~2% of accounts
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


######### Choose mule accounts #########
# We'll pick a small set of accounts to be labeled mule accounts; these will be used
# in fraud transactions. We want to ensure fraud_tx are exactly FRAUD_TX.

######### Choose mule accounts #########
# คำนวณจำนวนบัญชีม้าให้เป็นสัดส่วน 4% ของบัญชีทั้งหมด (จะได้ไม่ไปกระจุกตัวแค่ 12 บัญชี)
num_mule_accounts = int(NUM_ACCOUNTS * 0.04) 
mule_accounts = list(dim_accounts.sample(n=num_mule_accounts, random_state=2)["account_id"])

# Assign mule types: แบ่งครึ่งเป็น Burner และ Sleeper แบบอัตโนมัติ
half_mules = num_mule_accounts // 2
mule_types = ["Burner"] * half_mules + ["Sleeper"] * (num_mule_accounts - half_mules)

for acc_id, mtype in zip(mule_accounts, mule_types):
    dim_accounts.loc[dim_accounts["account_id"] == acc_id, "is_mule_label"] = True
    dim_accounts.loc[dim_accounts["account_id"] == acc_id, "mule_type"] = mtype
    # For sleepers, ensure low avg_tx_vol_last_3m
    if mtype == "Sleeper":
        dim_accounts.loc[dim_accounts["account_id"] == acc_id, "avg_tx_vol_last_3m"] = float(np.random.uniform(100, 900))

# Update registered_province for customers who own mule accounts: 80% chance to be
# assigned to a high-risk border province to reflect geographic risk skew.
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

# Helper to create a transaction record and update balances
def make_transaction(tx_id, ts, sender, receiver, device_id, amount, ip, channel, is_vpn=False, transaction_province=None):
	"""Create transaction dict and update account_balances accordingly.

	We compute sender_balance_after and receiver_balance_after using the running
	account_balances dict. We allow balances to go slightly negative for noisy realism.
	"""
	global account_balances
	sender_prev = account_balances.get(sender, 0.0)
	receiver_prev = account_balances.get(receiver, 0.0)

	sender_after = sender_prev - amount
	receiver_after = receiver_prev + amount

	# small randomness in rounding
	sender_after = round(sender_after, 2)
	receiver_after = round(receiver_after, 2)

	account_balances[sender] = sender_after
	account_balances[receiver] = receiver_after

	# Choose transaction province if not provided. Normal transactions use the
	# Bangkok-skewed distribution; fraud/planned transactions may pass a province
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

# Create a special device and IP for shared device/IP scenario
shared_device = dim_devices.sample(1, random_state=3)["device_id"].iloc[0]
shared_ip = gen_ip()


######### Construct fraud transactions to meet scenarios #########
# We'll craft targeted fraud events and mark their indexes as fraud_indices to
# ensure exactly FRAUD_TX fraudulent rows exist. We'll then fill remaining indices
# with normal or remaining fraud transactions.

planned_fraud_tx = []  # will store crafted fraud tx dicts

# 1) Smurfing: pick 2 mule accounts to receive many small transfers from distinct senders
smurf_mules = mule_accounts[:30]
for mule in smurf_mules:
	# create 6-8 small inbound transfers within a tight window (e.g., 30 minutes)
	center_ts = random_timestamp_between(START_DATE, END_DATE)
	senders = random.sample(non_mule_accounts, 8)
	for s in senders:
		ts = center_ts + timedelta(seconds=random.randint(-900, 900))  # +/-15 minutes
		# 80% chance the transaction province is a high-risk border province
		tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
		tx = make_transaction(
			tx_id=str(uuid.uuid4()),
			ts=ts,
			sender=s,
			receiver=mule,
			device_id=random.choice(dim_devices["device_id"].tolist()),
			amount=random.uniform(100, 500),
			ip=gen_ip(),
			channel="Mobile",
			is_vpn=random.random() < 0.05,
			transaction_province=tprov,
		)
		planned_fraud_tx.append(tx)

# 2) Dormancy Spike: sleeper mule accounts do a spike >500% of avg_tx_vol_last_3m
sleeper_mules = [m for m in mule_accounts if dim_accounts.loc[dim_accounts["account_id"] == m, "mule_type"].iloc[0] == "Sleeper"]
for mule in sleeper_mules[:50]:
	avg = float(dim_accounts.loc[dim_accounts["account_id"] == mule, "avg_tx_vol_last_3m"].iloc[0])
	spike_amount = max(2000, avg * 6.0)  # >500% (i.e., 6x)
	ts = random_timestamp_between(START_DATE, END_DATE)
	# receiver is mule (incoming)
	sender = random.choice(non_mule_accounts)
	# pick province biased to high-risk for this mule activity
	tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
	tx_in = make_transaction(str(uuid.uuid4()), ts, sender, mule, random.choice(dim_devices["device_id"].tolist()), spike_amount, gen_ip(), "Online", transaction_province=tprov)
	planned_fraud_tx.append(tx_in)

# 3) Shared Device/IP: choose a day and reuse the same device/ip with >3 distinct senders
for _ in range(15):  # จำลองว่าเกิดเหตุการณ์นี้ 15 ครั้ง
    day_center = START_DATE + timedelta(days=random.randint(0, 29))
    senders_shared = random.sample(non_mule_accounts, 5)
    for s in senders_shared:
        ts = day_center + timedelta(seconds=random.randint(0, 86399))
        tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
        tx = make_transaction(str(uuid.uuid4()), ts, s, random.choice(non_mule_accounts), shared_device, random.uniform(50, 2000), shared_ip, "Mobile", transaction_province=tprov)
        planned_fraud_tx.append(tx)

# 4) Pass-through / Dwell Time (<5 mins) + Zero-Balance Cashout:
# Choose a mule, create an incoming large transfer, then within <5 min create an outgoing
pass_through_mules = mule_accounts[30:90]
for mule in pass_through_mules:
	recv_sender = random.choice(non_mule_accounts)
	incoming_amount = random.uniform(20000, 80000)
	ts_in = random_timestamp_between(START_DATE, END_DATE)
	# set province biased to high-risk for mule activity
	tprov_in = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
	tx_in = make_transaction(str(uuid.uuid4()), ts_in, recv_sender, mule, random.choice(dim_devices["device_id"].tolist()), incoming_amount, gen_ip(), "Online", transaction_province=tprov_in)
	planned_fraud_tx.append(tx_in)

	# outgoing: almost equal to incoming, leaving near zero (<2% of incoming)
	outgoing_amount = incoming_amount * random.uniform(0.98, 0.999)
	ts_out = ts_in + timedelta(seconds=random.randint(10, 299))  # <5 minutes
	# choose an external wash account (non-mule)
	wash_receiver = random.choice(non_mule_accounts)
	# outgoing province also likely high-risk
	tprov_out = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
	tx_out = make_transaction(str(uuid.uuid4()), ts_out, mule, wash_receiver, random.choice(dim_devices["device_id"].tolist()), outgoing_amount, gen_ip(), "Online", transaction_province=tprov_out)
	# enforce zero-balance-ish: ensure sender_balance_after < 2% of incoming
	planned_fraud_tx.append(tx_out)

# 5) Remaining fraud transactions: fill up to FRAUD_TX entries by creating varied mule activity

remaining_needed = FRAUD_TX - len(planned_fraud_tx)
if remaining_needed > 0:
	for _ in range(remaining_needed):
		mule = random.choice(mule_accounts)
		# pick direction: 60% outgoing from mule, 40% incoming
		if random.random() < 0.6:
			sender = mule
			receiver = random.choice(non_mule_accounts)
			amount = random.uniform(500, 50000)
		else:
			sender = random.choice(non_mule_accounts)
			receiver = mule
			amount = random.uniform(100, 50000)

		# choose province biased to high-risk for fraud transactions
		tprov = np.random.choice(high_risk_border_provinces) if random.random() < 0.8 else np.random.choice(normal_provinces, p=province_weights)
		tx = make_transaction(str(uuid.uuid4()), random_timestamp_between(START_DATE, END_DATE), sender, receiver, random.choice(dim_devices["device_id"].tolist()), amount, gen_ip(), random.choice(channels), transaction_province=tprov)
		planned_fraud_tx.append(tx)

# Sanity: ensure we created exactly FRAUD_TX planned transactions
if len(planned_fraud_tx) != FRAUD_TX:
	# If we have more (shouldn't) or less, trim or fill with simple mule tx
	if len(planned_fraud_tx) > FRAUD_TX:
		planned_fraud_tx = planned_fraud_tx[:FRAUD_TX]
	else:
		while len(planned_fraud_tx) < FRAUD_TX:
			mule = random.choice(mule_accounts)
			tx = make_transaction(str(uuid.uuid4()), random_timestamp_between(START_DATE, END_DATE), random.choice(non_mule_accounts), mule, random.choice(dim_devices["device_id"].tolist()), random.uniform(100, 10000), gen_ip(), random.choice(channels))
			planned_fraud_tx.append(tx)


######### Build normal transactions for remaining slots #########
all_tx_records = []

# First, insert planned fraud transactions into the full timeline by picking FRAUD_TX indices
fraud_positions = sorted(random.sample(range(TOTAL_TX), FRAUD_TX))
fraud_iter = iter(planned_fraud_tx)

for i, ts in enumerate(timestamps):
	if i in fraud_positions:
		# place planned fraud transaction (already has its own timestamp); however we will
		# use the planned timestamp if provided — to maintain chronological order we still
		# use the planned tx timestamp field directly.
		tx = next(fraud_iter)
		all_tx_records.append(tx)
	else:
		# normal transaction
		sender = random.choice(non_mule_accounts)
		# prevent self transfer
		receiver = random.choice(non_mule_accounts)
		while receiver == sender:
			receiver = random.choice(non_mule_accounts)

		amount = float(max(0, np.random.exponential(3000)))  # many small, some large
		tx = make_transaction(str(uuid.uuid4()), ts, sender, receiver, random.choice(dim_devices["device_id"].tolist()), amount, gen_ip(), random.choice(channels), is_vpn=(random.random() < 0.02))
		all_tx_records.append(tx)


# Now we have TOTAL_TX transaction dicts in all_tx_records
fact_transactions = pd.DataFrame(all_tx_records)


######### Dirty data injection (3-5% of rows ~ DIRTY_ROWS) #########
dirty_idx = set(random.sample(range(len(fact_transactions)), DIRTY_ROWS))

# Missing values: occupation in dim_customers (randomly 3-5%)
num_missing_occ = max(1, int(0.04 * len(dim_customers)))
for idx in random.sample(list(dim_customers.index), num_missing_occ):
	dim_customers.at[idx, "occupation"] = None

# Missing ip_address in some transactions
for idx in dirty_idx:
	fact_transactions.at[idx, "ip_address"] = None

# Inconsistent account_status already injected earlier.

# Logical errors: inject some negative amounts in a few transaction rows
for idx in random.sample(range(len(fact_transactions)), max(1, int(0.005 * len(fact_transactions)))):
	fact_transactions.at[idx, "amount"] = -abs(fact_transactions.at[idx, "amount"])  # negative

# Duplicates: duplicate 2-3 entire rows (same transaction_id). We'll duplicate 3 rows.
dup_rows = fact_transactions.sample(3, random_state=7)
fact_transactions = pd.concat([fact_transactions, dup_rows], ignore_index=True)


######### Final data hygiene touches #########

# Ensure transaction_timestamp column is datetime dtype
fact_transactions["transaction_timestamp"] = pd.to_datetime(fact_transactions["transaction_timestamp"])

# Map is_mule_label into dim_accounts remains set earlier. But for clarity, we also
# produce a list of mule accounts used in fact_transactions for reference.
used_mules = set(dim_accounts.loc[dim_accounts["is_mule_label"], "account_id"].tolist())

# Optionally shuffle the fact_transactions rows to simulate natural ordering
fact_transactions = fact_transactions.sample(frac=1, random_state=11).reset_index(drop=True)


######### Export to Excel #########

# Ensure a data directory exists at the repository root: ../data relative to this script
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "mule_account_mock_data.xlsx")
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
	dim_customers.to_excel(writer, sheet_name="dim_customers", index=False)
	dim_accounts.to_excel(writer, sheet_name="dim_accounts", index=False)
	dim_devices.to_excel(writer, sheet_name="dim_devices", index=False)
	fact_transactions.to_excel(writer, sheet_name="fact_transactions", index=False)

print(f"Done — generated {len(fact_transactions)} transactions ({FRAUD_TX} flagged as fraud in account labels). Excel written to {output_file}")

