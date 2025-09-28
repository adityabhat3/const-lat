import random
from hdphmm.py import (
    Beta,
    BlockedSamplerPrior,
    DPGMMObservationModelPrior,
    Gamma,
    Normal,
    NormalInverseChisq,
    TransitionDistributionPrior,
    robuststats,
    segment,
)
from julia import Main, PyCall
import re


def find_lists_in_string(s):
    list_pattern = r"\[.*?\]"
    matches = re.findall(list_pattern, s)
    lists = [match for match in matches]
    return lists


# 2 signals, level shift and basically constant, run on multiple iters
# compare with other algos
def test_basic(data):
    obs_med, obs_var = robuststats(Normal, data)
    tp = TransitionDistributionPrior(Gamma(2, 10), Gamma(100, 10), Beta(500, 1))
    op = DPGMMObservationModelPrior(
        NormalInverseChisq(obs_med, obs_var, 1, 10), Gamma(1, 0.5)
    )
    prior = BlockedSamplerPrior(1.0, tp, op)
    return segment(data, prior, L=10, LP=5, iter=10, verbose=False)


def find_change_points(lst):
    change_points = []

    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1]:
            change_points.append(i)

    return change_points


def cp_hmm_hdp(arr):
    julia_obj = test_basic(arr)
    state_at_each_point = eval(find_lists_in_string(str(julia_obj))[2])
    change_points = find_change_points(state_at_each_point)
    return change_points
