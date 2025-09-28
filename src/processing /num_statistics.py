import os
import json
from collections import defaultdict
import csv
import numpy as np
from ranks_change_point_algo import cp_ranks
from bootstrap_change_point_algo import cp_bootstrap
from hmm_change_point_algo import cp_hmm_hdp


def calculate_differences(nums):
    if len(nums) < 2:
        raise ValueError(
            "List must contain at least two elements to calculate differences"
        )

    differences = [nums[i] - nums[i - 1] for i in range(1, nums.__len__())]

    return differences


def compute_statistics(timeline_data, cp_func):
    try:
        cps = cp_func(timeline_data)
    except Exception as e:
        print(e)
    if len(cps) == 0:
        return 0, np.nan, np.nan

    length = len(cps)
    cps.append(0)
    cps.append(len(timeline_data))
    cps.sort()
    cps = calculate_differences(cps)
    average = np.nanmean(cps)
    std_dev = np.nanstd(cps)

    return length, average, std_dev


def process_json_file(
    file_path,
    timeline_dict,
    anchor_probe_info,
):
    with open(file_path, "r") as file:
        data = json.load(file)

    for measurement in data:
        prb_id = measurement.get("prb_id")
        min_value = measurement.get("min")
        dst_name = measurement.get("dst_name")

        for anchor_id, stored_prb_id in anchor_probe_info.items():
            if stored_prb_id == prb_id:
                timeline_dict[(anchor_id, dst_name)].append(min_value)


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"
    csv_filename = "../../data/csv/num_statistics.csv"
    timeline_dict = defaultdict(list)

    with open(anchor_probe_info_file, "r") as anchor_probe_info_file:
        anchor_probe_info = json.load(anchor_probe_info_file)

    count = 0
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            process_json_file(
                file_path,
                timeline_dict,
                anchor_probe_info,
            )

    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Source (Anchor ID)",
                "Destination (Domain Name)",
                "bootstrap_num",
                "bootstrap_mean",
                "bootstrap_stdev",
                "ranks_num",
                "ranks_mean",
                "ranks_stdev",
                "hmm_num",
                "hmm_mean",
                "hmm_stdev",
            ]
        )
        for (anchor_id, dst_name), value in timeline_dict.items():
            timeline_data = timeline_dict[(anchor_id, dst_name)]

            bootstrap_stats = compute_statistics(timeline_data, cp_bootstrap)
            ranks_stats = compute_statistics(timeline_data, cp_ranks)
            hmm_stats = compute_statistics(timeline_data, cp_hmm_hdp)

            count += 1
            print(count)

            writer.writerow(
                [anchor_id, dst_name]
                + list(bootstrap_stats)
                + list(ranks_stats)
                + list(hmm_stats)
            )
