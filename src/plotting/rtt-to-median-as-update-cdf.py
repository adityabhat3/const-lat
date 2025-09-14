#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#

"""
Plot the CDF of ratio of RTT to median for intra-AS and inter-AS
"""

XLABEL = "Ratio of RTT to median "
COLUMN = "Normalized Median RTT"
DESCRIPTION = "Plot the CDF of ratio of RTT to median"
TICKS = 1

import options
import utils

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import palettable.colorbrewer.qualitative as cbqual
import sys
import pandas as pd
import io


def open(in_file, mode):
    return io.open(in_file, mode, encoding="utf-8")


def load_csv_ccdf(csv_file, column_label, remove_nan=True, out=sys.stdout):
    df = pd.read_csv(csv_file, keep_default_na=False, low_memory=False)

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
    df["Day"] = pd.to_datetime(df["Day"])
    df["Destination ASN"] = df["Destination ASN"].astype(str)
    df["Source ASN"] = df["Source ASN"].astype(str)

    intra_as = df[
        (df["Source ASN"] == df["Destination ASN"])
        & (df["Source ASN"] != "")
        & (df["Destination ASN"] != "")
        & (df["Source ASN"] != "Unknown")
        & (df["Destination ASN"] != "Unknown")
    ]
    inter_as = df[
        (df["Source ASN"] != df["Destination ASN"])
        & (df["Source ASN"] != "")
        & (df["Destination ASN"] != "")
        & (df["Source ASN"] != "Unknown")
        & (df["Destination ASN"] != "Unknown")
    ]

    both = df

    print(
        intra_as[column_label].median(),
        inter_as[column_label].median(),
        both[column_label].median(),
    )

    intra_as_more_than_2 = intra_as[intra_as[column_label] > 2]
    inter_as_more_than_2 = inter_as[inter_as[column_label] > 2]
    both_more_than_2 = both[both[column_label] > 2]
    print(
        intra_as_more_than_2[column_label].count() / intra_as[column_label].count(),
        inter_as_more_than_2[column_label].count() / inter_as[column_label].count(),
        both_more_than_2[column_label].count() / both[column_label].count(),
    )
    print(
        intra_as[column_label].count(),
        inter_as[column_label].count(),
        both[column_label].count(),
    )

    def compute_cdf(data):
        data_sorted = np.sort(data)
        N = len(data_sorted)
        cum_prob = np.arange(1, N + 1) / N
        return data_sorted, cum_prob

    intra_data, intra_cdf = compute_cdf(intra_as[column_label])
    inter_data, inter_cdf = compute_cdf(inter_as[column_label])

    both_data, both_cdf = compute_cdf(both[column_label])

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
            label="Both",
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

        ax.set_xscale("log")
        ax.set_xticks([10**n for n in range(-3, 4)])
        ax.xaxis.set_minor_locator(
            ticker.LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=10)
        )

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        ax.set(xlabel=XLABEL, xlim=(10 ** (-3), 100), ylabel="CDF")
        ax.legend()
        plt.tight_layout()

        if show_plot:
            plt.show()

        plt.savefig(out_file, bbox_inches="tight")


if __name__ == "__main__":
    # Define input/output file paths
    input_file = (
        "../../data/csv/pointwise_statistics.csv"  # Replace with actual CSV file path
    )
    stats_output_file = "../../data/text/rtt-to-median-update-as-cdf.txt"  # File to store basic analysis
    plot_output_file = "../../data/plots/rtt-to-median-update-as-cdf.pdf"  # Output PDF file for the plot

    # Configuration options
    retain_nans = False  # Change to True if you want to keep NaNs
    show_plot = False  # Change to True to display the plot

    #     # # Load data and compute CDFs
    with utils.open(stats_output_file, "w") as out:
        (
            intra_data,
            intra_cdf,
            inter_data,
            inter_cdf,
            both_data,
            both_cdf,
        ) = load_csv_ccdf(input_file, COLUMN, not retain_nans, out)

    # Generate and save the plot
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
