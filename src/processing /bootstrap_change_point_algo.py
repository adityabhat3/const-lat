import sys
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt

import sys
import pandas as pd
import numpy as np
import json


THRESH = 90


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


def cp_bootstrap_once(origarr, rounds=1000, thresh=THRESH):
    """
    Compute whether change has occurred in origarr using bootstrap method.
    """
    if len(origarr) <= 1:
        return -1
    avg = np.average(origarr)

    def mkavgdiff(avg):
        def avgdiff(x):
            return x - avg

        return avgdiff

    avgdiff = np.frompyfunc(mkavgdiff(avg), 1, 1)

    def sdiff(arr):
        return max(arr) - min(arr)

    cusum = np.cumsum(avgdiff(origarr))
    sd = sdiff(cusum)
    # print("S_diff orig", sd)
    x = 0
    for _ in range(rounds):
        bootstrap = origarr.copy()
        np.random.shuffle(bootstrap)
        bootstrap_sd = sdiff(np.cumsum(avgdiff(bootstrap)))
        if bootstrap_sd < sd:
            x += 1
    conf = 100 * (x / rounds)
    # print(conf)
    if conf > thresh:
        cp = find_cp(origarr)
        return cp
    return -1


def _cp_bootstrap(origarr, rounds=1000, thresh=THRESH, idx_offset=0):
    """
    Perform a "full" changepoint detection on a numpy array of values.
    Returns a list of indices of change points.
    """
    cp = cp_bootstrap_once(origarr, rounds, thresh)
    if cp > -1:
        # print("Change point found", cp+idx_offset)
        s1 = origarr[: (cp + 1)]
        a1 = _cp_bootstrap(s1, rounds, thresh, idx_offset)
        s2 = origarr[(cp + 1) :]
        a2 = _cp_bootstrap(s2, rounds, thresh, idx_offset + cp + 1)
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
        iscp = _cp_bootstrap(origarr[idx1:idx2], idx_offset=idx1)
        if len(iscp):
            cps.append(cp)
        # else:
        #    print(cp, "eliminated")
    # print(len(changepoints), len(cps))
    return cps


def cp_bootstrap(arr):
    arr = np.array(arr)
    cps = _cp_bootstrap(arr)
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
