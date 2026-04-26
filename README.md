# DE471 — Mule Account Detection
# การตรวจจับบัญชีม้า (Mule Account Detection)
โครงการวิเคราะห์ข้อมูลเพื่อตรวจจับธุรกรรมที่ผิดปกติจากบัญชีม้าในระบบธนาคาร

**Designed by:** MTN (MUMTENGNHONG) GROUP  
**Date:** 18 January 2026  
**Course:** DE471 Data Analytics & Business Intelligence

---

## 1. บทนำ (Introduction / Problem Statement)

ประเทศไทยกำลังเผชิญกับการเพิ่มขึ้นอย่างรวดเร็วของกลโกงแบบ **Authorized Push Payment (APP) Scam** ซึ่งเป็นรูปแบบการฉ้อโกงที่เหยื่อถูกหลอกให้โอนเงินด้วยความสมัครใจ เนื่องจากธุรกรรมเหล่านี้ถูกเริ่มต้นโดยลูกค้าที่ถูกต้องตามกฎหมาย ระบบตรวจจับการทุจริตแบบเดิมจึงไม่สามารถตรวจพบได้อย่างมีประสิทธิภาพ

หลังจากที่เหยื่อโอนเงินไปแล้ว มิจฉาชีพจะใช้ **บัญชีม้า (Mule Accounts)** เพื่อรับเงินและรีบโอนต่อออกไปภายในเวลาเพียงไม่กี่นาที ทำให้ธนาคารมีโอกาสน้อยมากในการระงับธุรกรรมหรือกู้คืนเงิน ในปัจจุบันธนาคารยังทำงานในลักษณะ **Reactive** คือรอให้เกิดความเสียหายก่อนแล้วจึงแก้ไข

ดังนั้น โครงการนี้จึงมีความจำเป็นในการพัฒนาระบบวิเคราะห์ข้อมูลเชิงรุก (Proactive Data Analytics) เพื่อตรวจจับธุรกรรมที่เกี่ยวข้องกับบัญชีม้าในลักษณะใกล้เคียงเวลาจริง (Near Real-Time) ก่อนที่เงินจะถูกโอนออกนอกระบบ

---

## 2. วัตถุประสงค์ (SMART Objectives / Value Propositions)

**SMART Objectives:**  
พัฒนา **Proactive Mule Account Detection Dashboard** ให้แล้วเสร็จภายใน Q2 2026 โดยระบบสามารถตรวจจับกิจกรรมของบัญชีม้าที่น่าสงสัยได้ **ภายใน 30 นาที** โดยใช้ข้อมูลธุรกรรมที่มีอยู่แล้ว บรรลุค่า **Recall ≥ 80%** และ **False Positive Rate ≤ 5%** เพื่อรองรับการตอบสนองปฏิบัติการที่รวดเร็วขึ้น และลดความสูญเสียทางการเงินจาก APP Scam

**Value Propositions:**

- **Proactive Detection:** เปลี่ยนจากการทำงานแบบ Reactive เป็น Proactive โดยสามารถตั้ง Alert ได้ก่อนที่เงินจะถูกโอนออกนอกระบบทั้งหมด
- **Faster Operational Response:** ลดเวลาการตอบสนองของทีม Fraud Operations ด้วย Dashboard ที่แสดงบัญชีที่มีความเสี่ยงสูงในแบบ Near Real-Time
- **AML Compliance:** รองรับข้อกำหนดของธนาคารแห่งประเทศไทยและ AMLO ในด้านการรายงานธุรกรรมที่น่าสงสัย (STR)

---

## 3. คำถามและสมมติฐาน (Questions / Hypothesis)

### คำถามเชิงวิเคราะห์ (5W1H Analytical Questions)

