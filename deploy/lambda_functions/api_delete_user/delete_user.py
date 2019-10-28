"""
Method to delete all user assets based on content in the
DynamoDB UserTable.
"""

import json
import os
import logging
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


import delete_resources as AWS_delete

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global Variables - Lambda manages CORS
httpHeaders = {"Access-Control-Allow-Origin": "*"}
ddb = boto3.resource("dynamodb")


def handler(event, context):
    """Deletes all user content based on username provided in body,
    only accessible from authenticated users with the custom:group=admin"""

    logger.info(f"Received event: {json.dumps(event)}")
    try:
        if event["requestContext"]["authorizer"]["claims"]["custom:group"] != "admin":
            logger.error("User does not have permissions to call this function")
            retval = {
                "body": "ERROR: User does not have permissions to call this function",
                "headers": httpHeaders,
                "statusCode": 200,
            }
            return retval
    except KeyError:
        logger.error("custom:group field not found in token")
        retval = {
            "body": "ERROR: custom:group field not found in token",
            "headers": httpHeaders,
            "statusCode": 200,
        }
        return retval

    username = json.loads(event["body"])["username"]
    user_pool_id = os.environ["USER_POOL_ID"]
    table = ddb.Table(os.environ["USER_TABLE"])

    # Query user and return contents of assets
    response = table.query(KeyConditionExpression=Key("userName").eq(username))
    if len(response["Items"]) == 1:
        if response["Items"][0]["assets"] == None:
            # User exists but no assets have been created. Only delete the Cognito user
            AWS_delete.cognito_user(username, user_pool_id)
            logger.info(f"INFO: User: {username} delete from Cognito, no other assets found")
        else:
            assets = response["Items"][0]["assets"]
            # Remove dispenser from DispenserTable (and entry into to event table)
            AWS_delete.clean_dispenser_tables(assets["iot"]["thingName"])
            # Detach Cognito identity from IoT policy
            AWS_delete.cognito_identity_iot_policy(
                cognito_identity_id = assets["cognito"]["principalId"],
                iot_policy=assets["cognito"]["iotPolicy"]
            )
            # Delete AWS thing, cert
            AWS_delete.iot_thing_certificate(
                assets["iot"]["certificateArn"], assets["iot"]["thingName"]
            )
            AWS_delete.cloud9(environment_id=assets["cloud9"]["environmentId"])
            # Delete Cognito
            AWS_delete.cognito_user(username, user_pool_id)
            # Delete IAM user last
            AWS_delete.iam_user(username)
        try:
            # Delete User's DynamoDB record
            response = table.delete_item(Key={"userName": username})
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(e.response["Error"]["Message"])
            else:
                raise
        logger.info(f"INFO: User: {username} assets and entry deleted")
        retval = {
            "body": f"INFO: User: {username} assets and entry deleted",
            "headers": httpHeaders,
            "statusCode": 200,
        }
    else:
        retval = {
            "body": f"WARNING: User: {username} not found, no action taken",
            "headers": httpHeaders,
            "statusCode": 200,
        }
    return retval
