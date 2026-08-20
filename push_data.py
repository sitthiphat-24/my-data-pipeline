import pandas as pd
from sqlalchemy import create_engine
import os

# 1. ดึงลิงก์ฐานข้อมูลที่ซ่อนไว้
db_url = os.environ.get('SUPABASE_URL')
engine = create_engine(db_url)

# 2. อ่านไฟล์ CSV (เปลี่ยนชื่อไฟล์ได้ถ้าไม่ได้ชื่อ data.csv)
print("กำลังอ่านไฟล์ CSV...")
df = pd.read_csv('defect_data_21_30.csv')

# (ตัวเลือกเสริม) Clean ข้อมูลเบื้องต้น เช่น ลบแถวที่ว่างทิ้ง
df_clean = df.dropna()

# 3. ส่งข้อมูลเข้า Supabase (แบ่งส่งทีละ 10,000 แถว ป้องกันเน็ตหลุด)
print("เริ่มส่งข้อมูลเข้า Supabase...")
# เปลี่ยนคำว่า 'sensor_data' เป็นชื่อตารางใน Supabase ของคุณ
df_clean.to_sql('piechart', engine, if_exists='append', index=False, chunksize=10000)

print("🚀 ยิงข้อมูลเข้า Supabase สำเร็จเรียบร้อย!")