**Who & What**
- บัญชีม้าประเภท Burner และ Sleeper แตกต่างจากบัญชีปกติอย่างไรในเชิงพฤติกรรมธุรกรรม?
- ระดับ Spike Ratio ที่เท่าไรที่สามารถใช้แยกแยะบัญชีม้าออกจากลูกค้าที่โอนเงินสูงตามปกติได้?

**When & How**
- เงินที่รับเข้ามาในบัญชีม้าถูกโอนออกภายในเวลานานเท่าใด และมีช่วงเวลา (Dwell Time) ที่สั้นแค่ไหนที่บ่งบอกพฤติกรรม Rapid Transit?
- บัญชีม้าประเภท Sleeper มีช่วงเวลาพักการใช้งานนานเพียงใดก่อนที่จะถูกเปิดใช้งานเพื่อทำธุรกรรมขนาดใหญ่?

**Where**
- จังหวัดหรือพื้นที่ใดในประเทศไทยที่มีความเข้มข้นของธุรกรรมที่เชื่อมโยงกับบัญชีม้าสูงที่สุด?
- การโอนเงินข้ามจังหวัดภายในเวลา 2 ชั่วโมง (Impossible Travel) มีความสัมพันธ์กับบัญชีม้าหรือไม่?

**Why**
- การระบุพฤติกรรมเหล่านี้ช่วยลดความสูญเสียจาก APP Scam และเพิ่มความปลอดภัยในระบบธนาคารได้อย่างไร?

### สมมติฐาน (Hypothesis)

สามารถตรวจจับบัญชีม้าได้โดยใช้การรวมกันของสัญญาณพฤติกรรม (Behavioral Signals) จากข้อมูลธุรกรรมที่มีอยู่ ได้แก่ Spike Ratio, Dwell Time, การใช้งาน Device/IP ร่วมกัน และรูปแบบการโอนเงินข้ามจังหวัด โดยไม่จำเป็นต้องอาศัยข้อมูลส่วนบุคคลหรือข้อมูลภายนอกเพิ่มเติม

---

## 4. แหล่งที่มาของข้อมูล (Data Source)

- **Dataset:** ชุดข้อมูลสังเคราะห์ (AI-Generated Synthetic Dataset) จำลองสภาพแวดล้อมธนาคารค้าปลีกในประเทศไทย
- **ขนาด:** 20,000 ธุรกรรม | 6,000 บัญชี | 5,000 ลูกค้า | 2,400 อุปกรณ์
- **อัตราส่วนการฉ้อโกง:** ~5% ของธุรกรรมทั้งหมด | ~4% ของบัญชีทั้งหมดถูกระบุเป็น Mule
- **ช่วงเวลา:** ข้อมูลย้อนหลัง 30 วัน
- **Schema:** Star Schema — 1 Fact Table + 3 Dimension Tables

---

## 5. โครงสร้างของชุดข้อมูล — Data Dictionary

### `dim_customers` — ข้อมูลลูกค้า

| ชื่อคอลัมน์ | ประเภทข้อมูล | คำอธิบาย | ค่าที่เป็นไปได้ |
| :--- | :--- | :--- | :--- |
| **customer_id** | String | รหัสลูกค้าเฉพาะ | `C1xxxxx` |
| **age** | Integer | อายุลูกค้า (ทำความสะอาด: แทนค่า Outlier ด้วย Median) | 0 – 100 ปี |
| **occupation** | String | อาชีพ (ค่า Null ถูกแทนด้วย `"Unknown"`) | Teacher, Engineer, Unemployed, ... |
| **risk_segment** | Categorical | ระดับความเสี่ยงที่ธนาคารกำหนด | `Low`, `Medium`, `High` |
| **kyc_status** | Categorical | สถานะการยืนยันตัวตน | `Verified`, `Unverified`, `Pending` |
| **registered_province** | String | จังหวัดที่ลงทะเบียน — ลูกค้าที่เชื่อมโยงกับบัญชีม้ามักอยู่ในจังหวัดชายแดนความเสี่ยงสูง | จังหวัดในประเทศไทย |

