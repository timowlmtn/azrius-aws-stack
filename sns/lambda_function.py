import os
import json
import boto3

sns_client = boto3.client("sns")
TOPIC_ARN = os.environ["TOPIC_ARN"]


def lambda_handler(event, context):
    for record in event.get("Records", []):
        s3 = record.get("s3", {})
        bucket = s3.get("bucket", {}).get("name")
        key = s3.get("object", {}).get("key")
        if not key:
            continue

        lower_key = key.lower()
        if lower_key.endswith((".jpg", ".jpeg", ".png", ".gif")):
            message = {"bucket": bucket, "key": key}
            sns_client.publish(
                TopicArn=TOPIC_ARN,
                Message=json.dumps(message),
                Subject="New Image Uploaded",
            )

    return {"statusCode": 200, "body": json.dumps({"status": "success"})}
