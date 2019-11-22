"""
CloudFormation custom resource to delete any participant users and resources
that have been left.
"""

import os
import json
import logging as log
import boto3
from botocore.exceptions import ClientError
import cfnresponse
from boto3.dynamodb.conditions import Key, Attr

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

log.getLogger().setLevel(log.INFO)

ddb_client = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")

def delete_participant_users(user_table):
    """Read each non-admin userName and invoke lambda to delete the user, returns
    total delete participant users"""

    table = ddb_client.Table(user_table)

    delete_function_arn = os.environ["DELETE_USER_LAMBDA_FUNCTION"]
    # Set event base to pass delete checks
    event = {
        "requestContext": {"authorizer": {"claims": {"custom:group": "admin"}}},
        "body": "",
    }

    # First call and process
    deleted_users = 0
    response = table.scan(ProjectionExpression="userName")
    for i in response["Items"]:
        # Invoke Lambda with username to delete
        if i["userName"] != "admin":
            print(f"deleting user {i['userName']}")
            event["body"] = json.dumps({"username": i["userName"]})
            lambda_client.invoke(
                FunctionName=delete_function_arn, Payload=json.dumps(event)
            )
            deleted_users += 1

    while "LastEvaluatedKey" in response:
        response = table.scan(
            ProjectionExpression="userName",
            Limit=1,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        for i in response["Items"]:
            # Invoke Lambda with username to delete
            if i["userName"] != "admin":
                print(f"deleting user {i['userName']}")
                event["body"] = json.dumps({"username": i["userName"]})
                lambda_client.invoke(
                    FunctionName=delete_function_arn, Payload=json.dumps(event)
                )
                deleted_users += 1
    return deleted_users


def main(event, context):
    # This needs to change if there are to be multiple resources
    # in the same stack
    physical_id = "DeleteParticipantUsers"

    try:
        log.info("Input event: %s", event)
        log.info("Environment variables: %s", os.environ)

        # Check if this is a Create and we're failing Creates
        if event["RequestType"] == "Create" and event["ResourceProperties"].get(
            "FailCreate", False
        ):
            raise RuntimeError("Create failure requested")
        elif event["RequestType"] == "Create":
            # No operation required for create, only act on delete
            attributes = {
                "Response": f"{physical_id} CREATE performed, no actions taken"
            }
        elif event["RequestType"] == "Update":
            # No operation required for update, only act on delete
            attributes = {
                "Response": f"{physical_id} UPDATE performed, no actions taken"
            }
        else:
            # delete all users and return
            response = delete_participant_users(os.environ["USER_TABLE"])
            attributes = {
                "Response": f"{physical_id} DELETE performed, {response} users deleted"
            }
        cfnresponse.send(event, context, cfnresponse.SUCCESS, attributes, physical_id)

    except Exception as e:
        log.exception(e)
        # cfnresponse's error message is always "see CloudWatch"
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
