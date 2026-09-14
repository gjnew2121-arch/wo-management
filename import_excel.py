"""
IMPORT SCRIPT — διαβάζει το Excel και το ανεβάζει στο Firestore
----------------------------------------------------------------
1. pip install firebase-admin openpyxl pandas
2. Βάλε serviceAccountKey.json στον ίδιο φάκελο
3. py import_excel.py
"""

import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import math

EXCEL_FILE   = "WORK_ORDER_LIST__12_.xlsx"
SERVICE_ACCT = "serviceAccountKey.json"

# GainJet χρόνια
GAINJET_SHEETS = ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018']
GAINJET_COLLECTION = "gainjet_workOrders"

# GJet SM WO
GJET_SHEETS = ['GJET SM WO']
GJET_COLLECTION = "gjet_workOrders"

cred = credentials.Certificate(SERVICE_ACCT)
firebase_admin.initialize_app(cred)
db = firestore.client()

def clean(val):
    if val is None: return ""
    if isinstance(val, float) and math.isnan(val): return ""
    if isinstance(val, datetime): return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    return "" if s.lower() == "nan" else s

def parse_status(row):
    s = clean(row.get("STATUS", "")).upper()
    return s if s in ("OPEN","CLOSED","CNX","PENDING") else "OPEN"

def parse_yesno(row, key):
    v = clean(row.get(key, "")).upper()
    if v == "YES": return "YES"
    if "PENDING" in v: return "PENDING"
    return ""

def import_sheets(sheets, collection):
    total = 0
    errors = 0
    for sheet in sheets:
        print(f"\n📋 Sheet: {sheet}")
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=0, dtype=str)
        except Exception as e:
            print(f"  ⚠️  Skipping: {e}"); continue

        df.columns = [str(c).strip() for c in df.columns]

        # Βρες το year
        try:
            year = int(sheet)
        except:
            year = 0

        batch = db.batch()
        count = 0

        for _, row in df.iterrows():
            wo_num = clean(row.get("WO NUM", ""))
            if not wo_num or wo_num.upper() in ("WO NUM","NAN",""): continue
            try:
                ref = db.collection(collection).document()
                batch.set(ref, {
                    "wo_number":          wo_num,
                    "issue_date":         clean(row.get("ISSUE DATE", "")),
                    "due_limit":          clean(row.get("DUE LIMIT (DATE/HRS/CLS) ", row.get("DUE LIMIT (DATE/HRS/CLS)", ""))),
                    "aircraft":           clean(row.get("AIRCRAFT", "")),
                    "issued_by":          clean(row.get("ISSUED BY (TAB ADDED 01/01/2018)", row.get("ISSUED BY", ""))),
                    "part_145":           clean(row.get("PART 145", "")),
                    "description":        clean(row.get("DESCRIPTION", "")),
                    "closed_date":        clean(row.get("CLOSED DATE", "")),
                    "cmp_updated":        clean(row.get("CMP/ TRXL UPDATED", row.get("CMP UPDATED", row.get("CMP/ TRXL UPDATED ", "")))),
                    "status":             parse_status(row),
                    "package_received":   parse_yesno(row, "ORIGINAL PACKAGE RECEIVED"),
                    "wp_filed":           parse_yesno(row, "WP FILED"),
                    "location":           clean(row.get("LOCATION", "")),
                    "cmp_component_list": clean(row.get("CMP/TRXL COMPONENT LIST UPDATED (IF APPLICABLE)", "")),
                    "form_completed":     clean(row.get("FORM GJ/M-28 COMPLETED    (IF REQUIRED)", "")),
                    "entered_by":         clean(row.get("ENTERED BY", "")),
                    "remarks":            clean(row.get("REMARKS (TAB ENTERED 20/11/2019)", row.get("REMARKS", ""))),
                    "year":               year,
                    "created_at":         firestore.SERVER_TIMESTAMP,
                    "updated_at":         firestore.SERVER_TIMESTAMP,
                })
                count += 1
                if count % 400 == 0:
                    batch.commit(); batch = db.batch()
                    print(f"  ✅ {count} committed…")
            except Exception as e:
                errors += 1; print(f"  ❌ {wo_num}: {e}")

        if count % 400 != 0: batch.commit()
        total += count
        print(f"  ✅ {count} records → {collection}")
    return total, errors

print("=" * 50)
print("GAINJET Import")
print("=" * 50)
t1, e1 = import_sheets(GAINJET_SHEETS, GAINJET_COLLECTION)

print("\n" + "=" * 50)
print("GJET SM WO Import")
print("=" * 50)
t2, e2 = import_sheets(GJET_SHEETS, GJET_COLLECTION)

print(f"\n🎉 Done!")
print(f"   GAINJET: {t1} imported")
print(f"   GJET:    {t2} imported")
print(f"   Errors:  {e1+e2}")
