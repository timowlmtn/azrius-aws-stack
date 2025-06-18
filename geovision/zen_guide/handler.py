import boto3
import re
import os
import json
import traceback
from datetime import datetime

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "amazon.nova-lite-v1:0"

BUCKET = os.environ.get("BUCKET_NAME", "azrius-data")


def list_folder_images(folder):
    prefix = f"{folder}/"
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET, Prefix=prefix)

    keys = []
    for page in pages:
        for obj in page.get("Contents", []):
            if obj["Key"].lower().endswith(".jpg") or obj["Key"].lower().endswith(
                ".png"
            ):
                keys.append(obj["Key"])
    return keys


def degrees_to_compass(degrees):
    directions = [
        "North",
        "North-East",
        "East",
        "South-East",
        "South",
        "South-West",
        "West",
        "North-West",
    ]
    rounded_degrees = round(degrees) % 360
    index = round(rounded_degrees / 45) % 8
    return f"{directions[index]} ({rounded_degrees}°)"


def parse_filename(key):
    parts = key.split("/")
    print(f"Parts: {parts}")

    app = parts[0]
    user = parts[1]
    project = parts[2]
    file_date = parts[3]
    lat_lon = parts[4]
    filename = parts[5]

    print(
        f"App: {app}, User: {user}, Project: {project}, File Date: {file_date}, Lat Lon: {lat_lon}, Filename: {filename}"
    )

    latitude, longitude = lat_lon.split("_")

    timestamp_str, rad_str = filename.replace(".jpg", "").replace(".png", "").split("_")
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H%M%S.%fZ")
    radians = float(rad_str)
    orientation = degrees_to_compass(radians)

    return {
        "date": file_date,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp.strftime("%B %d, %Y at %I:%M %p UTC"),
        "orientation": orientation,
    }


# images_with_meta: list of dicts with bucket, key, heading
def load_image_bytes(bucket, key):
    s3 = boto3.client("s3")
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "Invalid JSON body"}

    images_with_meta = []
    try:
        folder = body.get("folder")

        if not folder:
            return {"statusCode": 400, "body": "Missing folder"}

        # 1. Gather all user image keys from S3
        keys = list_folder_images(folder)
        if not keys:
            return {"statusCode": 404, "body": f"No images found for folder {folder}"}

        print(f"Found {len(keys)} images for folder {folder}")

        # 2. Fetch and embed each image
        for key in keys:
            metadata = parse_filename(key)
            images_with_meta.append(
                {"path": key, "orientation": metadata["orientation"]}
            )

        content = images_with_meta

        # Read and encode all images
        content = []
        for idx, item in enumerate(images_with_meta, start=1):
            bytes = load_image_bytes(BUCKET, item["path"])
            content.append({"image": {"format": "jpeg", "source": {"bytes": bytes}}})
            content.append({"text": f"Image {idx} heading: {item['orientation']}"})

        # Construct the prompt with metadata
        prompt_text = f"""
        You are a spatial reasoning expert with strong Feng Shui knowledge.

        You are given {len(images_with_meta)} images of a room taken from different angles.
        Each image includes a compass orientation.

        Please:
        1. Reconstruct the room layout as best you can.
        2. Identify key furniture positions.
        3. Recommend 3 Feng Shui improvements.

        """

        # Add your instruction text afterward
        content.append({"text": prompt_text})

        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[
                {
                    "text": "You are a spatial reasoning assistant with Feng Shui expertise."
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            inferenceConfig={"maxTokens": 800, "temperature": 0.5},
        )

        # Extract answer
        # Raw Nova reply
        raw_text = response["output"]["message"]["content"][0]["text"]

        # Use regex or simple string splits to extract structured parts
        sections = re.split(r"###\s*", raw_text)

        # Helper function to clean and normalize
        def extract_section(sections, title):
            for section in sections:
                if section.strip().lower().startswith(title.lower()):
                    return section.strip()[len(title) :].strip()
            return ""

        # Extract sections
        layout_text = extract_section(sections, "Room Layout Reconstruction")
        furniture_text = extract_section(sections, "Key Furniture Positions")
        feng_shui_text = extract_section(sections, "Feng Shui Improvements")

        # Final structured output
        structured_output = {
            "room_layout": layout_text,
            "furniture_positions": furniture_text,
            "feng_shui_advice": feng_shui_text,
            "image_count": len(images_with_meta),  # optional metadata
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(structured_output),
        }
    except Exception as e:
        # If anything goes wrong, log it and continue with the next record
        print(traceback.format_exc())
        print(f"Error: {str(e)}")

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
