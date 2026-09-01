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

def bucket_exists(s3_client, bucket_name):
    response = s3_client.list_buckets()

    for bucket in response["Buckets"]:
        if bucket["Name"] == bucket_name:
            return True

    return False

def main():
    s3_client = create_s3_client()

    if bucket_exists(s3_client, RAW_BUCKET_NAME):
        print(f"Bucket {RAW_BUCKET_NAME} already exists.")
    else:
        s3_client.create_bucket(Bucket=RAW_BUCKET_NAME)
        print(f"Bucket {RAW_BUCKET_NAME} created.")


if __name__ == "__main__":
    main()