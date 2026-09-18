#!/usr/bin/env python3
"""
Import GainJet & GJet Excel data → Firestore
Usage: python import_excel.py <path_to_excel.xlsx>
"""

import sys, re, math
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# ── INIT ─────────────────────────────────────────────────────────────────────
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "workorders.xlsx"

# ── GAINJET SHEETS ────────────────────────────────────────────────────────────
GAINJET_SHEETS = ['2026','2025','2024','2023','2022','2021','2020','2019','2018']
GJET_SHEETS    = ['GJET SM WO']

# ── COLUMN FINDER ─────────────────────────────────────────────────────────────
def norm(s):
    return re.sub(r'\s+', ' ', str(s).strip().upper())

def find_col(df, *candidates):
    cols = {norm(c): c for c in df.columns}
    for cand in candidates:
        key = norm(cand)
        if key in cols:
            return cols[key]
    # partial match
    for cand in candidates:
        key = norm(cand)
        for col_norm, col_orig in cols.items():
            if key in col_norm or col_norm in key:
                return col_orig
    return None

def safe(val):
    if val is None: return ''
    if isinstance(val, float) and math.isnan(val): return ''
    return str(val).strip()

def parse_date(val):
    if not val or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return pd.to_datetime(val).strftime('%Y-%m-%d')
    except:
        return safe(val) or None

# ── IMPORT GAINJET ────────────────────────────────────────────────────────────
def import_gainjet():
    col_ref = db.collection('gainjet_workOrders')
    print("Deleting existing gainjet_workOrders...")
    for d in col_ref.stream():
        d.reference.delete()

    all_records = []
    for sheet in GAINJET_SHEETS:
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=0)
        except Exception as e:
            print(f"  Sheet '{sheet}' not found or error: {e}")
            continue
        # Normalize column names
        df.columns = [re.sub(r'\s+', ' ', str(c).strip()) for c in df.columns]
        print(f"  Sheet '{sheet}': {len(df)} rows, cols: {list(df.columns)}")

        for _, row in df.iterrows():
            aa_col     = find_col(df, 'A/A', 'AA', 'Α/Α', 'No', 'NUM')
            wo_col     = find_col(df, 'WO NUM', 'WO NUMBER', 'WO')
            date_col   = find_col(df, 'ISSUE DATE', 'DATE ISSUED', 'DATE')
            due_col    = find_col(df, 'DUE LIMIT', 'DUE')
            ac_col     = find_col(df, 'AIRCRAFT', 'A/C')
            by_col     = find_col(df, 'ISSUED BY', 'ISSUED')
            p145_col   = find_col(df, 'PART 145')
            desc_col   = find_col(df, 'DESCRIPTION', 'DESC')
            closed_col = find_col(df, 'CLOSED DATE', 'CLOSE DATE', 'CLOSED')
            cmp_col    = find_col(df, 'CMP/TRXL', 'CMP TRXL', 'CMP')
            status_col = find_col(df, 'STATUS')
            pkg_col    = find_col(df, 'PKG RCV', 'PKG')
            wp_col     = find_col(df, 'WP FILED', 'WP')
            loc_col    = find_col(df, 'LOCATION', 'LOC')
            cmplist_col= find_col(df, 'CMP LIST', 'COMP LIST')
            m28_col    = find_col(df, 'FORM M-28', 'M-28', 'M28')
            entby_col  = find_col(df, 'ENTERED BY', 'ENTRY BY')
            rem_col    = find_col(df, 'REMARKS', 'REM')

            # Parse serial number (A/A)
            aa_raw = safe(row[aa_col]) if aa_col else ''
            try:
                serial_number = int(float(aa_raw)) if aa_raw else None
            except:
                serial_number = None

            wo_num = safe(row[wo_col]) if wo_col else ''
            if not wo_num and not serial_number:
                continue  # skip empty rows

            status_raw = safe(row[status_col]).upper() if status_col else ''
            if 'CNX' in status_raw or 'CANCEL' in status_raw:
                status = 'CNX'
            elif 'CLOSE' in status_raw or 'CMP' in status_raw or 'COMP' in status_raw:
                status = 'CLOSED'
            else:
                status = 'OPEN'

            record = {
                'serial_number': serial_number,
                'wo_number':     wo_num,
                'issue_date':    parse_date(row[date_col])   if date_col   else None,
                'due_limit':     safe(row[due_col])           if due_col    else '',
                'aircraft':      safe(row[ac_col])            if ac_col     else '',
                'issued_by':     safe(row[by_col])            if by_col     else '',
                'part_145':      safe(row[p145_col])          if p145_col   else '',
                'description':   safe(row[desc_col])          if desc_col   else '',
                'closed_date':   parse_date(row[closed_col])  if closed_col else None,
                'cmp_trxl':      safe(row[cmp_col])           if cmp_col    else '',
                'status':        status,
                'pkg_rcv':       safe(row[pkg_col])           if pkg_col    else '',
                'wp_filed':      safe(row[wp_col])            if wp_col     else '',
                'location':      safe(row[loc_col])           if loc_col    else '',
                'cmp_list':      safe(row[cmplist_col])       if cmplist_col else '',
                'form_m28':      safe(row[m28_col])           if m28_col    else '',
                'entered_by':    safe(row[entby_col])         if entby_col  else '',
                'remarks':       safe(row[rem_col])           if rem_col    else '',
                'source_sheet':  sheet,
            }
            all_records.append(record)

    print(f"Importing {len(all_records)} GainJet records...")
    for rec in all_records:
        col_ref.add(rec)
    print(f"  Done: {len(all_records)} records imported to gainjet_workOrders")