### `dim_accounts` — ข้อมูลบัญชี

| ชื่อคอลัมน์ | ประเภทข้อมูล | คำอธิบาย | ค่าที่เป็นไปได้ |
| :--- | :--- | :--- | :--- |
| **account_id** | String | รหัสบัญชีเฉพาะ | `A2xxxxx` |
| **customer_id** | String | FK → `dim_customers` | — |
| **account_status** | Categorical | สถานะบัญชี (มาตรฐานจาก Dirty Data) | `Active`, `Dormant`, `Closed` |
| **account_age_days** | Integer | อายุบัญชีเป็นวัน — บัญชีใหม่ (0–500 วัน) มักเชื่อมโยงกับ Burner Mule | 0 – 3,650+ วัน |
| **avg_tx_vol_last_3m** | Float | ปริมาณธุรกรรมเฉลี่ย 3 เดือน (บาท) — ค่าต่ำมากสำหรับ Sleeper Mule | ≥ 0 |
| **is_mule_label** | Boolean | **Ground Truth Label** — `True` สำหรับบัญชีม้าที่ยืนยันแล้ว (~4%) | `True`, `False` |
| **mule_type** | Categorical | ประเภทบัญชีม้า | `Burner`, `Sleeper`, `None` |

### `dim_devices` — ข้อมูลอุปกรณ์

| ชื่อคอลัมน์ | ประเภทข้อมูล | คำอธิบาย | ค่าที่เป็นไปได้ |
| :--- | :--- | :--- | :--- |
| **device_id** | String | รหัสอุปกรณ์เฉพาะ | `D3xxxxx` |
| **device_type** | Categorical | ระบบปฏิบัติการ / แพลตฟอร์ม | `Android`, `iOS`, `Windows`, `macOS`, `Linux`, `Other` |
| **is_jailbroken_rooted** | Boolean | Flag อุปกรณ์ที่ถูก Jailbreak หรือ Root (~8%) | `True`, `False` |

### `fact_transactions` — ข้อมูลธุรกรรม

| ชื่อคอลัมน์ | ประเภทข้อมูล | คำอธิบาย | ค่าที่เป็นไปได้ |
| :--- | :--- | :--- | :--- |
| **transaction_id** | String | UUID ของธุรกรรม (ทำ Deduplication ระหว่าง Cleaning) | UUID |
| **transaction_timestamp** | Datetime | วันเวลาของธุรกรรม | ช่วง 30 วัน |
| **sender_account_id** | String | FK → `dim_accounts` (ผู้โอน) | — |
| **receiver_account_id** | String | FK → `dim_accounts` (ผู้รับ) | — |
| **device_id** | String | FK → `dim_devices` | — |
| **amount** | Float | จำนวนเงินโอน (บาท) — ค่าติดลบถูกแก้เป็น Absolute Value | ≥ 0 |
| **sender_balance_after** | Float | ยอดคงเหลือของผู้โอนหลังธุรกรรม | — |
| **ip_address** | String | IP ต้นทาง (Null ถูกแทนด้วย `0.0.0.0`) | IPv4 |
| **is_vpn_or_tor** | Boolean | Flag การใช้ VPN หรือ Tor | `True`, `False` |
| **transaction_province** | String | จังหวัดที่ทำธุรกรรม | จังหวัดในประเทศไทย |
| **channel** | Categorical | ช่องทางธุรกรรม | `Mobile`, `Online`, `ATM`, `Branch` |
| **impossible_travel_flag** | Boolean | **(Engineered)** โอนข้ามจังหวัดภายใน 2 ชั่วโมง | `True`, `False` |

### Engineered Features (จาก `feature_engineering.py`)

