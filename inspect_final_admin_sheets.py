import pandas as pd

f = r"F:\ADMI RECORDS.xlsx"

sheets = [
    "rec",
    "Sheet1",
    "Payment analysis",
    "EVG FUND REPORT",
    "ATTENDANCE  REGISTER",
    "TRANSFERS",
    "B. Sheet",
    "BAPTISM",
    "RENTALS",
    "ADMI EXPENSES",
    "AIR CON FUNDRAISING",
    "NEW COMMERS",
    " STATEMENT OF ACCOUNT",
    "Hubtel momo transfer",
    "MOMO-SOWUTUOM"
]

for sheet in sheets:

    print("\n" + "=" * 120)
    print("SHEET:", repr(sheet))
    print("=" * 120)

    try:
        d = pd.read_excel(f, sheet_name=sheet, header=None)

        print("SHAPE:", d.shape)

        shown = 0

        for i in range(len(d)):

            values = []

            for j, v in enumerate(d.iloc[i]):

                if pd.notna(v) and str(v).strip() != "":
                    values.append(f"{j}={str(v).strip()}")

            if values:
                print(f"ROW {i}: " + " | ".join(values))
                shown += 1

                if shown >= 25:
                    break

    except Exception as e:
        print("ERROR:", e)

print("\n" + "=" * 120)
print("TARGETED INSPECTION COMPLETE")
print("=" * 120)
