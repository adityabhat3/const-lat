#!/usr/bin/env python3
# -*- coding: utf-8; fill-column: 80; -*-
#
"""Utility function to load plotting data from files.
"""

import numpy as np
import io
import pandas as pd
import sys


def open(in_file, mode):
    return io.open(in_file, mode, encoding="utf-8")


def load_csv(csv_file, column_label, remove_nan=True, out=sys.stdout):
    """
    Reads a CSV file, selects a column, removes `NaN' values if specified, sorts
    the data, calculates cumulative probabilities, and emits basic statistics to
    the specified output stream (`STDOUT' by default).
    """
    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Select the column by label
    col = df[column_label]

    # Remove NaN values, if specified
    if remove_nan:
        col = col.dropna()

    col_sorted = np.sort(col)

    # Calculate cumulative probabilities
    N = len(col_sorted)
    cum_prob = np.arange(1, N + 1) / N

    mean = np.mean(col_sorted)
    quantiles = np.quantile(col_sorted, (0.10, 0.25, 0.50, 0.75, 0.9, 0.95, 0.99))
    sdev = np.std(col_sorted)

    count_zeros = (col_sorted == 0).sum()
    percent_zeros = (count_zeros / N * 100) if N > 0 else 0

    print(percent_zeros)
    # count_gt_10 = (col_sorted > 10).sum()
    # fraction_gt_10 = count_gt_10 / N if N > 0 else 0
    # print(fraction_gt_10)
    out.write("#<mean> <p10> <p25> <p50> <p75> <p90> <p95> <p99> <sdev>\n")
    out.write(f"{mean:.2f} ")
    out.write(" ".join((f"{v:.2f}" for v in quantiles)))
    out.write(f" {sdev:.2f}")
    out.write("\n")

    return col_sorted, cum_prob