# ── IMPORT GJET ───────────────────────────────────────────────────────────────
def import_gjet():
    col_ref = db.collection('gjet_workOrders')
    print("Deleting existing gjet_workOrders...")
    for d in col_ref.stream():
        d.reference.delete()

    all_records = []
    for sheet in GJET_SHEETS:
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=0)
        except Exception as e:
            print(f"  Sheet '{sheet}' not found or error: {e}")
            continue
        df.columns = [re.sub(r'\s+', ' ', str(c).strip()) for c in df.columns]
        print(f"  Sheet '{sheet}': {len(df)} rows, cols: {list(df.columns)}")

        for _, row in df.iterrows():
            aa_col     = find_col(df, 'A/A', 'AA', 'Α/Α', 'No', 'NUM')
            wo_col     = find_col(df, 'WO NUM', 'WO NUMBER', 'WO')
            date_col   = find_col(df, 'ISSUE DATE', 'DATE ISSUED', 'DATE')
            due_col    = find_col(df, 'DUE LIMIT', 'DUE')
            ac_col     = find_col(df, 'AIRCRAFT', 'A/C')
            by_col     = find_col(df, 'ISSUED BY', 'ISSUED')
            p145_col   = find_col(df, 'PART 145')
            desc_col   = find_col(df, 'DESCRIPTION', 'DESC')
            closed_col = find_col(df, 'CLOSED DATE', 'CLOSE DATE', 'CLOSED')
            cmp_col    = find_col(df, 'CMP/TRXL', 'CMP TRXL', 'CMP')
            status_col = find_col(df, 'STATUS')
            pkg_col    = find_col(df, 'PKG RCV', 'PKG')
            wp_col     = find_col(df, 'WP FILED', 'WP')
            loc_col    = find_col(df, 'LOCATION', 'LOC')
            cmplist_col= find_col(df, 'CMP LIST', 'COMP LIST')
            m28_col    = find_col(df, 'FORM M-28', 'M-28', 'M28')
            entby_col  = find_col(df, 'ENTERED BY', 'ENTRY BY')
            rem_col    = find_col(df, 'REMARKS', 'REM')

            aa_raw = safe(row[aa_col]) if aa_col else ''
            try:
                serial_number = int(float(aa_raw)) if aa_raw else None
            except:
                serial_number = None

            wo_num = safe(row[wo_col]) if wo_col else ''
            if not wo_num and not serial_number:
                continue

            status_raw = safe(row[status_col]).upper() if status_col else ''
            if 'CNX' in status_raw or 'CANCEL' in status_raw:
                status = 'CNX'
            elif 'CLOSE' in status_raw or 'CMP' in status_raw or 'COMP' in status_raw:
                status = 'CLOSED'
            else:
                status = 'OPEN'

            record = {
                'serial_number': serial_number,
                'wo_number':     wo_num,
                'issue_date':    parse_date(row[date_col])   if date_col   else None,
                'due_limit':     safe(row[due_col])           if due_col    else '',
                'aircraft':      safe(row[ac_col])            if ac_col     else '',
                'issued_by':     safe(row[by_col])            if by_col     else '',
                'part_145':      safe(row[p145_col])          if p145_col   else '',
                'description':   safe(row[desc_col])          if desc_col   else '',
                'closed_date':   parse_date(row[closed_col])  if closed_col else None,
                'cmp_trxl':      safe(row[cmp_col])           if cmp_col    else '',
                'status':        status,
                'pkg_rcv':       safe(row[pkg_col])           if pkg_col    else '',
                'wp_filed':      safe(row[wp_col])            if wp_col     else '',
                'location':      safe(row[loc_col])           if loc_col    else '',
                'cmp_list':      safe(row[cmplist_col])       if cmplist_col else '',
                'form_m28':      safe(row[m28_col])           if m28_col    else '',
                'entered_by':    safe(row[entby_col])         if entby_col  else '',
                'remarks':       safe(row[rem_col])           if rem_col    else '',
                'source_sheet':  sheet,
            }
            all_records.append(record)

    print(f"Importing {len(all_records)} GJet records...")
    for rec in all_records:
        col_ref.add(rec)
    print(f"  Done: {len(all_records)} records imported to gjet_workOrders")


if __name__ == '__main__':
    import_gainjet()
    import_gjet()
    print("\n✅ Import complete!")
