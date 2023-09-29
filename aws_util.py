import os

import boto3
from dotenv import load_dotenv

load_dotenv()
QUEUE_NAME = os.getenv('QUEUE_NAME')

sqs = boto3.client('sqs',
                   region_name=os.getenv("AWS_REGION"),
                   aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                   aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

s3 = boto3.client('s3',
                   region_name=os.getenv("AWS_REGION"),
                   aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                   aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))


def send_sqs(payload):
    queue_url = os.getenv("SQS_QUEUE_URL")
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=payload
    )
    return response.get('MessageId')
