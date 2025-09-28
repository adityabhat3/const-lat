import os
import json
from collections import defaultdict
import csv
import numpy as np

ALPHA = 0.01
WINDOW_SIZE = 32


def simple_moving_average(data, window_size):
    sma = []
    for i in range(len(data)):
        if i < window_size:
            sma.append(np.nan)  # Not enough data for prediction
        else:
            sma.append(np.mean(data[i - window_size : i]))
    return sma


def exponentially_weighted_moving_average(data, alpha):
    """
    Compute the Exponentially Weighted Moving Average (EWMA) for a timeline.

    Args:
        data (list or array-like): Input timeline.
        alpha (float): Smoothing factor.

    Returns:
        list: Predicted values using EWMA.
    """
    ewma = [data[0]]  # y0 = x0
    for i in range(1, len(data)):
        predicted = (1 - alpha) * ewma[-1] + alpha * data[i]
        ewma.append(predicted)
    return ewma


def compute_prediction_error(actual, predicted):
    """
    Compute prediction error for each data point.

    Args:
        actual (list or array-like): Actual values from the timeline.
        predicted (list or array-like): Predicted values for the timeline.

    Returns:
        list: Prediction error for each data point.
    """
    return [
        np.abs(np.log(pred / act)) if act > 0 else np.nan
        for act, pred in zip(actual, predicted)
    ]


def compute_statistics(timeline_data):
    actual = timeline_data
    # predicted = simple_moving_average(actual, WINDOW_SIZE)
    predicted = exponentially_weighted_moving_average(actual, ALPHA)
    err = compute_prediction_error(actual, predicted)
    return err


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
                if min_value > 0 and min_value is not None:
                    timeline_dict[(anchor_id, dst_name)].append(min_value)


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"
    csv_filename = f"../../data/csv/predictive-ewma-{ALPHA}-statistics.csv"
    # csv_filename = f"../../data/csv/predictive-sma-{WINDOW_SIZE}-statistics.csv"

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
                "error",
            ]
        )
        for (anchor_id, dst_name), value in timeline_dict.items():
            ranks_statistics_info = compute_statistics(
                timeline_dict[(anchor_id, dst_name)],
            )
            count += 1
            print(count)

            for idx, point in enumerate(ranks_statistics_info):
                writer.writerow(
                    [
                        anchor_id,
                        dst_name,
                        idx,
                        float(point),
                    ]
                )
