import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import palettable.colorbrewer.qualitative as cbqual
import options
import matplotlib as mpl


def compute_cdf(data):
    data_sorted = np.sort(data)
    N = len(data_sorted)
    cum_prob = np.arange(1, N + 1) / N
    return data_sorted, cum_prob


def load_csv_ccdf(csv_file):
    df = pd.read_csv(
        csv_file, keep_default_na=False, na_values=["nan"], low_memory=False
    )
    df = df.dropna(subset=["hmm_cfr"])
    df["hmm_cfr"] = df["hmm_cfr"].astype(float)

    df["Destination ASN"] = df["Destination ASN"].astype(str)
    df["Source ASN"] = df["Source ASN"].astype(str)
    print(len(df))

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

    print(len(intra_as), len(inter_as))
    print(intra_as)
    intra_as_data, intra_as_cdf = compute_cdf(intra_as["hmm_cfr"])
    inter_as_data, inter_as_cdf = compute_cdf(inter_as["hmm_cfr"])

    return intra_as_data, intra_as_cdf, inter_as_data, inter_as_cdf


def plot_cdf(intra_as_data, intra_as_cdf, inter_as_data, inter_as_cdf, output_file):
    with mpl.rc_context(options.get_basic_conf()):
        fig, ax = plt.subplots(figsize=(options.FIG_W, options.FIG_H))

        ax.plot(
            intra_as_data,
            intra_as_cdf,
            "-",
            linewidth=2.5,
            color=cbqual.Set1_5.mpl_colors[0],
            label="Intra-AS",
        )
        ax.plot(
            inter_as_data,
            inter_as_cdf,
            "-",
            linewidth=2.3,
            color=cbqual.Set1_5.mpl_colors[1],
            label="Inter-AS",
        )

        ax.set_xticks(range(0, 250, 50))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        ax.set(
            xlabel="HMM CFR (hours)",
            xlim=None,  # (-20, 400),
            ylabel="CDF",
        )  # ylim=(-0.1, 1))

        plt.tight_layout()
        ax.legend(loc="lower right", prop={"size": 15})

        ax.grid(which="major", linestyle="dashdot", linewidth=0.4, color="#AEAEAE")
        ax.grid(which="minor", linestyle="dotted", linewidth=0.2, color="#AEAEAE")

        plt.tight_layout()
        plt.savefig(output_file, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    input_csv = "../../data/csv/hmm-as-cfr-ipinfo-statistics.csv"  # Change to actual CSV file path
    output_pdf = "../../data/plots/hmm-as-cfr-ipinfo-cdf.pdf"

    intra_as_data, intra_as_cdf, inter_as_data, inter_as_cdf = load_csv_ccdf(input_csv)
    plot_cdf(intra_as_data, intra_as_cdf, inter_as_data, inter_as_cdf, output_pdf)
