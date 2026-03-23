# DE471_Mule_account_detection
This repository serves for DE471 DA&amp;BI project.
## 📚 Data Dictionary

This section outlines the schema and definitions for the simulated banking dataset used in the Mule Account Detection project.

### 1. Dimension Table: `dim_customers`
Contains demographic and risk profile information for each customer.

| Column Name | Data Type | Key | Description |
| :--- | :---: | :---: | :--- |
| `customer_id` | string | **PK** | Unique identifier for the customer. |
| `age` | int | - | Age of the customer. |
| `occupation` | string | - | Customer's declared occupation. |
| `risk_segment` | string | - | Assigned risk level (e.g., Low, Medium, High). |
| `kyc_status` | string | - | Identity verification method (e.g., eKYC, Branch). |
| `registered_province` | string | - | Province of the customer's registered address. |

### 2. Dimension Table: `dim_accounts`
Contains account-level details and mule classification labels.

| Column Name | Data Type | Key | Description |
| :--- | :---: | :---: | :--- |
| `account_id` | string | **PK** | Unique identifier for the bank account. |
| `customer_id` | string | **FK** | Reference to `dim_customers`. |
| `account_status` | string | - | Current status of the account (e.g., Active, Dormant). |
| `account_age_days` | int | - | Number of days since the account was opened. |
| `avg_tx_vol_last_3m` | float | - | Average transaction volume over the last 3 months (THB). |
| `is_mule_label` | boolean | - | Target variable: `True` if flagged as a mule, `False` otherwise. |
| `mule_type` | string | - | Specific mule category (e.g., Burner, Sleeper, None). |

### 3. Dimension Table: `dim_devices`
Contains information about the devices used to access accounts and perform transactions.

| Column Name | Data Type | Key | Description |
| :--- | :---: | :---: | :--- |
| `device_id` | string | **PK** | Unique identifier for the device. |
| `device_type` | string | - | Type of device used (e.g., Mobile, Web, ATM). |
| `is_jailbroken_rooted` | boolean | - | `True` if the device's OS has been compromised (Rooted/Jailbroken). |

### 4. Fact Table: `fact_transactions`
Contains transactional records and calculated behavioral features for fraud detection.

| Column Name | Data Type | Key | Description |
| :--- | :---: | :---: | :--- |
| `transaction_id` | string | **PK** | Unique identifier for the transaction. |
| `transaction_timestamp` | datetime | - | Date and time the transaction occurred. |
| `sender_account_id` | string | **FK** | Account ID of the sender (Reference to `dim_accounts`). |
| `receiver_account_id` | string | **FK** | Account ID of the receiver (Reference to `dim_accounts`). |
| `device_id` | string | **FK** | Device ID used for the transaction (Reference to `dim_devices`). |
| `amount` | float | - | Transaction amount transferred. |
| `sender_balance_after` | float | - | Sender's account balance after the transaction. |
| `receiver_balance_after`| float | - | Receiver's account balance after the transaction. |
| `ip_address` | string | - | IP address logged during the transaction. |
| `is_vpn_or_tor` | boolean | - | `True` if the IP address indicates VPN or Tor network usage. |
| `transaction_province` | string | - | Geographic location (province) where the transaction was initiated. |
| `channel` | string | - | Platform used for the transaction (e.g., Mobile_App). |
| `dwell_time_minutes` | float | - | Time (in minutes) funds remained in the account before being transferred out. |
| `impossible_travel_flag`| boolean | - | `True` if sequential transactions suggest physically impossible travel distances. |