| Feature | สูตร / Logic | สัญญาณที่บ่งบอก |
| :--- | :--- | :--- |
| **spike_ratio** | `amount / avg_tx_vol_last_3m` | ค่า > 10 → Dormancy Spike |
| **is_dormancy_spike** | `spike_ratio > 10.0` | Flag การเปิดใช้งาน Sleeper Mule |
| **is_zero_balance_cashout** | `sender_balance_after / amount < 0.02` | รูปแบบการดูดเงินออกจนเกลี้ยงบัญชี |
| **is_shared_device** | `distinct_accounts_per_device > 3` หรือ `per_ip > 3` | โครงสร้างพื้นฐานของ Mule Farm |
| **dwell_time_mins** | ช่วงเวลาระหว่างรับเงินเข้า → โอนออก (นาที) | < 5 นาที → Pass-Through |
| **is_pass_through** | `dwell_time_mins < 5.0` | พฤติกรรม Hit-and-Run |
| **impossible_travel_flag** | โอนข้ามจังหวัดภายใน < 2 ชั่วโมง | ความผิดปกติทางภูมิศาสตร์ |

---

## 6. โครงสร้าง Repository

```
DE471_Mule_account_detection/
│
├── data/
│   ├── mule_account_mock_data.xlsx      # ชุดข้อมูลดิบ (Raw) — Star Schema 4 Sheets
│   ├── mule_data_cleaned.xlsx           # ชุดข้อมูลหลัง Data Cleaning
│   └── mule_data_features.xlsx          # ชุดข้อมูล Feature-Engineered (พร้อมสำหรับ EDA/Model)
│
├── notebooks/
│   └── EDA_Mule_Detection.twbx          # Tableau Workbook — การวิเคราะห์ 5W1H
│
├── src/
│   ├── data_gen.py                       # Script สร้างชุดข้อมูลสังเคราะห์ (20,000 ธุรกรรม)
│   ├── data_clean.py                     # Pipeline ทำความสะอาดข้อมูล
│   └── feature_engineering.py           # คำนวณ Behavioral Features 7 ตัว
│
├── presentation/
│   └── Project Canvas MTN GROUP.pptx    # Project Canvas Slide Deck
│
└── README.md
```

---

## 7. กระบวนการทำความสะอาดข้อมูล (Data Cleaning Process)

ชุดข้อมูลดิบถูกสร้างขึ้นพร้อมกับ Dirty Data ที่จงใจฝังไว้ เพื่อจำลองสภาพแวดล้อมจริงของธนาคาร กระบวนการทำความสะอาดจึงดำเนินการดังนี้

### 1. Fact Transactions
- **Duplicate Rows:** ตรวจสอบและลบแถวซ้ำซ้อนโดยใช้ `transaction_id` เป็น Key (พบ 3 แถวซ้ำ)
- **Negative Amount:** แก้ไขค่า Amount ติดลบให้เป็น Absolute Value เพื่อรักษาสัญญาณการฉ้อโกง
- **Null IP Address:** แทนค่า Null ด้วย `0.0.0.0` แทนการลบแถว เพื่อป้องกันการทำลาย Fraud Signal

### 2. Dim Accounts
- **Account Status:** มาตรฐานค่าที่ไม่สม่ำเสมอ เช่น `"ACT"`, `"Actv"`, `"active"` ให้เป็น `"Active"`

### 3. Dim Customers
- **Age Outliers:** แทนค่าอายุที่ผิดปกติ (เช่น -5, 150) ด้วยค่า Median แทนการลบแถวออก เนื่องจากลูกค้าเหล่านี้อาจเป็นบัญชีม้า
- **Null Occupation:** แทนค่า Null ด้วย `"Unknown"`

> **หลักการสำคัญ:** ไม่ลบ Outliers ออก เนื่องจาก Outlier คือสัญญาณของการฉ้อโกง (Rare Fraud Class) การลบออกจะทำลาย Fraud Signal ที่มีคุณค่าที่สุด

---

## 8. การวิเคราะห์ข้อมูลเชิงสำรวจ (Exploratory Data Analysis: EDA)

