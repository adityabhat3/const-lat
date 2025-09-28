import os
import json
from collections import defaultdict
import csv
import numpy as np

AVG_SPREAD = 2


def compute_statistics(timeline_data, thresh):
    change_points = []
    numbers = np.array(timeline_data)  # Ensure input is a NumPy array
    floored = np.ceil(numbers / thresh) * thresh  # Floor to nearest 100
    change_points = np.where(np.diff(floored) != 0)[0] + 1  # Find change points
    # differences = np.diff(change_indexes)
    change_points = np.concatenate([[0], change_points, [len(timeline_data)]])
    change_points.sort()
    print(change_points)
    differences = [
        change_points[i] - change_points[i - 1] for i in range(1, len(change_points))
    ]
    max_cfr = np.nanmax(differences) * AVG_SPREAD  # 2 hours on average between points
    return max_cfr


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
                if min_value > 0:
                    timeline_dict[(anchor_id, dst_name)].append(min_value)


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"
    csv_filename = "../../data/csv/max-cfr-operational-statistics.csv"

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
                "operational_max_cfr100",
                "operational_max_cfr50",
                "operational_max_cfr25",
                "operational_max_cfr10",
            ]
        )
        for key, value in timeline_dict.items():
            count += 1
            print(count)
            anchor_id, dst_name = key
            writer.writerow(
                [
                    anchor_id,
                    dst_name,
                    compute_statistics(timeline_dict[key], 100),
                    compute_statistics(timeline_dict[key], 50),
                    compute_statistics(timeline_dict[key], 25),
                    compute_statistics(timeline_dict[key], 10),
                ]
            )
