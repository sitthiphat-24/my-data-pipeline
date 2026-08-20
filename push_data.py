
import pandas as pd
from sqlalchemy import create_engine
import os
from datetime import datetime
import pytz # ใช้สำหรับตั้งโซนเวลาให้แม่นยำ

# 1. เชื่อมต่อฐานข้อมูล
db_url = os.environ.get('SUPABASE_URL')
engine = create_engine(db_url)

# 2. อ่านไฟล์ CSV
print("กำลังอ่านไฟล์ CSV...")
df = pd.read_csv('defect_data_21_30.csv')
df_clean = df.dropna()

# 3. หาวันที่ของ "วันนี้" (ตั้งโซนเวลาเป็นเอเชีย/กรุงเทพฯ-สิงคโปร์)
# เวลาในเซิร์ฟเวอร์ GitHub เป็น UTC เราต้องปรับให้ตรงกับเวลาบ้านเรา
tz = pytz.timezone('Asia/Bangkok')
today_date = datetime.now(tz).strftime('%Y-%m-%d')
print(f"วันที่รันระบบวันนี้คือ: {today_date}")

# 4. กรองเอาเฉพาะข้อมูลของ "วันนี้" เท่านั้น
time_column = 'defect_date' # เปลี่ยนชื่อคอลัมน์ให้ตรงกับไฟล์ของคุณ
table_name = 'piechart'  # เปลี่ยนชื่อตารางให้ตรงกับใน Supabase

# แปลงคอลัมน์เวลาเป็นข้อความ และเลือกเฉพาะแถวที่ขึ้นต้นด้วยวันที่ของวันนี้
df_clean[time_column] = df_clean[time_column].astype(str)
df_today = df_clean[df_clean[time_column].str.startswith(today_date)]

# 5. ส่งข้อมูลเข้า Supabase
if len(df_today) > 0:
    print(f"พบข้อมูลของวันที่ {today_date} จำนวน {len(df_today)} แถว! กำลังส่งเข้า Supabase...")
    df_today.to_sql(table_name, engine, if_exists='append', index=False, chunksize=10000)
    print("🚀 ส่งข้อมูลของวันนี้สำเร็จเรียบร้อย!")
else:
    print(f"✨ วันนี้ ({today_date}) ไม่มีข้อมูลเซ็นเซอร์ในไฟล์ CSV เลยไม่ได้ส่งอะไรไปครับ")
