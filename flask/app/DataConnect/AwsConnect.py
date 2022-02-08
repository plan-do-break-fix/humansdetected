#!/bin/python3
from email.message import Message
from os import environ
from typing import Tuple

import mysql.connector
import boto3

def get_rds_connection() -> mysql.connector.connection:
    try:
        conn = mysql.connector.connect(host=environ["RDS_HOSTNAME"],
                                       user=environ["RDS_USERNAME"],
                                       passwd=environ["RDS_PASSWORD"],
                                       port=environ["RDS_PORT"],
                                       database=environ["RDS_DB_NAME"]
                                       )
        return conn
    except ValueError as e:
        print(f"Required environment variables not found.\n{e}")
    except Exception as e:
        print(f"Connection to RDS instance failed.\n{e}")
    return False



class SQS_Connection:

    def __init__(self, url: str):
        self.conn = boto3.client("sqs")
        self.url = url
        
    def send(self, body: str, attributes: dict) -> dict:
        response = self.conn.send_message(
            QueueUrl = self.url,
            DelaySeconds = 1,
            MessageAttributes = attributes,
            MessageBody = body)
        return response

    def receive(self) -> dict:
        response = self.conn.receive_message(
            QueueUrl = self.url,
            AttributeNames = ["SentTimestamp"],
            MaxNumberOfMessages = 1,
            MessageAttributeNames = ["All"],
            VisibilityTimeout = 0,
            WaitTimeSeconds = 0
        )
        return response

    def delete(self, receipt_handle: str) -> bool:
        self.conn.delete_message(
            QueueUrl = self.url,
            ReceiptHandle = receipt_handle
        )
        return True
