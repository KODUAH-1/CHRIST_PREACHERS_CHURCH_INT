import pandas as pd
import os

f = r"F:\ADMI RECORDS.xlsx"

xl = pd.ExcelFile(f)

out = []

for sheet in xl.sheet_names:
    print("\n" + "=" * 100)
    print("SHEET:", sheet)
    print("=" * 100)

    try:
        d = pd.read_excel(f, sheet_name=sheet, header=None)

        print("SHAPE:", d.shape)

        # Print first 15 rows with every non-empty cell
        limit = min(15, len(d))

        for i in range(limit):
            values = []

            for j, v in enumerate(d.iloc[i]):
                if pd.notna(v) and str(v).strip() != "":
                    values.append(f"{j}={str(v).strip()}")

            if values:
                line = f"ROW {i}: " + " | ".join(values)
                print(line)
                out.append(f"[{sheet}] {line}")

    except Exception as e:
        print("ERROR:", e)
        out.append(f"[{sheet}] ERROR: {e}")

# Save inspection to file
report = ".\ADMIN_RECORDS_STRUCTURE.txt"

with open(report, "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(out))

print("\n" + "=" * 100)
print("STRUCTURE REPORT SAVED TO:")
print(os.path.abspath(report))
print("=" * 100)
