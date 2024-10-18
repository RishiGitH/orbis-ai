import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def upload_file_to_s3(file, object_name=None):
    """Upload a file to an S3 bucket

    :param file: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file.name

    # Upload the file
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_S3_REGION_NAME)
    try:
        s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{object_name}"