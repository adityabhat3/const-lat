import os
import json
from collections import defaultdict
import csv
import numpy as np
from geoip2.database import Reader
from geopy.distance import geodesic
import requests
from functools import cache, lru_cache
import pycountry_convert as pc

TOTAL_MEASUREMENTS = 120
SPEED_OF_LIGHT_KM_PER_MS = 299.792458  # Speed of light in km/ms
# Path to your MaxMind GeoLite2 database files
asn_db_file = "../../data/geolocation/GeoLite2-ASN.mmdb"
city_db_file = "../../data/geolocation/GeoLite2-City.mmdb"
geoip_database_file = "../../data/geolocation/GeoLite2-City.mmdb"

# Load the CSV file into memory for quick lookups
csv_file_path = "../../data/geolocation/ipinfo-enrichment-results.csv"  # Change this to the actual file path

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


@cache
def get_probe_geolocation(probe_id):
    url = f"https://atlas.ripe.net/api/v2/probes/{probe_id}/"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        probe_info = response.json()
        coordinates = probe_info.get("geometry", {}).get("coordinates", None)
        if coordinates:
            return coordinates
        else:
            raise ValueError(f"Coordinates not found for probe ID {probe_id}")
    else:
        response.raise_for_status()


def haversine(lat1, lon1, lat2, lon2):
    if np.any(np.isnan([lat1, lon1, lat2, lon2])):
        return np.nan
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers


@cache
def get_ip_info(ip_address):
    if ip_address is None:
        return np.nan, np.nan
    with Reader(geoip_database_file) as reader:
        try:
            response = reader.city(ip_address)
            latitude = response.location.latitude
            longitude = response.location.longitude
            if latitude is None or longitude is None:
                return np.nan, np.nan
            return latitude, longitude
        except Exception as e:
            print("Error:", e)
            print(ip_address)
            return np.nan, np.nan


def compute_completeness_factor(timelines, key):
    # Count only positive values
    positive_values = [value for value in timelines[key] if value > 0]
    timelines[key] = positive_values
    return len(positive_values) / TOTAL_MEASUREMENTS


def compute_statistics(timeline):
    # Compute statistics for a single timeline
    if len(timeline) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    q1 = np.nanpercentile(timeline, 25)
    q3 = np.nanpercentile(timeline, 75)
    return (
        np.nanmin(timeline),
        q3 - q1,
        np.nanmedian(timeline),
        np.nanmean(timeline),
        np.nanstd(timeline),
        np.nanpercentile(timeline, 90),
        np.nanpercentile(timeline, 95),
    )


cdn_domains_file = "all_cdn_domains_new.json"


def load_cdn_providers():
    with open(cdn_domains_file, "r") as file:
        return json.load(file)


cdn_providers = load_cdn_providers()


@cache
def get_cdn_provider(dst_name):
    for provider, domains in cdn_providers.items():
        if dst_name in domains:
            return provider
    return "Unknown"


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


def process_json_file(
    file_path,
    timelines,
    theoretical_rtt,
    distances,
    anchor_probe_info,
    distances_v2,
    theoretical_rtt_v2,
    asn_continent_dict,
    cdn_providers_dict,
):
    with open(file_path, "r") as file:
        data = json.load(file)

    for measurement in data:
        prb_id = measurement.get("prb_id")
        dst_name = measurement.get("dst_name")
        src_addr = measurement.get("src_addr")
        dst_addr = measurement.get("dst_addr")

        src_asn = get_probe_asn(prb_id) if prb_id else ""
        dst_asn = get_dest_asn_ipinfo(dst_addr) if dst_addr else ""
        src_continent = get_probe_continent(prb_id) if prb_id else ""
        dst_continent = get_dest_continent_ipinfo(dst_addr) if dst_addr else ""

        # Check if prb_id is present and corresponds to anchor_id
        for anchor_id, stored_prb_id in anchor_probe_info.items():
            if stored_prb_id == prb_id:
                key = (anchor_id, dst_name)
                timelines[key].append(measurement.get("min"))
                asn_continent_dict[key] = (
                    src_asn,
                    dst_asn,
                    src_continent,
                    dst_continent,
                )
                if theoretical_rtt[key] == 0:
                    src_lat, src_lon = get_ip_info(src_addr)
                    dst_lat, dst_lon = get_dest_geoloc_ipinfo(dst_addr)

                    try:
                        src_lonv2, src_latv2 = get_probe_geolocation(prb_id)
                    except Exception as e:
                        print(f"Error: {e}")

                    cdn_providers_dict[key] = get_cdn_provider(dst_name)

                    distances[key] = haversine(src_lat, src_lon, dst_lat, dst_lon)
                    theoretical_rtt[key] = (
                        3 * distances[key]
                    ) / SPEED_OF_LIGHT_KM_PER_MS

                    distances_v2[key] = haversine(
                        src_latv2, src_lonv2, dst_lat, dst_lon
                    )
                    theoretical_rtt_v2[key] = (
                        3 * distances_v2[key]
                    ) / SPEED_OF_LIGHT_KM_PER_MS


