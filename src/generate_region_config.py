
import json
import subprocess
import sys
from RegionTypes import Cell, RegionInfo, RegionsConfig

def read_and_parse_plugin(plugin_path):
    # Define the command to execute tes3conv
    command = ["./tes3conv", plugin_path]

    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the command was executed successfully
    if result.returncode != 0:
        raise Exception(f"tes3conv failed with return code {result.returncode}: {result.stderr}")

    # Parse the JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON output: {str(e)}")

    return data

def generate_color(region: str):
    # Generate a color based on the region name
    # This is a simple example and can be improved
    # by using a more sophisticated algorithm
    region_hash = hash(region)
    r = (region_hash & 0xFF0000) >> 16
    g = (region_hash & 0x00FF00) >> 8
    b = region_hash & 0x0000FF
    return f"#{r:02X}{g:02X}{b:02X}4D"


def extract_from_plugin(plugin_path) -> RegionsConfig:
    # Use the implemented function to read and parse the plugin
    plugin_data = read_and_parse_plugin(plugin_path)

    # Filter for locations and extract relevant data (assuming plugin_data structure is known and consistent)
    locations = [entry for entry in plugin_data if entry['type'] == 'Cell']

    config = {
        "Region": {}
    }
    for location in locations:
        if not location.get('region'):
            continue
        cellX = location['data']['grid'][0]
        cellY = location['data']['grid'][1]
        regionID = location['region']

        if regionID not in config["Region"]:
            config["Region"][regionID] = {
                "name":  location["region"],
                "color": generate_color(regionID),
                "locations": [],
            }

        config["Region"][regionID]["locations"].append({
            "cellX": cellX,
            "cellY": cellY
        })

    return config

# python src/generate_region_config.py "${MW_DATA_FILES}/TR_Mainland.esm" "tr_regions.json"
if __name__ == "__main__":
    # args from command line
    plugin_path = sys.argv[1]
    output_path = sys.argv[2]
    extract_from_plugin(plugin_path, output_path)