"""
Cognito UserPool Pre-SignUp Trigger

Executed after sign up step and before completion of sign up
"""

import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Main entry into function"""
    logger.info("Received event: %s", json.dumps(event))

    cog_client = boto3.client("cognito-idp")
    ddb_client = boto3.client("dynamodb")

    # If phone number already on confirmed user, reject
    try:
        phone_number = event["request"]["userAttributes"]["phone_number"]
    except KeyError:
        raise Exception(f"User attribute 'phone_number' not found in Cognito User Pool")
    # Check all other entries
    response = cog_client.list_users(
        UserPoolId=event["userPoolId"], Filter=f'phone_number = "{phone_number}"'
    )
    if len(response["Users"]) > 0:
        raise Exception(
            f"Phone number {phone_number} already associated with an account"
        )

    response = ddb_client.scan(TableName=os.environ["USER_TABLE"], Select="COUNT")
    if response["Count"] > int(os.environ["PARTICIPANT_LIMIT"]):
        raise Exception(
            "Maximum participants reached, please see workshop leader for assistance"
        )

    return event
