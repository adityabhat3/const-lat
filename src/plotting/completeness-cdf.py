#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#
"""
Plot the CDF of Completeness Factor of latencies. Each data point is the Completeness Factor of latencies observed in a specific timeline.
"""
XLABEL = "Completeness Factor"
COLUMN = "Completeness Factor"
DESCRIPTION = "Plot the CDF of completeness factor of latencies"
TICKS = 0.2

import options
import utils

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import palettable.colorbrewer.qualitative as cbqual
import sys


def gen_plot(data, cdf, out_file, show_plot=False):
    with mpl.rc_context(options.get_basic_conf()):
        # Default size of plots.
        fig = plt.figure()
        ax = fig.subplots()
        fig.set_size_inches(options.FIG_W, options.FIG_H)

        ax.plot(data, cdf, "-", linewidth=3.0, color=cbqual.Set1_3.mpl_colors[0])

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

        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(TICKS / 5))

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        ax.set(
            xlabel=XLABEL,
            xlim=None,  # (-20, 400),
            ylabel="CDF",
        )  # ylim=(-0.1, 1))

        plt.tight_layout()

        if show_plot:
            plt.show()

        plt.savefig(out_file, bbox_inches="tight")


def main(args):
    with utils.open(args.stats_file, "w") as out:
        data, cdf = utils.load_csv(args.in_file, COLUMN, not args.retain_nans, out)

    gen_plot(data, cdf, args.plot_file, args.show_plot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
    )

    # should be timeline_statistics.csv
    parser.add_argument("in_file", type=str, help="Path to input (CSV) file")

    parser.add_argument(
        "stats_file", type=str, help="Output file for storing some basic analyses"
    )

    parser.add_argument("plot_file", type=str, help="Path to output (PDF) plot")

    parser.add_argument(
        "-n",
        "--retain-nans",
        dest="retain_nans",
        action="store_true",
        default=False,  # By default, remove NaNs
        help="Retain NaN values in the data",
    )

    parser.add_argument(
        "-s",
        "--show-plot",
        dest="show_plot",
        action="store_true",
        default=False,
        help="Show plot (useful when developing script)",
    )

    main(parser.parse_args())
