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

    as_as = df[(df["Source Continent"] == "AS") & (df["Destination Continent"] == "AS")]
    eu_eu = df[(df["Source Continent"] == "EU") & (df["Destination Continent"] == "EU")]
    na_na = df[(df["Source Continent"] == "NA") & (df["Destination Continent"] == "NA")]
    as_na = df[(df["Source Continent"] == "AS") & (df["Destination Continent"] == "NA")]
    eu_na = df[(df["Source Continent"] == "EU") & (df["Destination Continent"] == "NA")]

    def compute_cdf(data):
        data_sorted = np.sort(data)
        N = len(data_sorted)
        cum_prob = np.arange(1, N + 1) / N
        return data_sorted, cum_prob

    as_as_data, as_as_cdf = compute_cdf(as_as[column_label])
    eu_eu_data, eu_eu_cdf = compute_cdf(eu_eu[column_label])
    na_na_data, na_na_cdf = compute_cdf(na_na[column_label])
    as_na_data, as_na_cdf = compute_cdf(as_na[column_label])
    eu_na_data, eu_na_cdf = compute_cdf(eu_na[column_label])
    print(
        len(as_as_data),
        len(eu_eu_data),
        len(na_na_data),
        len(as_na_data),
        len(eu_na_data),
    )
    print("as_as, eu_eu, na_na, as_na, eu_na")
    print("absolute values")
    print(
        len(as_as_data[as_as_data > 10]),
        len(eu_eu_data[eu_eu_data > 10]),
        len(na_na_data[na_na_data > 10]),
        len(as_na_data[as_na_data > 10]),
        len(eu_na_data[eu_na_data > 10]),
    )
    print("percentages")
    print(
        len(as_as_data[as_as_data > 10]) / len(as_as_data),
        len(eu_eu_data[eu_eu_data > 10]) / len(eu_eu_data),
        len(na_na_data[na_na_data > 10]) / len(na_na_data),
        len(as_na_data[as_na_data > 10]) / len(as_na_data),
        len(eu_na_data[eu_na_data > 10]) / len(eu_na_data),
    )

    return (
        as_as_data,
        as_as_cdf,
        eu_eu_data,
        eu_eu_cdf,
        na_na_data,
        na_na_cdf,
        as_na_data,
        as_na_cdf,
        eu_na_data,
        eu_na_cdf,
    )


def gen_plot(
    as_as_data,
    as_as_cdf,
    eu_eu_data,
    eu_eu_cdf,
    na_na_data,
    na_na_cdf,
    as_na_data,
    as_na_cdf,
    eu_na_data,
    eu_na_cdf,
    out_file,
    show_plot=False,
):
    with mpl.rc_context(options.get_basic_conf()):
        fig, ax = plt.subplots(figsize=(options.FIG_W, options.FIG_H))

        ax.plot(
            as_as_data,
            as_as_cdf,
            "--",
            linewidth=2.8,
            color=cbqual.Set1_5.mpl_colors[0],
            label="AS-AS",
        )
        ax.plot(
            eu_eu_data,
            eu_eu_cdf,
            "--",
            linewidth=2.9,
            color=cbqual.Set1_5.mpl_colors[1],
            label="EU-EU",
        )
        ax.plot(
            na_na_data,
            na_na_cdf,
            "--",
            linewidth=2.7,
            color=cbqual.Set1_5.mpl_colors[2],
            label="NA-NA",
        )
        ax.plot(
            as_na_data,
            as_na_cdf,
            "--",
            linewidth=2.6,
            color=cbqual.Set1_5.mpl_colors[3],
            label="AS-NA",
        )
        ax.plot(
            eu_na_data,
            eu_na_cdf,
            "--",
            linewidth=2.5,
            color=cbqual.Set1_5.mpl_colors[4],
            label="EU-NA",
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

        ax.set_xticks(range(0, 11, 2))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        ax.set(xlabel=XLABEL, xlim=(0, 11), ylabel="CDF")
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
    stats_output_file = "../../data/text/rtt-to-median-continent-update-cdf.txt"  # File to store basic analysis
    plot_output_file = "../../data/plots/rtt-to-median-continent-final-ipinfo-cdf.pdf"  # Output PDF file for the plot

    # Configuration options
    retain_nans = False  # Change to True if you want to keep NaNs
    show_plot = False  # Change to True to display the plot

    #     # # Load data and compute CDFs
    with utils.open(stats_output_file, "w") as out:
        (
            as_as_data,
            as_as_cdf,
            eu_eu_data,
            eu_eu_cdf,
            na_na_data,
            na_na_cdf,
            as_na_data,
            as_na_cdf,
            eu_na_data,
            eu_na_cdf,
        ) = load_csv_ccdf(input_file, COLUMN, not retain_nans, out)

    # Generate and save the plot
    gen_plot(
        as_as_data,
        as_as_cdf,
        eu_eu_data,
        eu_eu_cdf,
        na_na_data,
        na_na_cdf,
        as_na_data,
        as_na_cdf,
        eu_na_data,
        eu_na_cdf,
        plot_output_file,
        show_plot,
    )
