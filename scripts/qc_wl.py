import pandas as pd
import numpy as np

D = pd.read_parquet("data/wl_2019_2023.parquet")
D = D.sort_values(["station", "timestamp"]).copy()

D["raw_water_lv"] = D.water_lv
D["qc_spike"] = False

for station, idx in D.groupby("station").groups.items():
    x = D.loc[idx].sort_values("timestamp")

    prev = x.water_lv.shift(1)
    nxt = x.water_lv.shift(-1)

    dt_prev = x.timestamp.diff().dt.total_seconds()
    dt_next = (
        x.timestamp.shift(-1) - x.timestamp
    ).dt.total_seconds()

    spike = (
        ((prev - nxt).abs() <= 0.30)
        & ((x.water_lv - prev).abs() > 1.0)
        & ((x.water_lv - nxt).abs() > 1.0)
        & (dt_prev == 600)
        & (dt_next == 600)
    )

    D.loc[x.index[spike], "qc_spike"] = True

F = D[D.qc_spike]

print("=== SPIKES BY STATION ===")
print(F.groupby("station").size())

print("\n=== FLAGGED SAMPLE ===")
print(
    F[["timestamp", "station", "water_lv"]]
    .head(100)
    .to_string(index=False)
)

print("\nTOTAL FLAGGED:", len(F))

D.loc[D.qc_spike, "water_lv"] = np.nan
D.to_parquet("wl_clean_v1.parquet", index=False)

print("\nSAVED wl_clean_v1.parquet")
