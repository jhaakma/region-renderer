import json
from PIL import Image, ImageDraw, ImageFont
import sys

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from RegionTypes import Cell, RegionInfo

def generate_color(region: str):
    # Generate a color based on the region name
    # This is a simple example and can be improved
    # by using a more sophisticated algorithm
    region_hash = hash(region)
    r = (region_hash & 0xFF0000) >> 16
    g = (region_hash & 0x00FF00) >> 8
    b = region_hash & 0x0000FF
    return f"#{r:02X}{g:02X}{b:02X}4D"

def add_legend_to_image(img, regions):
    for regionTypeId, info in regions.items():
        # Create a new image for the legend with a transparent background
        legend_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(legend_img)

        # Define starting position for the legend and text properties
        x_start, y_start = img.size[0] * 0.85, 100  # Adjust these values as needed
        padding = 10
        font_size = 64
        font = ImageFont.truetype("assets/ARIAL.TTF", font_size)  # Ensure you have this font or choose another

        # Iterate over region types to draw the legend
        for i, (regionTypeId, info) in enumerate(regions.items()):
            color = ""
            if "color" in info:
                color = info["color"]
            else:
                color = generate_color(regionTypeId)

            name = ""
            if "name" in info:
                name = info["name"]
            else:
                name = regionTypeId

            # remove " Region" from end of string if its there
            if name.endswith(" Region"):
                name = name[:-7]

            # Draw a small rectangle for the color
            draw.rectangle([x_start, y_start + i * (font_size + padding), x_start + font_size, y_start + font_size + i * (font_size + padding)], fill=color)

            # Draw the name text next to the rectangle
            draw.text((x_start + font_size + padding, y_start + i * (font_size + padding)), name, fill="black", font=font)

        # Paste the legend onto the main image
        img.paste(legend_img, (0, 0), legend_img)

    return img

def draw_circle(draw, center, radius, color):
    left_up_point = (center[0] - radius, center[1] - radius)
    right_down_point = (center[0] + radius, center[1] + radius)
    draw.ellipse([left_up_point, right_down_point], fill=color)

def draw_rectangle(draw, bottom_left, width, height, color):
    top_right = (bottom_left[0] + width, bottom_left[1] + height)
    draw.rectangle([bottom_left, top_right], fill=color)

def render_map(start_x, start_y, end_x, end_y, image_path, config_path, dpi=100):
    # Load the background image
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Get regions from regions.json
    with open(config_path) as f:
        regions = json.load(f)

    # Create a transparent layer for each location type
    transparent_layers = {region_name: Image.new('RGBA', img.size, (255, 255, 255, 0)) for regionId, region in regions.items() for region_name in region}

    # Assuming img_width and img_height are the dimensions of the image in pixels
    grid_width = end_x - start_x  # Grid width in locations
    grid_height = end_y - start_y  # Grid height in locations
    print("grid_width", grid_width)
    print("grid_height", grid_height)

    # Calculate scale factors
    scale_x = img_width / grid_width
    scale_y = img_height / grid_height
    print("scale_x", scale_x)
    print("scale_y", scale_y)

    # Draw shapes on the respective transparent layer
    for category, category_entries in regions.items():
        for region_name, region in category_entries.items():
            region: RegionInfo = region
            draw = ImageDraw.Draw(transparent_layers[region_name])
            print("region", region_name)

            color = ""
            if "color" in region:
                color = region["color"]
            else:
                color = generate_color(region_name)

            if len(color) == 7:  # Assuming color is in the format '#RRGGBB'
                color += '4D'  # Append alpha value for 30% opacity
            for cell in region["locations"]:
                #Scale coordinates and dimensions
                adjusted_cell_x = (cell["cellX"] - start_x) * scale_x
                adjusted_cell_y = img_height - (cell["cellY"] - start_y) * scale_y


                if "radius" in cell:
                    # Render as a circle
                    scaled_radius = cell["radius"] * (scale_x + scale_y) / 2  # Average scale for radius

                    draw_circle(draw, (adjusted_cell_x, adjusted_cell_y), scaled_radius, color)
                else:
                    #print("cell", cell)
                    width = cell.get("width", 1)
                    height = cell.get("height", 1)
                    # Render as a rectangle
                    scaled_width = width * scale_x
                    scaled_height = height * scale_y
                    draw_rectangle(draw, (adjusted_cell_x, adjusted_cell_y), scaled_width, scaled_height, color)

    # Blend each transparent layer with the background image
    for layer in transparent_layers.values():
        img = Image.alpha_composite(img.convert('RGBA'), layer)

    # Add legend to the image if regionType.active is True or not specified
    img = add_legend_to_image(img, regions)

    # Save the final image to a file
    img.save("regions.png")

# Example usage
#render_map(-42, -64, 61, 38, "regionmap.png", "/mnt/c/games/Morrowind installs/main/Morrowind/Data Files/MWSE/config/UltimateFishing_regions.json")
if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 7:
        print("Usage: python render.py start_x start_y end_x end_y image_path config_path")
        sys.exit(1)

    # Parse the command line arguments
    start_x = int(sys.argv[1])
    start_y = int(sys.argv[2])
    end_x = int(sys.argv[3])
    end_y = int(sys.argv[4])
    image_path = sys.argv[5]
    config_path = sys.argv[6]

    # Call the render_map function with the provided arguments
    render_map(start_x, start_y, end_x, end_y, image_path, config_path)