if __name__ == "__main__":
    input_folder = "../../data/raw"
    anchor_probe_info_file = "../../data/anchor_probe_info/anchor_probe_info.json"
    csv_filename = "../../data/csv/timeline_statistics.csv"

    timelines = defaultdict(list)
    theoretical_rtt = defaultdict(float)
    distances = defaultdict(float)
    theoretical_rtt_v2 = defaultdict(float)
    distances_v2 = defaultdict(float)
    asn_continent_dict = defaultdict(tuple)
    cdn_providers_dict = defaultdict(str)

    with open(anchor_probe_info_file, "r") as anchor_probe_info_file:
        anchor_probe_info = json.load(anchor_probe_info_file)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            process_json_file(
                file_path,
                timelines,
                theoretical_rtt,
                distances,
                anchor_probe_info,
                distances_v2,
                theoretical_rtt_v2,
                asn_continent_dict,
                cdn_providers_dict,
            )

    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Source (Anchor ID)",
                "Destination (Domain Name)",
                "Source ASN",
                "Destination ASN",
                "Source Continent",
                "Destination Continent",
                "CDN Provider",
                "Completeness Factor",
                "Minimum",
                "IQR",
                "Median",
                "Average",
                "Standard Deviation",
                "90th Percentile",
                "95th Percentile",
                "Theoretical Min",
                "Min Inflation",
                "Median Inflation",
                "90th Percentile Inflation",
                "Distance(KM)",
                "Distance V2(KM)",
                "Theoretical Min V2",
                "Min Inflation V2",
                "Median Inflation V2",
                "90th Percentile Inflation V2",
            ]
        )
        for key, value in timelines.items():
            anchor_id, dst_name = key
            completeness_factor = compute_completeness_factor(timelines, key)
            statistics_info = compute_statistics(timelines[key])
            theoretical_min = theoretical_rtt[key]

            if theoretical_min == 0:
                min_inflation = np.nan
                median_inflation = np.nan
                ninetieth_percentile_inflation = np.nan
            else:
                min_inflation = statistics_info[0] / theoretical_min
                median_inflation = statistics_info[2] / theoretical_min
                ninetieth_percentile_inflation = statistics_info[5] / theoretical_min

            theoretical_min_v2 = theoretical_rtt_v2[key]
            if theoretical_min_v2 == 0:
                min_inflation_v2 = np.nan
                median_inflation_v2 = np.nan
                ninetieth_percentile_inflation_v2 = np.nan
            else:
                min_inflation_v2 = statistics_info[0] / theoretical_min_v2
                median_inflation_v2 = statistics_info[2] / theoretical_min_v2
                ninetieth_percentile_inflation_v2 = (
                    statistics_info[5] / theoretical_min_v2
                )

            src_asn, dst_asn, src_continent, dst_continent = asn_continent_dict[key]
            writer.writerow(
                [
                    anchor_id,
                    dst_name,
                    src_asn,
                    dst_asn,
                    src_continent,
                    dst_continent,
                    cdn_providers_dict[key],
                    completeness_factor,
                ]
                + list(statistics_info)
                + [
                    theoretical_min,
                    min_inflation,
                    median_inflation,
                    ninetieth_percentile_inflation,
                    distances[key],
                    distances_v2[key],
                    theoretical_rtt_v2[key],
                    min_inflation_v2,
                    median_inflation_v2,
                    ninetieth_percentile_inflation_v2,
                ]
            )