กลยุทธ์หลักที่ใช้ในการวิเคราะห์ข้อมูลที่มีความไม่สมดุลสูง (Class Imbalance 1:42.6):
- ใช้ **Log Scale** บน Y-Axis เพื่อให้มองเห็น Minority Class (บัญชีม้า) ได้ชัดเจน แทนที่จะถูกกลืนหายโดย Normal Class
- ใช้ **Boxplot** เพื่อแสดงการกระจายและ Outlier ของตัวแปรอย่าง Spike Ratio
- ใช้ **สีที่มีความตัดกันสูง** (น้ำเงิน = ปกติ, แดง = บัญชีม้า) เพื่อเน้น Minority Class ในทุกกราฟ
- ไม่ลบ Outlier ออก เพราะค่าสุดขั้วคือสัญญาณสำคัญของการฉ้อโกง

### Dashboard ภาพรวม (EDA Overview)

![EDA Dashboard Overview](images/8_dashboard_overview.png)
*ภาพรวม Dashboard แสดงทุก Visualization ในหน้าเดียว — Dataset: 20,000 ธุรกรรม | Mule: 459 (4%) | Normal: 19,541 (96%) | Ratio 1:24*

---

### กราฟที่ 1 — Who & What: การกระจายตัวของ Class (Class Imbalance)

![Class Distribution](images/1_class_distribution.png)
*กราฟ Bar Chart แบบ Log Scale แสดงจำนวนธุรกรรมแยกตามประเภทบัญชี*

กราฟนี้ตอบคำถาม **"WHO are the mule accounts?"** โดยแสดงให้เห็นความไม่สมดุลของข้อมูลอย่างชัดเจน บัญชีม้าคิดเป็นเพียง **2.3% ของธุรกรรมทั้งหมด** (459 จาก 20,000) โดยแบ่งเป็น Burner 257 ธุรกรรม และ Sleeper 202 ธุรกรรม ความไม่สมดุลในระดับ **1:42.6** นี้ยืนยันว่าจำเป็นต้องใช้เทคนิคพิเศษในการตรวจจับ เช่น Log Scale และการเน้น Minority Class ในการแสดงผล แทนที่จะใช้กราฟปกติที่บัญชีม้าจะแทบมองไม่เห็น

---

### กราฟที่ 2 — Who & What: ช่องทางธุรกรรมของบัญชีม้าแต่ละประเภท

![Mule Type by Channel](images/3_mule_type_by_channel.png)
*Stacked Bar Chart แสดงจำนวนธุรกรรมของ Burner และ Sleeper แยกตาม Channel*

กราฟนี้ตอบคำถาม **"WHAT channels do mule accounts use?"** พบว่า Burner Accounts ใช้ช่องทาง **Mobile และ Online** สูงกว่า Sleeper อย่างเห็นได้ชัด ในขณะที่ Sleeper Accounts มีสัดส่วน **ATM และ Online** ที่สูงกว่าเมื่อเทียบกับตัวเอง ซึ่งบ่งชี้ว่าบัญชีม้าทั้งสองประเภทมีกลยุทธ์การหลีกเลี่ยงการตรวจจับที่แตกต่างกัน — Burner เน้นความเร็วผ่าน Mobile ในขณะที่ Sleeper หลีกเลี่ยงการสร้างรูปแบบที่ชัดเจนด้วยการกระจาย Channel

---

### กราฟที่ 3 — What: การกระจายของ Spike Ratio (สัญญาณที่แข็งแกร่งที่สุด)

![Spike Ratio Distribution](images/4_spike_ratio_boxplot.png)
*Boxplot แบบ Log Scale เปรียบเทียบ Spike Ratio ระหว่างบัญชีปกติ (เหลือง) และบัญชีม้า (แดง) พร้อม Reference Line ที่ Alert Threshold 10x*

