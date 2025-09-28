#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#

"""
Plot multiple CDFs on the same graph for specified columns in a CSV file using a configuration dictionary.
Each column has its own stats file.
"""

XLABEL = "CFR durations (hours)"
DESCRIPTION = "Plot the CDF of multiple columns."
import options
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import palettable.colorbrewer.qualitative as cbqual
import utils


def gen_plot(cdfs, labels, out_file, show_plot=False):
    """
    Generate a single plot with multiple CDFs overlayed.

    Args:
        cdfs (list of tuples): Each tuple contains (data, cdf) for a column.
        labels (list of str): Labels for each column (to display in legend).
        out_file (str): Path to the output PDF file.
        show_plot (bool): If True, display the plot interactively.
    """
    with mpl.rc_context(options.get_basic_conf()):
        # Default size of plots.
        fig = plt.figure()
        ax = fig.subplots()
        # fig.set_size_inches(8, 6)

        # Plot each CDF
        fig.set_size_inches(options.FIG_W, options.FIG_H)
        for i, (data, cdf) in enumerate(cdfs):
            color = cbqual.Set1_9.mpl_colors[i % len(cbqual.Set1_9.mpl_colors)]
            ax.plot(
                data, cdf, "-", linewidth=2.0 - 0.4 * i, label=labels[i], color=color
            )

        # Add gridlines
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

        # Configure ticks
        ax.set_xticks(range(0, 36, 5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))

        # Set axis labels and limits
        ax.set(xlabel=XLABEL, xlim=(-1, 251), ylabel="CDF")

        # Add legend
        ax.legend(loc="upper left", fontsize=10)

        # Adjust layout and save or show the plot
        plt.tight_layout()
        if show_plot:
            plt.show()
        plt.savefig(out_file, bbox_inches="tight")


def main(config):
    """
    Main function to process input, compute CDFs, and generate a plot.

    Args:
        config (dict): Configuration dictionary with the following keys:
            - in_file (str): Path to input CSV file.
            - column_stats_map (dict): Mapping of columns to their stats file paths.
            - plot_file (str): Path to output plot (PDF).
            - retain_nans (bool): Whether to retain NaNs in the data.
            - show_plot (bool): Whether to show the plot interactively.
    """
    cdfs = []
    # labels = list(config['column_stats_map'].keys())
    labels = config["labels"]

    outs = config["outs"]
    # Load data and compute CDF for each column
    for i, (column, stats_file) in enumerate(config["column_stats_map"].items()):
        with utils.open(stats_file, "r") as stats_file_ptr:
            with utils.open(outs[i], "w") as out:
                data, cdf = utils.load_csv(
                    stats_file_ptr, column, not config["retain_nans"], out
                )
                cdfs.append((data, cdf))

    # Generate the plot with multiple CDFs
    gen_plot(cdfs, labels, config["plot_file"], config["show_plot"])


if __name__ == "__main__":
    # Configuration dictionary
    config = {
        "labels": ["RankOrder", "Bootstrap", "HMM-HDP"],
        "column_stats_map": {  # Mapping of columns to stats file paths
            "ranks_cfr": "../../data/csv/ranks-cfr-statistics.csv",
            "bootstrap_cfr": "../../data/csv/bootstrap-cfr-statistics.csv",
            "hmm_cfr": "../../data/csv/hmm-cfr-statistics.csv",
        },
        "outs": [
            "../../data/text/ranks-cfr-stats.txt",
            "../../data/text/bootstrap-cfr-stats.txt",
            "../../data/text/hmm-cfr-stats.txt",
        ],
        "plot_file": "../../data/plots/cfr-cdf.pdf",  # Output PDF file
        "retain_nans": False,  # Whether to retain NaN values
        "show_plot": False,  # Whether to show the plot interactively
    }

    # Call the main function with the configuration
    main(config)
