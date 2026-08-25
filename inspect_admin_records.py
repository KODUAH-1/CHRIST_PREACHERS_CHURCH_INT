import pandas as pd
import os

f = r"F:\ADMI RECORDS.xlsx"

print("\nFILE:", f)
print("EXISTS:", os.path.exists(f))

if not os.path.exists(f):
    raise FileNotFoundError(f"Workbook not found: {f}")

xl = pd.ExcelFile(f)

print("\n========== SHEETS ==========")
for i, s in enumerate(xl.sheet_names):
    print(f"{i}: {s}")

print("\n========== SHEET DIMENSIONS ==========")

for s in xl.sheet_names:
    try:
        d = pd.read_excel(f, sheet_name=s, header=None)
        print(f"{s:<30} ROWS={d.shape[0]:<5} COLS={d.shape[1]}")
    except Exception as e:
        print(f"{s:<30} ERROR: {e}")

print("\n========== YEAR DETECTION ==========")

for s in xl.sheet_names:
    try:
        d = pd.read_excel(f, sheet_name=s, header=None)

        years = set()

        for row in d.itertuples(index=False):
            for v in row:
                if pd.isna(v):
                    continue

                text = str(v)

                for year in ["2024", "2025", "2026"]:
                    if year in text:
                        years.add(year)

        print(f"{s:<30} YEARS FOUND: {sorted(years)}")

    except Exception as e:
        print(f"{s:<30} ERROR: {e}")

print("\n========== END INSPECTION ==========")