กราฟนี้ตอบคำถาม **"WHAT is the quantitative threshold that separates mule transactions?"** และพิสูจน์ได้ว่า Spike Ratio คือสัญญาณที่ทรงพลังที่สุดในชุดข้อมูลนี้ — บัญชีม้ามีค่าเฉลี่ย Spike Ratio **44 เท่า** เมื่อเทียบกับ **5 เท่า** ของบัญชีปกติ กราฟ Boxplot แบบ Log Scale ช่วยให้เห็นความแตกต่างที่ชัดเจน โดย Median ของบัญชีม้าพุ่งอยู่เหนือ Alert Threshold (10x) อย่างเด่นชัด ในขณะที่ Median ของบัญชีปกติอยู่ต่ำกว่า 10x อย่างมีนัยสำคัญ

---

### กราฟที่ 4 — Where: ความเสี่ยงทางภูมิศาสตร์รายจังหวัด

![Geographic Risk Map](images/6_geographic_map.png)
*Choropleth Map แสดงอัตราส่วน Mule Rate รายจังหวัดทั่วประเทศไทย (สีแดงเข้ม = ความเสี่ยงสูง)*

กราฟนี้ตอบคำถาม **"WHERE should fraud prevention efforts be prioritized geographically?"** ผลการวิเคราะห์พบว่าความเสี่ยงกระจายตัวทั่วทุกภูมิภาค **โดยไม่มีจังหวัดใดจุดเดียวที่เป็น Hotspot หลัก** รูปแบบนี้บ่งชี้ว่าเครือข่ายบัญชีม้าปฏิบัติการในหลายภูมิภาคพร้อมกัน ซึ่งหมายความว่าการใช้ Geographic Profiling เพียงอย่างเดียวไม่เพียงพอ และจำเป็นต้องใช้ร่วมกับ Behavioral Signal อื่นๆ

---

### กราฟที่ 5 — Where & Who: Account Age vs. Transaction Volume (Scatter Plot)

![Account Age Scatter Plot](images/5_account_age_scatter.png)
*Scatter Plot แสดงความสัมพันธ์ระหว่าง Account Age Days (แกน X) และ Avg Tx Vol Last 3M (แกน Y) พร้อม Risk Threshold ที่ 500 วัน*

กราฟนี้ตอบคำถาม **"WHICH accounts exhibit suspicious behavior based on account age?"** บัญชีม้า (จุดสีแดง) กระจุกตัวอยู่ใน **ช่วง 0–500 วัน** อย่างเด่นชัด ยืนยันว่าบัญชีที่เพิ่งเปิดใหม่มีความเสี่ยงสูงที่สุดโดยไม่ขึ้นกับปริมาณธุรกรรม นอกจากนี้ยังพบว่าบัญชีม้ามีการกระจายตัว Avg Tx Vol ที่หลากหลาย ทำให้ไม่สามารถใช้ Volume เพียงอย่างเดียวในการตัดสิน จำเป็นต้องใช้ Account Age ร่วมด้วยเสมอ

---

### กราฟที่ 6 — When & How: Dormancy Spike และ Zero Balance Rate

![Dormancy Spike and Zero Balance](images/2_dormancy_spike_zero_balance.png)
*Bar Chart เปรียบเทียบ Dormancy Spike Rate และ Zero Balance Cashout Rate ระหว่างบัญชีปกติ (น้ำเงิน) และบัญชีม้า (แดง) พร้อม Reference Line ที่ Alert Threshold 50%*

กราฟนี้ตอบคำถาม **"HOW do mule accounts drain funds after receiving them?"** ผลการวิเคราะห์พบความแตกต่างที่ชัดเจนมาก:
- **Dormancy Spike Rate:** บัญชีม้า **77%** vs บัญชีปกติ **24%** — สูงกว่า Alert Threshold (50%) อย่างมีนัยสำคัญ
- **Zero Balance Cashout Rate:** บัญชีม้า **61%** vs บัญชีปกติ **31%** — ยืนยันพฤติกรรมดูดเงินออกจนเกลี้ยงบัญชี

