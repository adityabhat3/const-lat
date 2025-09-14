#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#
"""Plot the CDF of Inflation of latencies. Each data point is the Inflation of latencies
observed in a specific timeline.
"""
XLABEL = "Median Latency Inflation"
TICKS = 50
import options
import utils
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import palettable.colorbrewer.qualitative as cbqual
import sys
import pandas as pd
import io
import numpy as np


def open(in_file, mode):
    return io.open(in_file, mode, encoding="utf-8")


def compute_cdf(data):
    data_sorted = np.sort(data)
    N = len(data_sorted)
    cum_prob = np.arange(1, N + 1) / N
    return data_sorted, cum_prob


def compute_ccdf(data):
    data_sorted = np.sort(data)
    N = len(data_sorted)
    cum_prob = 1 - (np.arange(1, N + 1) / N)
    return data_sorted, cum_prob


def compute_value_distribution(data):
    data = np.array(data)  # Ensure data is a NumPy array for efficient processing
    total = len(data)  # Total number of data points

    if total == 0:
        return {"<1": 0, "<10": 0, ">10": 0, ">100": 0}  # Avoid division by zero

    # Compute percentages
    less_than_1 = np.sum(data < 1) / total * 100
    between_1_and_10 = np.sum(data < 10) / total * 100
    greater_than_10 = np.sum(data > 10) / total * 100
    greater_than_100 = np.sum(data > 100) / total * 100

    print("remain", np.sum(data < 1), len(data), len(data) - np.sum(data < 1))
    return {
        "<1": less_than_1,
        "<10": between_1_and_10,
        ">10": greater_than_10,
        ">100": greater_than_100,
    }


def load_csv_ccdf(csv_file, column_label, remove_nan=True, out=sys.stdout):
    df = pd.read_csv(
        csv_file, keep_default_na=False, na_values=["nan"], low_memory=False
    )

    df["Destination ASN"] = df["Destination ASN"].astype(str)
    df["Source ASN"] = df["Source ASN"].astype(str)

    df = df.dropna(
        subset=[
            "Min Inflation V2",
            "Median Inflation V2",
            "90th Percentile Inflation V2",
        ]
    )

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
    both = df

    both_data, both_cdf = compute_cdf(both[column_label])
    intra_data, intra_cdf = compute_cdf(intra_as[column_label])
    inter_data, inter_cdf = compute_cdf(inter_as[column_label])

    print("both", compute_value_distribution(both_data))
    print("intra", compute_value_distribution(intra_data))
    print("inter", compute_value_distribution(inter_data))
    return intra_data, intra_cdf, inter_data, inter_cdf, both_data, both_cdf


def gen_plot(
    intra_data,
    intra_cdf,
    inter_data,
    inter_cdf,
    both_data,
    both_cdf,
    out_file,
    show_plot=False,
):
    with mpl.rc_context(options.get_basic_conf()):
        fig, ax = plt.subplots(figsize=(options.FIG_W, options.FIG_H))

        ax.plot(
            intra_data,
            intra_cdf,
            "--",
            linewidth=3.0,
            color=cbqual.Set1_5.mpl_colors[0],
            label="Intra-ASN",
        )
        ax.plot(
            inter_data,
            inter_cdf,
            "--",
            linewidth=2.8,
            color=cbqual.Set1_5.mpl_colors[1],
            label="Inter-ASN",
        )
        ax.plot(
            both_data,
            both_cdf,
            "--",
            linewidth=2.6,
            color=cbqual.Set1_5.mpl_colors[2],
            label=f"Both",
        )

        ax.grid(
            which="major", axis="y", linestyle="dashdot", linewidth=0.4, color="#AEAEAE"
        )
        ax.grid(
            which="minor", axis="y", linestyle="dotted", linewidth=0.2, color="#AEAEAE"
        )
        ax.grid(
            which="major", axis="x", linestyle="dashdot", linewidth=0.4, color="#AEAEAE"
        )
        ax.grid(
            which="minor", axis="x", linestyle="dotted", linewidth=0.2, color="#AEAEAE"
        )

        ax.set_xticks(range(0, TICKS * 6, TICKS))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKS / 5))

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        ax.set(
            xlabel=XLABEL,
            xlim=(-20, 200),
            ylabel="CDF",
        )  # ylim=(-0.1, 1))

        plt.tight_layout()
        ax.legend(loc="lower right")

        if show_plot:
            plt.show()

        plt.savefig(out_file, bbox_inches="tight")


if __name__ == "__main__":
    # Define input/output file paths
    input_file = "../../data/csv/timeline_statistics.csv"  # CSV input under data/csv/
    # Write analysis and plots under data/text/ and data/plots/
    stats_output_file = (
        "../../data/text/median-inflation-as-cdf.txt"  # Basic analysis output
    )
    plot_output_file = (
        "../../data/plots/median-inflation-as-cdf.pdf"  # Output PDF file for the plot
    )

    # Configuration options
    retain_nans = False  # Change to True if you want to keep NaNs
    show_plot = False  # Change to True to display the plot

    with utils.open(stats_output_file, "w") as out:
        (
            intra_data,
            intra_cdf,
            inter_data,
            inter_cdf,
            both_data,
            both_cdf,
        ) = load_csv_ccdf(input_file, "Median Inflation V2", not retain_nans, out)

    gen_plot(
        intra_data,
        intra_cdf,
        inter_data,
        inter_cdf,
        both_data,
        both_cdf,
        plot_output_file,
        show_plot,
    )
