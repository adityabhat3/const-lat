#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#
"""Plot the CDF of IQR of latencies. Each data point is the IQR of latencies
observed in a specific timeline.
"""
XLABEL = "Inter-quartile range of latency (ms)"
COLUMN = "IQR"
DESCRIPTION = "Plot the CDF of inter-quartile range of latencies"
TICKS = 100

import options
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

    df["Destination ASN"] = df["Destination ASN"].astype(str)
    df["Source ASN"] = df["Source ASN"].astype(str)
    df["IQR"] = df["IQR"].astype(str)
    df = df[df["IQR"] != "nan"]
    df["IQR"] = df["IQR"].astype(float)

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

    def compute_cdf(data):
        data_sorted = np.sort(data)
        N = len(data_sorted)
        cum_prob = np.arange(1, N + 1) / N
        return data_sorted, cum_prob

    intra_data, intra_cdf = compute_cdf(intra_as[column_label])
    inter_data, inter_cdf = compute_cdf(inter_as[column_label])

    both_data, both_cdf = compute_cdf(both[column_label])
    print(both_data[-1], intra_data[-1], inter_data[-1])
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

        ax.set_xticks(range(0, TICKS * 5, TICKS))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKS / 5))

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        ax.set(
            xlabel=XLABEL,
            xlim=None,  # (-20, 400),
            ylabel="CDF",
        )  # ylim=(-0.1, 1))

        plt.tight_layout()

        ax.legend(loc="lower right")

        if show_plot:
            plt.show()

        plt.savefig(out_file, bbox_inches="tight")


if __name__ == "__main__":
    # Define input/output file paths
    input_file = (
        "../../data/csv/timeline_statistics.csv"  # Replace with actual CSV file path
    )
    stats_output_file = (
        "../../data/text/iqr-update-ipinfo-cdf.txt"  # File to store basic analysis
    )
    plot_output_file = (
        "../../data/plots/iqr-update-ipinfo-cdf.pdf"  # Output PDF file for the plot
    )

    # Configuration options
    retain_nans = False  # Change to True if you want to keep NaNs
    show_plot = False  # Change to True to display the plot

    gen_plot(
        *load_csv_ccdf(input_file, COLUMN, not retain_nans),
        plot_output_file,
        show_plot,
    )
