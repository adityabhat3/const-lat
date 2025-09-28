import os
import json
from collections import defaultdict
import csv
import numpy as np

# from ranks_change_point_algo import cp_ranks
# from bootstrap_change_point_algo import cp_bootstrap
from hmm_change_point_algo import cp_hmm_hdp
import requests
from functools import cache, lru_cache

"""
This file can be used to generate csv files required for 
all Max CFR related plots. Replace hmm_hdp with ranks or bootstrap
to use those algoritms instead
"""

cdn_domains_file = "../../data/targets/all_cdn_domains_new.json"

# Load the CSV file into memory for quick lookups
csv_file_path = "../../data/geolocation/ipinfo-enrichment-results.csv"  # Change this to the actual file path

AVG_SPREAD = 2  # Hours


@lru_cache(maxsize=None)
def get_probe_asn(probe_id):
    """
    Fetch the ASN (Autonomous System Number) for a given probe ID from RIPE Atlas API.
    """
    url = f"https://atlas.ripe.net/api/v2/probes/{probe_id}/"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        probe_info = response.json()
        return probe_info.get("asn_v4", None)  # Return ASN for IPv4
    else:
        response.raise_for_status()


def load_cdn_providers():
    with open(cdn_domains_file, "r") as file:
        return json.load(file)


cdn_providers = load_cdn_providers()


@cache
def get_cdn_provider(dst_name):
    for provider, domains in cdn_providers.items():
        if dst_name in domains:
            return provider
    return ""


def load_csv_data(csv_file):
    """Load CSV data into a dictionary for fast lookups."""
    data_dict = {}
    with open(csv_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ip = row["ip"].strip()
            data_dict[ip] = row
    return data_dict


# Load the CSV data once
ipinfo_data = load_csv_data(csv_file_path)


def get_dest_asn_ipinfo(dst_ip):
    """Get ASN for a given destination IP."""
    row = ipinfo_data.get(dst_ip)
    if row:
        if row["org"].split():
            return row["org"].split()[0][2:]  # Extract ASN (e.g., 'AS9121' → '9121')
    return None


def compute_statistics(timeline_data, cp_func):
    cps = []
    try:
        cps = cp_func(timeline_data)
    except Exception as e:
        print(e)
    cps.append(0)
    cps.append(len(timeline_data))
    cps.sort()
    cps_diff = [cps[i] - cps[i - 1] for i in range(1, len(cps))]
    max_cfr = np.nanmax(cps_diff) * AVG_SPREAD  # 2hrs on avg between 2 points
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
        src_addr = measurement.get("src_addr")
        dst_addr = measurement.get("dst_addr")

        src_asn = get_probe_asn(prb_id) if prb_id else ""
        dst_asn = get_dest_asn_ipinfo(dst_addr) if dst_addr else ""

        for anchor_id, stored_prb_id in anchor_probe_info.items():
            if stored_prb_id == prb_id:
                if min_value > 0:
                    timeline_dict[(anchor_id, dst_name)].append(min_value)
                    asn_continent_dict[(anchor_id, dst_name)] = (
                        src_asn,
                        dst_asn,
                    )


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"
    csv_filename = "../../data/csv/hmm-as-max-cfr-ipinfo-statistics.csv"

    timeline_dict = defaultdict(list)
    asn_continent_dict = defaultdict(tuple)

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
                "Source ASN",
                "Destination ASN",
                "hmm_max_cfr",
            ]
        )
        for key, value in timeline_dict.items():
            hmm_statistics_info = compute_statistics(timeline_dict[key], cp_hmm_hdp)
            count += 1
            print(count)
            anchor_id, dst_name = key

            writer.writerow(
                [
                    anchor_id,
                    dst_name,
                    asn_continent_dict[key][0],
                    asn_continent_dict[key][1],
                    hmm_statistics_info,
                ]
            )