ทั้งสองสัญญาณนี้เกินค่า Alert Threshold 50% ในกลุ่มบัญชีม้า ซึ่งหมายความว่าสามารถนำไปใช้เป็นกฎการตรวจจับได้ทันที

---

### กราฟที่ 7 — When: Dwell Time (หน้าต่างการหลีกเลี่ยง 5 นาที)

![Dwell Time Distribution](images/7_dwell_time.png)
*Histogram แสดงการกระจายของ Dwell Time (นาที) หลังจากรับเงินเข้า แยกระหว่างบัญชีม้า (แดง) และบัญชีปกติ (น้ำเงิน) พร้อม Reference Line ที่ 5-Minute Evasion Window*

กราฟนี้ตอบคำถาม **"WHEN are illicit funds moved out of the suspected account?"** และเป็นหลักฐานที่แข็งแกร่งที่สุดของพฤติกรรม Rapid Transit — เงินในบัญชีม้า **54% ถูกโอนออกภายใน 4 นาที** ของการรับ (43 จาก 79 ธุรกรรม) กราฟแสดงให้เห็นชัดว่าบัญชีม้า (สีแดง) กระจุกตัวอยู่ที่ช่วง 1–4 นาที อย่างหนาแน่น ในขณะที่บัญชีปกติ (สีน้ำเงิน) กระจายตัวออกไปในช่วงเวลาที่นานกว่า ยืนยันว่า **Dwell Time < 5 นาที** เป็น Alert Rule ที่ใช้งานได้จริง

---

## 9. ผลการวิเคราะห์ (Key Findings and Insights)

### สรุปผลการวิเคราะห์จากทุก Visualization

| # | Finding | ตัวเลขสำคัญ | นัยสำคัญ |
| :---: | :--- | :--- | :--- |
| 1 | **Class Imbalance รุนแรง** | Mule 2.3% (459/20,000) อัตราส่วน 1:42.6 | จำเป็นต้องใช้ Log Scale และเทคนิค Imbalanced Data |
| 2 | **Spike Ratio คือสัญญาณที่แข็งแกร่งที่สุด** | Mule เฉลี่ย 44x vs Normal 5x | ส่วนใหญ่ของบัญชีม้าเกิน Alert Threshold 10x |
| 3 | **Account Age ≤ 500 วัน คือกลุ่มเสี่ยงหลัก** | Mule กระจุกใน 0–500 วัน | บัญชีใหม่ + Spike Ratio สูง = ความเสี่ยงสูงมาก |
| 4 | **Dormancy Spike** | 77% ของ Mule vs 24% ของ Normal | เกิน Alert Threshold 50% อย่างมีนัยสำคัญ |
| 5 | **Zero Balance Cashout** | 61% ของ Mule vs 31% ของ Normal | ยืนยันพฤติกรรมดูดเงินออกจนหมดบัญชี |
| 6 | **5-Minute Evasion Window** | 54% ของ Mule โอนออกภายใน 4 นาที | หน้าต่างการแทรกแซงแคบมาก ต้องการ Near Real-Time Alert |
| 7 | **ไม่มี Geographic Hotspot เดียว** | ความเสี่ยงกระจายทั่วประเทศ | Geographic Profiling ต้องใช้ร่วมกับ Behavioral Signal เสมอ |

---

## 📝 บทสรุป (Conclusion)

จากการวิเคราะห์ข้อมูล สามารถสรุปได้ว่าบัญชีม้าสามารถระบุได้จากการรวมกันของสัญญาณพฤติกรรม ดังนี้

