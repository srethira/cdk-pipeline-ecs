from __future__ import print_function

import json
import uuid
import decimal
import os
import boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb')

# set environment variable
TABLE_NAME = os.environ['TABLE_NAME']


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    # put item in table
    response = table.get_item(
        Item={
            'first_name': 'srikanth'
        }
    )

    return {
        'statusCode': 200,
    }