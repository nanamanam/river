import zipfile,io
import pandas as pd

S=["THA006","THA007","THA008","THA009","THA010","THA011"]
A=[]

for y in range(2019,2024):
    with zipfile.ZipFile(f"raw/water_level/{y}.zip") as z:
        for s in S:
            fs=[n for n in z.namelist()
                if n.upper().endswith("/"+s+".CSV")]

            print(y,s,"months",len(fs))

            for f in fs:
                d=pd.read_csv(io.BytesIO(z.read(f)),low_memory=False)

                t=pd.to_datetime(
                    d["date"].astype(str)+" "+d["time"].astype(str),
                    errors="coerce"
                )

                w=pd.to_numeric(d["water_lv"],errors="coerce")

                A.append(pd.DataFrame({
                    "timestamp":t,
                    "station":s,
                    "water_lv":w
                }))

D=pd.concat(A,ignore_index=True)
D=D.dropna(subset=["timestamp"])
D=D.sort_values(["station","timestamp"])

dup=D.duplicated(["station","timestamp"]).sum()
D=D.drop_duplicates(["station","timestamp"],keep="last")

D.to_parquet("data/wl_2019_2023.parquet",index=False)

print("\n=== RESULT ===")
print("ROWS",f"{len(D):,}")
print("DUPLICATES REMOVED",dup)
print("START",D.timestamp.min())
print("END",D.timestamp.max())

print("\n=== STATIONS ===")
print(D.groupby("station").agg(
    rows=("water_lv","size"),
    valid=("water_lv","count"),
    min=("water_lv","min"),
    max=("water_lv","max")
).to_string())

print("\nSAVED data/wl_2019_2023.parquet")
