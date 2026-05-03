#!/usr/bin/env python3
import struct
import os
import sys
import glob

pir_cols = ['scoma', 'meanbp', 'hrt', 'resp', 'temp', 'pafi', 'alb', 'bili', 'crea',
            'sod', 'ph', 'glucose', 'bun', 'wblc', 'urine', 'num.co', 'dzgroup',
            'ca', 'diabetes', 'dementia', 'age', 'sex', 'race', 'income', 'edu', 'death']

INCOME_LABELS = {0: 'under $11k', 1: '$11-$25k', 2: '$25-$50k', 3: '>$50k', -1: 'Unknown'}
SEX_LABELS    = {0: 'Female', 1: 'Male'}
CA_LABELS     = {0: 'No cancer', 1: 'Yes', 2: 'Metastatic'}
DEATH_LABELS  = {0: 'Alive', 1: 'Deceased'}

RECEPTION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reception')

def decode_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if len(data) != 208:
        print(f"WARNING: Expected 208 bytes, got {len(data)} bytes")
    values = struct.unpack('26d', data[:208])
    record = dict(zip(pir_cols, values))
    print("=" * 50)
    print(f"  RETRIEVED PATIENT RECORD")
    print(f"  File: {os.path.basename(filepath)}")
    print("=" * 50)
    print(f"  {'Field':<12} {'Value'}")
    print(f"  {'-'*30}")
    for col, val in record.items():
        if col == 'income':
            display = INCOME_LABELS.get(int(round(val)), str(val))
        elif col == 'sex':
            display = SEX_LABELS.get(int(round(val)), str(val))
        elif col == 'ca':
            display = CA_LABELS.get(int(round(val)), str(val))
        elif col == 'death':
            display = DEATH_LABELS.get(int(round(val)), str(val))
        elif col in ['diabetes', 'dementia']:
            display = 'Yes' if round(val) == 1 else 'No'
        else:
            display = f"{val:.4f}" if val != int(val) else str(int(val))
        print(f"  {col:<12}  {display}")
    print("=" * 50)
    return record

def main():
    if len(sys.argv) > 1:
        # Specific file passed as argument
        filepath = sys.argv[1]
        if not os.path.isabs(filepath):
            filepath = os.path.join(RECEPTION_DIR, filepath)
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        decode_file(filepath)
    else:
        # Auto-detect latest file in reception/
        if not os.path.exists(RECEPTION_DIR):
            print(f"Error: reception/ folder not found at {RECEPTION_DIR}")
            print("Run pir_client first to retrieve a record.")
            sys.exit(1)
        files = sorted(glob.glob(os.path.join(RECEPTION_DIR, '*')), key=os.path.getmtime, reverse=True)
        if not files:
            print("No files found in reception/. Run pir_client first.")
            sys.exit(1)
        print(f"Auto-detected latest file: {os.path.basename(files[0])}")
        decode_file(files[0])

if __name__ == '__main__':
    main()
