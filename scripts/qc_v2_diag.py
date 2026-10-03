import pandas as pd
import numpy as np

D = pd.read_parquet("data/wl_2019_2023.parquet")
D = D.sort_values(["station","timestamp"]).copy()

targets = [
 ("THA008","2020-04-25"),
 ("THA008","2020-10-21"),
 ("THA010","2021-01-17"),
 ("THA010","2021-10-30"),
 ("THA010","2023-05-26"),
 ("THA006","2023-02-12"),
]

print("=== TARGET WINDOWS ===")

for station, day in targets:
    t = pd.Timestamp(day)
    x = D[
        (D.station == station) &
        (D.timestamp >= t-pd.Timedelta("6h")) &
        (D.timestamp <  t+pd.Timedelta("30h"))
    ][["timestamp","station","water_lv"]]

    print("\n###",station,day)
    print(x.to_string(index=False))

print("\n=== HOURLY ROBUST CHECK ===")

H = (
    D.set_index("timestamp")
     .groupby("station").water_lv
     .resample("1h").agg(["median","count","min","max"])
     .reset_index()
)

for station, day in targets:
    t=pd.Timestamp(day)
    x=H[
       (H.station==station) &
       (H.timestamp>=t-pd.Timedelta("6h")) &
       (H.timestamp<t+pd.Timedelta("30h"))
    ]

    print("\n###",station,day)
    print(x.to_string(index=False))
