# app/s3_client.py
import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import certifi
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

boto_config = Config(
    region_name=AWS_REGION,
    retries={"max_attempts": 10, "mode": "standard"},
    connect_timeout=10,
    read_timeout=60,
    signature_version="s3v4",
)

def get_s3_client():
    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
        # credentials not set; return None (upload endpoints should handle this)
        return None
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
        verify=certifi.where()
    )

# def upload_fileobj_to_s3(file_obj, bucket: str, key: str):
#     s3 = get_s3_client()
#     if s3 is None:
#         raise RuntimeError("AWS credentials not configured")
#     try:
#         s3.upload_fileobj(file_obj, bucket, key)
#     except ClientError as e:
#         raise
# app/s3_client.py
import os
import boto3
import certifi
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

def get_s3_client():
    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
        return None
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
        verify=certifi.where()  # ✅ Fixes SSL validation error
    )

def upload_fileobj_to_s3(file_obj, bucket: str, key: str):
    s3 = get_s3_client()
    if s3 is None:
        raise RuntimeError("AWS credentials not configured")

    try:
        print(f"Uploading {key} to bucket {bucket}...")
        s3.upload_fileobj(file_obj, bucket, key)
        print("✅ Upload successful!")
    except ClientError as e:
        print("❌ AWS ClientError:", e)
        raise
    except Exception as e:
        print("❌ Unexpected error:", e)
        raise







