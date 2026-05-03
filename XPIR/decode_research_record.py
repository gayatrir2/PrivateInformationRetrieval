#!/usr/bin/env python3
import struct, os, sys, glob, json

RESEARCH_COLS = ['meanbp','hrt','resp','temp','pafi','alb','bili',
                 'crea','sod','ph','glucose','bun','wblc','urine',
                 'scoma','age','death','diabetes','dementia']

N_VALS      = len(RESEARCH_COLS) * 3   # 19 cols × 3 stats = 57 doubles
RECORD_SIZE = 512                       # padded size on disk
EXPECTED_BYTES = N_VALS * 8            # 456 bytes of actual data

CLIENT_DIR    = os.path.dirname(os.path.abspath(__file__))
RECEPTION     = os.path.join(CLIENT_DIR, 'reception')
INDEX_MAP_PATH = os.path.join(CLIENT_DIR, 'research_index_map.json')

if not os.path.exists(INDEX_MAP_PATH):
    print(f"ERROR: research_index_map.json not found at {INDEX_MAP_PATH}")
    sys.exit(1)

with open(INDEX_MAP_PATH) as f:
    index_map = json.load(f)

def show_index():
    print()
    print("=" * 55)
    print("  RESEARCH QUERY INDEX")
    print("  (Enter one of these numbers in pir_client)")
    print("=" * 55)
    categories = {}
    for i, name in sorted(index_map.items(), key=lambda x: int(x[0])):
        prefix = name.split(":")[0].strip()
        categories.setdefault(prefix, []).append((i, name))
    for prefix, items in categories.items():
        print(f"\n  ── {prefix} ──")
        for i, name in items:
            print(f"    [{i:>2}]  {name}")
    print()

def decode(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < EXPECTED_BYTES:
        print(f"ERROR: File is {len(data)} bytes, expected at least {EXPECTED_BYTES} bytes.")
        print("This looks like a patient record, not a research record.")
        print("Make sure you ran pir_client against the RESEARCH server (port 5050), not the patient server (port 1234).")
        return

    values = struct.unpack(f'{N_VALS}d', data[:EXPECTED_BYTES])

    fname = os.path.basename(filepath)
    label = index_map.get(fname, f"Record {fname}")

    print()
    print("=" * 60)
    print(f"  RESEARCHER QUERY RESULT  (PII-free)")
    print(f"  Query: {label}")
    print("=" * 60)
    print(f"  {'Attribute':<14} {'Mean':>10} {'Std':>10} {'N Patients':>12}")
    print(f"  {'-'*50}")
    for i, col in enumerate(RESEARCH_COLS):
        mean = values[i*3]
        std  = values[i*3+1]
        n    = int(round(values[i*3+2]))
        if col == 'death':
            print(f"  {col:<14} {mean*100:>9.1f}% {std*100:>9.1f}% {n:>12}  (mortality rate)")
        elif col in ['diabetes', 'dementia']:
            print(f"  {col:<14} {mean*100:>9.1f}% {std*100:>9.1f}% {n:>12}  (prevalence)")
        else:
            print(f"  {col:<14} {mean:>10.3f} {std:>10.3f} {n:>12}")
    print("=" * 60)
    print()

if __name__ == '__main__':

    if '--index' in sys.argv and len(sys.argv) == 2:
        show_index()
        sys.exit(0)

    if '--index' in sys.argv:
        show_index()

    args = [a for a in sys.argv[1:] if a != '--index']

    if args:
        fname = args[0]
        path = os.path.join(RECEPTION, fname) if not os.path.isabs(fname) else fname
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}")
            print(f"Files in reception/: {os.listdir(RECEPTION) if os.path.exists(RECEPTION) else 'folder missing'}")
            sys.exit(1)
        decode(path)
    else:
        if not os.path.exists(RECEPTION):
            print(f"ERROR: reception/ folder not found. Run pir_client first.")
            sys.exit(1)
        files = sorted(glob.glob(os.path.join(RECEPTION, '*')),
                       key=os.path.getmtime, reverse=True)
        if not files:
            print("No files in reception/. Run pir_client -p 5050 first.")
            sys.exit(1)
        print(f"Auto-detected latest file: {os.path.basename(files[0])}")
        decode(files[0])
