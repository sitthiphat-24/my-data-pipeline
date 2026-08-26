import pandas as pd
from sqlalchemy import create_engine
import os
from datetime import datetime
import pytz 

# 1. เชื่อมต่อฐานข้อมูล (ทำครั้งเดียวใช้งานได้ตลอด)
db_url = os.environ.get('SUPABASE_URL')
engine = create_engine(db_url)

# 2. หาวันที่ของ "วันนี้" (ทำครั้งเดียว)
tz = pytz.timezone('Asia/Bangkok')
today_date = datetime.now(tz).strftime('%Y-%m-%d')
print(f"วันที่รันระบบวันนี้คือ: {today_date}")

# ---------------------------------------------------------
# สร้างฟังก์ชันสำหรับจัดการไฟล์ CSV คลีนข้อมูล และส่งเข้า Supabase
# ---------------------------------------------------------
def process_and_upload(file_name, table_name, time_column):
    print(f"\n--- เริ่มประมวลผลไฟล์: {file_name} ---")
    try:
        # อ่านและคลีนไฟล์ CSV
        
        df = pd.read_csv(file_name)
        # ==========================================
        # แยกวิธี Clean Data ตามชื่อตาราง
        # ==========================================
        if table_name == 'dssa-defect-report':
            df_clean["defect_code"] = df_clean["defect_code"].astype(str).str.strip()
            df_clean["defect_code"] = df_clean["defect_code"].replace(["none", "None", "NULL", "null", "", "nan"], "None")
            df_clean["defect_code"] = df_clean["defect_code"].replace(r"^\s+$", "None", regex=True)
            df_clean = df_clean[df_clean["tab"] != " "]
            df_clean["tab"] = df_clean["tab"].astype(str).str.upper()
            df_clean = df.dropna()
            df_clean = df.drop_duplicates()
            print("✅ คลีนข้อมูลตาราง {table_name}")
            
        elif table_name == 'crst-defect-report':
            df_clean["sub_category"] = df_clean["sub_category"].astype(str).str.strip()
            df_clean["sub_category"] = df_clean["sub_category"].replace(["none", "None", "NULL", "null", "", "nan"],"None")
            df_clean["sub_category"] = df_clean["sub_category"].replace(r"^\s+$", "None", regex=True)
            df_clean = df_clean[df_clean["tab"] != " "]
            df_clean["tab"] = df_clean["tab"].astype(str).str.upper()
            df_clean = df.dropna()
            df_clean = df.drop_duplicates()
            print("✅ คลีนข้อมูลตาราง {table_name}")
            
        else:
            # ตารางอื่นๆ (เผื่อไว้ในอนาคต): ใช้ค่าเริ่มต้นคือคลีนทั้งหมด
            df_clean = df.dropna()
            print(f"✅ คลีนข้อมูลตาราง {table_name} ด้วยค่าเริ่มต้น")
        # ==========================================

        # 3. ขั้นตอนการกรองวันที่ (ใช้เหมือนกันทุกตาราง)
        if time_column not in df_clean.columns:
            print(f"❌ ไม่พบคอลัมน์เวลา '{time_column}' ข้ามการทำงานไฟล์นี้")
            return

        
        # กรองเอาเฉพาะข้อมูลของ "วันนี้"
        df_clean[time_column] = df_clean[time_column].astype(str)
        df_today = df_clean[df_clean[time_column].str.startswith(today_date)]

        # ส่งข้อมูลเข้า Supabase
        if len(df_today) > 0:
            print(f"พบข้อมูลจำนวน {len(df_today)} แถว! กำลังส่งเข้าตาราง '{table_name}'...")
            df_today.to_sql(table_name, engine, if_exists='append', index=False, chunksize=10000)
            print(f"🚀 ส่งข้อมูลเข้าตาราง {table_name} สำเร็จเรียบร้อย!")
        else:
            print(f"✨ วันนี้ไม่มีข้อมูลใหม่ในไฟล์ {file_name} เลยไม่ได้ส่งอะไรไปครับ")
            
    except FileNotFoundError:
        print(f"❌ หาไฟล์ {file_name} ไม่พบ กรุณาตรวจสอบชื่อไฟล์อีกครั้ง")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดกับไฟล์ {file_name}: {e}")


# ---------------------------------------------------------
# 3. สั่งรันการทำงาน (เรียกใช้ฟังก์ชัน)
# ---------------------------------------------------------

# ไฟล์ที่ 1: ตาราง Defect (งานเดิมของคุณ)
process_and_upload(
    file_name='defect_data_21_30.csv', 
    table_name='dssa-defect-report', 
    time_column='defect_date'
)

# ไฟล์ที่ 2: ตารางใหม่ที่คุณต้องการเพิ่ม (แก้ชื่อให้ตรงกับของคุณ)
process_and_upload(
    file_name='crst-defect-report.csv',       
    table_name='crst-defect-report',        
    time_column='date'         
)
