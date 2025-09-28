import os
import json
import random
import matplotlib.pyplot as plt
from collections import defaultdict


def kalman_filter(data, process_var=1e-2, measurement_var=0.1**2):
    """
    Apply a simple 1D Kalman filter to the data.

    Args:
        data (list): A list of observed values.
        process_var (float): Process variance (Q).
        measurement_var (float): Measurement variance (R).

    Returns:
        list: Filtered (predicted) values.
    """
    if not data:
        return []

    x = data[0]  # Initial state estimate
    P = 1.0  # Initial error covariance
    Q = process_var  # Process variance
    R = measurement_var  # Measurement variance
    predictions = [x]

    for i in range(1, len(data)):
        # Prediction step
        x_pred = x
        P = P + Q

        # Update step
        K = P / (P + R)
        x = x_pred + K * (data[i] - x_pred)
        P = (1 - K) * P

        predictions.append(x)

    return predictions


def process_json_file(file_path, timeline_dict, anchor_probe_info):
    with open(file_path, "r") as file:
        data = json.load(file)

    for measurement in data:
        prb_id = measurement.get("prb_id")
        min_value = measurement.get("min")
        dst_name = measurement.get("dst_name")

        for anchor_id, stored_prb_id in anchor_probe_info.items():
            if stored_prb_id == prb_id:
                if min_value is not None and min_value > 0:
                    timeline_dict[(anchor_id, dst_name)].append(min_value)


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"

    timeline_dict = defaultdict(list)

    with open(anchor_probe_info_file, "r") as f:
        anchor_probe_info = json.load(f)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            process_json_file(file_path, timeline_dict, anchor_probe_info)

    # Select a random timeline to visualize
    random_timeline = random.choice(list(timeline_dict.keys()))
    original_values = timeline_dict[random_timeline]
    kalman_filtered_values = kalman_filter(original_values)

    # Plot original vs. Kalman-filtered values
    plt.figure(figsize=(10, 5))
    plt.plot(original_values, label="Original Latency", marker="o", linestyle="dashed")
    plt.plot(
        kalman_filtered_values,
        label="Kalman-Filtered Latency",
        marker="s",
        linestyle="solid",
    )

    plt.xlabel("Time (Index)")
    plt.ylabel("Latency (ms)")
    plt.title(f"Latency Timeline for {random_timeline}")
    plt.legend()
    plt.grid()

    plt.show()
