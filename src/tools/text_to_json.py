import json


def text_to_json(input_file, output_file):
    cdn_dict = {}

    with open(input_file, "r") as file:
        for line in file:
            domain, cdn_name, _, _ = line.split()

            if cdn_name not in cdn_dict:
                cdn_dict[cdn_name] = []

            cdn_dict[cdn_name].append(domain)
    for keys, vals in cdn_dict.items():
        print(len(vals))
    with open(output_file, "w") as json_file:
        json.dump(cdn_dict, json_file, indent=2)


# Replace 'input.txt' and 'output.json' with your actual file names
text_to_json(
    "../../data/targets/cdn-targets-info.txt",
    "../../data/targets/all_cdn_domains_new.json",
)
