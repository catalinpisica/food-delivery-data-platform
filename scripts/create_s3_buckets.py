import boto3

from delivery_simulator.object_storage import RAW_BUCKET_NAME, create_s3_client

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