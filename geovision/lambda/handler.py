import os
import json
import base64
import boto3
import traceback
from datetime import datetime

from urllib.parse import unquote

# S3 prompt source
PROMPT_BUCKET = "azrius-data"
PROMPT_KEY = "geovision/agent/zen_guide/image_process.txt"

# Initialize the Bedrock Runtime client. In Lambda, credentials are typically provided by the execution role.
bedrock_client = boto3.client("bedrock-runtime")

# Initialize the S3 client
s3_client = boto3.client("s3")

# The Bedrock model ID can be overridden via environment variable, otherwise use Haiku v1
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# Only process these image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}


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


def load_prompt_template():
    response = s3_client.get_object(Bucket=PROMPT_BUCKET, Key=PROMPT_KEY)
    return response["Body"].read().decode("utf-8")


def parse_filename(key):
    # Example: 2025-06-17/41.9291_-71.4518/2025-06-17T135157.758Z_0.6332678198814392.png
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

    timestamp_str, rad_str = filename.replace(".png", "").split("_")
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


def lambda_handler(event, context):
    """
    Entry point for S3 ObjectCreated events.
    """
    # print(f"Event: {json.dumps(event)}")

    records = event.get("Records", [])
    # print(f"Records: {json.dumps(event)}")

    for record in records:
        # print("\tReceived record: %s", json.dumps(record))

        sns_event = record.get("Sns", {})
        sns_records = sns_event.get("Message", {})

        # print(f"SNS Records: {json.dumps(sns_records)}")

        for sns_record in json.loads(sns_records)["Records"]:
            # print(f"\tSNS Record: {sns_record}")
            try:

                # Extract bucket and key from the S3 event
                bucket_name = sns_record["s3"]["bucket"]["name"]
                object_key = unquote(sns_record["s3"]["object"]["key"])

                # Skip non-image files
                _, ext = os.path.splitext(object_key.lower())
                if ext not in IMAGE_EXTENSIONS:
                    print(f"Skipping non-image object: s3://{bucket_name}/{object_key}")
                    continue

                # Load the prompt template from S3
                prompt_template = load_prompt_template()
                metadata = parse_filename(object_key)

                # Download the image bytes from S3
                s3_obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                image_bytes = s3_obj["Body"].read()

                # Encode to Base64
                encoded_image = base64.b64encode(image_bytes).decode()

                # Construct the payload for the Bedrock model
                payload = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": encoded_image,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "You are an AI assistant that describes images.",
                                },
                            ],
                        }
                    ],
                    "max_tokens": 512,
                    "anthropic_version": "bedrock-2023-05-31",
                }

                print("Invoking Bedrock model with payload:", json.dumps(payload))
                # Invoke the Bedrock model
                response = bedrock_client.invoke_model(
                    modelId=MODEL_ID,
                    contentType="application/json",
                    body=json.dumps(payload),
                )

                # Read and parse the model's response
                output_binary = response["body"].read()
                output_json = json.loads(output_binary)
                description = output_json["content"][0]["text"]

                caption = prompt_template.format(
                    timestamp=metadata["timestamp"],
                    latitude=metadata["latitude"],
                    longitude=metadata["longitude"],
                    compass_direction=metadata["orientation"],
                    description=description,
                )

                # Log the result. You can modify this to write back to S3, a database, etc.
                print(f"Processed image: s3://{bucket_name}/{object_key}")
                print(f"AI description: {caption}")

                # Write the description back to S3 as a .txt file
                # e.g. if object_key is "path/to/image.jpg",
                # this will write to "path/to/image.txt"
                base_key, _ext = os.path.splitext(object_key)
                text_key = f"{base_key}.txt"

                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=text_key,
                    Body=caption.encode("utf-8"),
                    ContentType="text/plain",
                )
                print(f"Wrote description to s3://{bucket_name}/{text_key}")

            except Exception as e:
                # If anything goes wrong, log it and continue with the next record
                print(traceback.format_exc())
                print(f"Error processing s3://{bucket_name}/{object_key}: {str(e)}")

    return {"statusCode": 200, "body": json.dumps({"message": "OK"})}
