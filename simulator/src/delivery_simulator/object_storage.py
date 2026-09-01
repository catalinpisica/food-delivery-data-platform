import boto3


S3_ENDPOINT_URL = "http://localhost:8333"
S3_ACCESS_KEY_ID = "admin"
S3_SECRET_ACCESS_KEY = "admin"
RAW_BUCKET_NAME = "food-delivery-raw"


def create_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
    )