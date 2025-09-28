import os
import json
import csv
from collections import defaultdict
import numpy as np
from datetime import datetime
import requests
from functools import lru_cache
import pycountry_convert as pc
from geoip2.database import Reader

TOTAL_MEASUREMENTS = 120

# Path to your MaxMind GeoLite2 database files
asn_db_file = "../../data/geolocation/GeoLite2-ASN.mmdb"
city_db_file = "../../data/geolocation/GeoLite2-City.mmdb"
# Load the CSV file into memory for quick lookups
csv_file_path = "../../data/geolocation/ipinfo-enrichment-results.csv"  # Change this to the actual file path

# Initialize the readers once to avoid reopening the files on every lookup.
asn_reader = Reader(asn_db_file)
city_reader = Reader(city_db_file)


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


@lru_cache(maxsize=None)
def get_probe_continent(probe_id):
    """
    Fetch the continent for a given probe ID based on country code.
    """
    url = f"https://atlas.ripe.net/api/v2/probes/{probe_id}/"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        probe_info = response.json()
        country_code = probe_info.get("country_code", None)

        if country_code:
            try:
                continent_code = pc.country_alpha2_to_continent_code(country_code)
                return continent_code
            except KeyError:
                return "Unknown"
        else:
            return "Unknown"
    else:
        response.raise_for_status()


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


def get_dest_continent_ipinfo(dst_ip):
    """Get the continent name for a given destination IP."""
    row = ipinfo_data.get(dst_ip)
    if row:
        country_code = row["country"]
        try:
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            return continent_code
        except KeyError:
            return None
    return None


def get_dest_geoloc_ipinfo(dst_ip):
    """Get latitude and longitude for a given destination IP."""
    row = ipinfo_data.get(dst_ip)
    if row:
        return tuple(
            map(float, row["loc"].split(","))
        )  # Convert "41.0048,29.0448" to (41.0048, 29.0448)
    return (np.nan, np.nan)


def process_json_file(file_path, timeline_dict, anchor_probe_info):
    with open(file_path, "r") as file:
        data = json.load(file)

    for measurement in data:
        prb_id = measurement.get("prb_id")
        results = measurement.get("result")
        if results is not None:
            # Extract valid RTTs (ignore strings and non-positive values)
            results_list = [
                x["rtt"]
                for x in results
                if "rtt" in x and isinstance(x["rtt"], (int, float)) and x["rtt"] > 0
            ]
            if not results_list:
                continue
            measurement_median = np.nanmedian(results_list)
            dst_name = measurement.get("dst_name")
            timestamp = measurement.get("timestamp")
            src_addr = measurement.get("src_addr")
            dst_addr = measurement.get("dst_addr")
            prb_id = measurement.get("prb_id")
            src_asn = get_probe_asn(prb_id) if prb_id else ""
            dst_asn = get_dest_asn_ipinfo(dst_addr) if dst_addr else ""
            src_continent = get_probe_continent(prb_id) if prb_id else ""
            dst_continent = get_dest_continent_ipinfo(dst_addr) if dst_addr else ""
            # Convert timestamp to a day string (e.g., "2023-08-15")
            day = (
                datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                if timestamp
                else ""
            )

            # Find the corresponding anchor_id from anchor_probe_info using prb_id.
            anchor_id = None
            for a_id, stored_prb_id in anchor_probe_info.items():
                if stored_prb_id == prb_id:
                    anchor_id = a_id
                    break
            if anchor_id is None:
                anchor_id = "Unknown"

            timeline_key = (anchor_id, dst_name)
            timeline_dict[timeline_key].append(
                {
                    "timestamp": timestamp,
                    "day": day,
                    "results": results_list,
                    "measurement_median": measurement_median,
                    "src_addr": src_addr,
                    "dst_addr": dst_addr,
                    "src_asn": src_asn,
                    "dst_asn": dst_asn,
                    "src_continent": src_continent,
                    "dst_continent": dst_continent,
                }
            )


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"
    csv_filename = "../../data/csv/pointwise_statistics.csv"

    timeline_dict = defaultdict(list)

    with open(anchor_probe_info_file, "r") as f:
        anchor_probe_info = json.load(f)

    # Process each JSON file in the input folder.
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            process_json_file(
                os.path.join(input_folder, filename), timeline_dict, anchor_probe_info
            )

    # Write CSV with extra columns for further analysis.
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Anchor ID",
                "Destination",
                "Measurement Index",
                "Timestamp",
                "Day",
                "Source IP",
                "Destination IP",
                "Source ASN",
                "Destination ASN",
                "Source Continent",
                "Destination Continent",
                "Median RTT",
                "Timeline Global Median RTT",
                "Normalized Median RTT",
                "Spike (Normalized >= 10)",
            ]
        )
        # Process each timeline separately.
        for (anchor_id, dst_name), measurements in timeline_dict.items():
            # Aggregate all RTT values in the timeline to compute the global median.
            timeline_rtts = []
            for m in measurements:
                timeline_rtts.extend(m["results"])
            if not timeline_rtts:
                continue
            timeline_global_median = np.nanmedian(timeline_rtts)
            for idx, m in enumerate(measurements):
                normalized = (
                    m["measurement_median"] / timeline_global_median
                    if timeline_global_median > 0
                    else 0
                )
                spike = normalized >= 10
                writer.writerow(
                    [
                        anchor_id,
                        dst_name,
                        idx,
                        m["timestamp"],
                        m["day"],
                        m["src_addr"],
                        m["dst_addr"],
                        m["src_asn"],
                        m["dst_asn"],
                        m["src_continent"],
                        m["dst_continent"],
                        m["measurement_median"],
                        timeline_global_median,
                        normalized,
                        spike,
                    ]
                )
