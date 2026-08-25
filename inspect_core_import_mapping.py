import pandas as pd

FILE = r"F:\ADMI RECORDS.xlsx"

TARGETS = [
    "N. FUND",
    "EV. FUND",
    "ATTENDANCE  REGISTER"
]

print()
print("=" * 100)
print("CORE IMPORT MAPPING INSPECTION")
print("=" * 100)

xl = pd.ExcelFile(FILE)

for sheet in TARGETS:

    print()
    print("=" * 100)
    print("SHEET:", repr(sheet))
    print("=" * 100)

    if sheet not in xl.sheet_names:
        print("NOT FOUND")
        continue

    df = pd.read_excel(
        FILE,
        sheet_name=sheet,
        header=None
    )

    print("SHAPE:", df.shape)

    print()
    print("NON-EMPTY ROWS:")

    shown = 0

    for i, row in df.iterrows():

        values = []

        for j, value in enumerate(row.tolist()):

            if pd.isna(value):
                continue

            text = str(value).strip()

            if text:
                values.append(
                    "{}={}".format(j, text)
                )

        if values:
            print(
                "ROW {:>4}: {}".format(
                    i,
                    " | ".join(values)
                )
            )

            shown += 1

            if shown >= 120:
                print("... FIRST 120 NON-EMPTY ROWS SHOWN ...")
                break

print()
print("=" * 100)
print("CORE IMPORT MAPPING INSPECTION COMPLETE")
print("=" * 100)
