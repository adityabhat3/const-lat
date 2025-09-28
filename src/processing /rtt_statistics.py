import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV data
csv_file = "../../data/csv/pointwise_statistics.csv"
df = pd.read_csv(csv_file, keep_default_na=False, low_memory=False)

# Convert timestamp to datetime for easier temporal analysis
df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
df["Day"] = pd.to_datetime(df["Day"])
df["Destination ASN"] = df["Destination ASN"].astype(str)
df["Source ASN"] = df["Source ASN"].astype(str)

# -------------------------------
# 1. Identify Spike Measurements
# -------------------------------
# Spike condition: Normalized Median RTT >= 10
spikes = df[df["Spike (Normalized >= 10)"] == True]

print("Total measurements:", len(df))
print("Measurements with spikes:", len(spikes))
print("Fraction with spikes: {:.2%}".format(len(spikes) / len(df)))

# ---------------------------------------------------------
# 2. Analyze Distribution of Spikes by Source ASN (Vantage)
# ---------------------------------------------------------
asn_distribution = spikes["Source ASN"].value_counts()
print("\nSpike distribution by Source ASN:")
print(asn_distribution)

# -----------------------------------------------------------
# 3. Analyze Distribution of Spikes by Destination (Targets)
# -----------------------------------------------------------
dest_asn_distribution = spikes["Destination ASN"].value_counts()
# dest_asn_distribution = spikes.groupby('Destination ASN').sum()
# dest_asn_distribution = spikes['Destination ASN'].value_counts().groupby(level=0).sum().sort_values(ascending=False)
print("\nSpike distribution by Destination ASN:")
print(dest_asn_distribution)

# -------------------------------------------------------
# 4. Temporal Analysis: Are spikes closely spaced in time?
# -------------------------------------------------------
spikes_by_day = spikes.groupby(spikes["Day"].dt.date).size()
print("\nSpike counts by day:")
print(spikes_by_day)

# ---------------------------------------------------------------------
# 5. Classify RTTs based on ASes: Inter-AS vs Intra-AS
# ---------------------------------------------------------------------
# Create a new column: True if Source ASN != Destination ASN (Inter-AS)
# / is this correct?
df["Inter_AS"] = (
    (df["Source ASN"] != df["Destination ASN"])
    & (df["Source ASN"] != "")
    & (df["Destination ASN"] != "")
)

spike_inter_as = df[(df["Spike (Normalized >= 10)"] == True) & (df["Inter_AS"])]
spike_intra_as = df[(df["Spike (Normalized >= 10)"] == True) & (~df["Inter_AS"])]

print("\nNumber of spikes in Inter-AS paths:", len(spike_inter_as))
print("Number of spikes in Intra-AS paths:", len(spike_intra_as))

# /just like above make a new column for inter_as and intra_as
# -------------------------------------------------------

intra_as = df[
    (df["Source ASN"] == df["Destination ASN"])
    & (df["Source ASN"] != "")
    & (df["Destination ASN"] != "")
]
inter_as = df[
    (df["Source ASN"] != df["Destination ASN"])
    & (df["Source ASN"] != "")
    & (df["Destination ASN"] != "")
]

print(intra_as)
print("\nNumber of Intra-AS paths:", len(intra_as))
print("Number of Inter-AS paths:", len(inter_as))

print(intra_as["Source ASN"].head(), intra_as["Destination ASN"].head())

# ----------------------------------------------------------------------
# 6. Analyze Spike Distribution by Continents (Source and Destination)
# ----------------------------------------------------------------------
spikes_by_continent = spikes.groupby(
    ["Source Continent", "Destination Continent"]
).size()
print("\nSpike distribution by continents (Source, Destination):")
print(spikes_by_continent)
print(spikes_by_continent.loc[("NA", "NA")])


# ---------------------------------------------------
# Optional: Plot CDFs for Normalized Median RTTs
# ---------------------------------------------------
def plot_cdf(data, label):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    plt.plot(sorted_data, cdf, label=label)


plt.figure(figsize=(10, 6))
plot_cdf(df["Normalized Median RTT"], "All Measurements")
plot_cdf(spikes["Normalized Median RTT"], "Spike Measurements")
plt.xlabel("Normalized Median RTT")
plt.ylabel("CDF")
plt.title("CDF of Normalized Median RTT")
plt.legend()
plt.grid(True)
plt.show()
