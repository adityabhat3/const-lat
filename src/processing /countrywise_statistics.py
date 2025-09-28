import os
import json
from geoip2.database import Reader

# Path to your MaxMind GeoIP2 database file
geoip_database_file = "../../data/geolocation/GeoLite2-City.mmdb"


# Function to get IP information (latitude and longitude)
def get_ip_info(ip_address):
    if ip_address is None:
        return None, None
    with Reader(geoip_database_file) as reader:
        try:
            response = reader.city(ip_address)
            latitude = response.location.latitude
            longitude = response.location.longitude
            return latitude, longitude
        except Exception as e:
            print("Error:", e)
            return None, None


# Function to get country and continent for an IP address
def get_country_and_continent(ip_address):
    with Reader(geoip_database_file) as reader:
        try:
            response = reader.city(ip_address)
            country = response.country.name
            continent = response.continent.code
            return country, continent
        except Exception as e:
            print("Error:", e)
            return None, None


giga = dict()


# count =
# Function to process the JSON files and compute the country and continent statistics
def process_json_file(file_path, counts_dict):
    with open(file_path, "r") as file:
        data = json.load(file)

    for measurement in data:
        src_addr = measurement.get("src_addr")
        dst_addr = measurement.get("dst_addr")
        prb_id = measurement.get("prb_id")
        # min_value = measurement.get("min")
        dst_name = measurement.get("dst_name")

        if (prb_id, dst_name) not in giga:
            giga[(prb_id, dst_name)] = 1
            counts_dict["count"] += 1

            if src_addr and dst_addr:
                # Get country and continent information for the source and destination IPs
                src_country, src_continent = get_country_and_continent(src_addr)
                dst_country, dst_continent = get_country_and_continent(dst_addr)

                if src_country is not None and dst_country is not None:
                    if src_country == dst_country:
                        counts_dict["same_country"] += 1
                    else:
                        counts_dict["different_country"] += 1

                    # Check if the pair is in North America - Europe (NA-EU)
                    if (src_continent == "NA" and dst_continent == "EU") or (
                        src_continent == "EU" and dst_continent == "NA"
                    ):
                        counts_dict["na_eu"] += 1


# Main function to process all files and compute requested statistics
if __name__ == "__main__":
    input_folder = "../../data/raw/"

    # Initialize the counts dictionary
    counts_dict = {"same_country": 0, "different_country": 0, "na_eu": 0, "count": 0}

    # Process all the files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            process_json_file(file_path, counts_dict)

    # Print the requested statistics from the counts dictionary
    print(f"(b) Number of pairs in the same country: {counts_dict['same_country']}")
    print(
        f"(c) Number of pairs in different countries: {counts_dict['different_country']}"
    )
    print(f"(d) Number of pairs in North America - Europe: {counts_dict['na_eu']}")
    print(counts_dict["count"])