- บัญชีม้าส่วนใหญ่เป็นบัญชีที่มีอายุ **ไม่เกิน 500 วัน** บ่งชี้ว่ามิจฉาชีพนิยมเปิดบัญชีใหม่เพื่อหลีกเลี่ยงการตรวจจับ
- ค่า Spike Ratio ของบัญชีม้าสูงกว่าบัญชีปกติถึง **~8.8 เท่า** (เฉลี่ย 44x vs 5x) ซึ่งเป็นสัญญาณที่ชัดเจนและวัดผลได้
- เงินในบัญชีม้าถูกโอนออกอย่างรวดเร็ว โดยมี **Dwell Time น้อยกว่า 5 นาที** ในกรณีส่วนใหญ่ ทำให้หน้าต่างการแทรกแซงแคบมาก
- การใช้งาน Device/IP ร่วมกันระหว่างหลายบัญชี เป็นสัญญาณของ **Mule Farm** ที่ดำเนินการอย่างเป็นระบบ
- ไม่มีจังหวัดใดจุดเดียวที่เป็น Hotspot หลัก แสดงว่าเครือข่ายม้ากระจายตัวทั่วประเทศ

---

## 📝 ข้อเสนอแนะและผลกระทบ (Recommendation / Action and Impact)

### Rule-Based Detection Alerts

ควรนำกฎการตรวจจับต่อไปนี้ไปใช้เป็น Near Real-Time Alert ในระบบ Transaction Monitoring ของธนาคาร:

- **Rule 1:** Flag บัญชีใดก็ตามที่มี Spike Ratio เกิน **10 เท่า** ของค่าเฉลี่ย 3 เดือน
- **Rule 2:** Flag ธุรกรรมใดก็ตามที่ Dwell Time ต่ำกว่า **5 นาที** หลังจากรับเงินก้อนใหญ่เข้า
- **Rule 3:** Flag บัญชีที่มีอายุ **ต่ำกว่า 500 วัน** และพร้อมกันกระตุ้น Dormancy Spike และ Zero Balance Cashout

### Operational Response

บัญชีที่ถูก Flag ควรถูกระงับธุรกรรมชั่วคราว (Temporary Transaction Hold) รอการตรวจสอบโดยทีม Fraud Operations ซึ่งช่วยให้สามารถแทรกแซงได้ภายในหน้าต่างการหลบเลี่ยงที่วิกฤต ก่อนที่เงินจะถูกโอนออกไปชั้นถัดไป

### Balancing Security and Customer Experience

เพื่อลด False Positives ควรกำหนดให้ต้องมีการกระตุ้น Flag **อย่างน้อย 2 สัญญาณพร้อมกัน** ก่อนที่จะ Escalate ซึ่งลดความเสี่ยงในการรบกวนลูกค้าที่ถูกต้องตามกฎหมาย ในขณะที่ยังคงรักษาความสามารถในการตรวจจับไว้

### Expected Impact

- ลดการหลีกเลี่ยงของบัญชีม้าภายในหน้าต่าง 5 นาที
- รองรับการปฏิบัติตามข้อกำหนด AML ของธนาคารแห่งประเทศไทย
- ลดความสูญเสียทางการเงินจาก APP Scam

---

## 🚀 วิธีการรันโปรแกรม (How to Run)

```bash
# 1. ติดตั้ง Dependencies
pip install pandas numpy openpyxl faker

# 2. สร้างชุดข้อมูลสังเคราะห์
python src/data_gen.py
# Output: data/mule_account_mock_data.xlsx

# 3. ทำความสะอาดข้อมูล
python src/data_clean.py
# Output: data/mule_data_cleaned.xlsx

# 4. สร้าง Engineered Features
python src/feature_engineering.py
# Output: data/mule_data_features.xlsx

# 5. เปิด Tableau Workbook สำหรับ EDA
# เปิดไฟล์ notebooks/EDA_Mule_Detection.twbx ใน Tableau Desktop
```

---

*Modified from Bill Schmarzo's Machine Learning Canvas and Jasmine Vasandani's Data Science Workflow Canvas for SWU*