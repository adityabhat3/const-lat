import sys
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import math
import sys
import pandas as pd
import numpy as np
import math
from scipy.stats import norm
import json

THRESH = 90


def get_ranks(arr):
    """
    Replaces each value in a list with its rank (1 for smallest, n for biggest).
    """
    s = np.sort(arr)
    for i in range(len(s)):
        arr[np.where(arr == s[i])[0]] = i + 1
    return arr


def find_cp(origarr):
    """
    Find change point location using min index of MSE.
    """
    avg = np.average(origarr)
    li = []
    for i in range(len(origarr) - 1):
        h1 = origarr[:i]
        h1 = np.add(h1, avg)
        h1 = np.square(h1)
        h2 = origarr[(i + 1) :]
        h2 = np.add(h2, avg)
        h2 = np.square(h2)
        s = np.sum(h1) + np.sum(h2)
        li.append(s)
    return np.argmin(li)


def cp_ranks_once(origarr, rounds=1000, thresh=THRESH):
    """
    Compute whether change has occurred in origarr using ranks method.
    """
    # Filter for empty arrays:
    if len(origarr) > 1:
        cp = find_cp(origarr.copy())
    else:
        return -1
    # faulty/no data:
    if origarr[cp] == -1:
        return -1
    # To prevent division by zero:
    # (removed in backwards_elimination if insignificant enough)
    # changepoint at right end of interval
    if cp == len(origarr) - 2:
        return cp_ranks_once(origarr[:-1])
    # changepoint at left end of interval
    if cp == 0:
        return cp_ranks_once(origarr[1:])
    s1 = origarr[:(cp)]
    x_minus = get_ranks(s1.copy())
    s2 = origarr[(cp + 1) :]
    x_plus = get_ranks(s2.copy())
    s12 = np.concatenate((s1, s2))
    x_union = get_ranks(s12.copy())

    r_minus = np.subtract(x_union[:(cp)], x_minus)
    r_plus = np.subtract(x_union[(cp):], x_plus)
    rp_mean = np.mean(r_plus)
    rm_mean = np.mean(r_minus)
    v_plus = np.sum((r_plus.copy() - rp_mean) ** 2)
    v_minus = np.sum((r_minus.copy() - rm_mean) ** 2)
    z = len(r_plus) * rp_mean - len(r_minus) * rm_mean
    z /= 2 * math.sqrt(rp_mean * rm_mean + v_plus + v_minus)
    cdf = norm.cdf(abs(z))
    l = (100 - thresh) / 100
    # Rejecting the null hypothesis:
    if cdf >= 1 - (l / 2):
        return cp
    return -1


def _cp_ranks(origarr, rounds=1000, thresh=THRESH, idx_offset=0):
    """
    Perform a "full" changepoint detection on a numpy array of values.
    Returns a list of indices of change points.
    """
    cp = cp_ranks_once(origarr, rounds, thresh)
    if cp > -1:
        # print("Change point found", cp+idx_offset)
        s1 = origarr[: (cp + 1)]
        a1 = _cp_ranks(s1, rounds, thresh, idx_offset)
        s2 = origarr[(cp + 1) :]
        a2 = _cp_ranks(s2, rounds, thresh, idx_offset + cp + 1)
        return sorted([cp + idx_offset] + a1 + a2)
    return []


def backwards_elimination(origarr, changepoints):
    """
    Performs backwards elimination to filter out irrelevant changepoints.
    """
    changepoints = [0] + changepoints + [len(origarr)]
    cps = []
    for i in range(1, len(changepoints) - 1):
        idx1 = changepoints[i - 1] + 1
        cp = changepoints[i]
        idx2 = changepoints[i + 1]
        # print("back", idx1, cp, idx2)
        iscp = _cp_ranks(origarr[idx1:idx2], idx_offset=idx1)
        if len(iscp):
            cps.append(cp)
        # else:
        #    print(cp, "eliminated")
    # print(len(changepoints), len(cps))
    return cps


def cp_ranks(arr):
    arr = np.array(arr)
    cps = _cp_ranks(arr)
    cps = backwards_elimination(arr, cps)
    return cps


def plot_changepoints(data, changepoints, title):
    """
    Plot the original data along with the detected changepoints.

    Parameters:
    - data: numpy array, input time series data
    - changepoints: list of changepoint indices
    """
    plt.figure(figsize=(10, 6))
    plt.plot(data, "bo-", label="Original Data", linewidth=1)  # Blue line, thinner
    for changepoint in changepoints:
        plt.axvline(
            changepoint, linestyle="--", color="red", linewidth=2, label="Changepoint"
        )

    plt.xlabel("Time")
    plt.ylabel("Average RTT")
    plt.title(title)

    plt.ylim(bottom=0)
    plt.grid(True, linestyle=":", linewidth=0.5, color="gray")  # Finer gridlines
    plt.minorticks_on()  # Enable minor ticks
    plt.grid(
        True, which="both", linestyle=":", linewidth=0.2, color="gray"
    )  # Add minor gridlines

    plt.legend()
    plt.show()
