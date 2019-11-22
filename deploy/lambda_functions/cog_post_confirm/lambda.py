"""
Cognito UserPool Post-Confirmation Trigger

Executed after the confirmation is validated:

- Create a dispenser entry in DynamoDB (next available entry)
- Add the dispenser field to the users entry in Cognito
"""

import os
import json
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cog_client = boto3.client("cognito-idp")
ddb_client = boto3.resource("dynamodb")


def set_dispenser_attrib(username, user_pool_id, dispenser_id):
    """Add dispenserId attribute to the user entry"""

    cog_client.admin_update_user_attributes(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[{"Name": "custom:dispenserId", "Value": dispenser_id}],
    )
def set_group_attrib(username, user_pool_id, group):
    """Add custom:group attribute to the user entry"""

    cog_client.admin_update_user_attributes(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[{"Name": "custom:group", "Value": group}],
    )


def handler(event, context):
    """Main entry into function"""
    logger.info("Received event: %s", json.dumps(event))
    logger.info("Received environ: %s", os.environ)

    # Create new user entry with username
    username = event["userName"]
    table = ddb_client.Table(os.environ["USER_TABLE"])

    # Get tracking record details (next dispenser)
    response = table.query(KeyConditionExpression=Key("userName").eq("admin"))

    # If first run (CloudFormation deploy or delete of UseTable records),
    # create tracking record and then the user - Completed during deployment of stack
    if len(response["Items"]) == 0:
        # First time, create the tracking record
        logging.info("No tracking record found in UserTable, creating admin user")
        response = table.put_item(Item={"userName": "admin", "nextDispenserId": "100"})

        # Create the user *if* it isn't the admin user
        if username != "admin":
            response = table.put_item(
                Item={"userName": username, "dispenserId": "100", "assets": None}
            )
            set_dispenser_attrib(
                username=username, user_pool_id=event["userPoolId"], dispenser_id="100"
            )
            set_group_attrib(
                username=username, user_pool_id=event["userPoolId"], group="user"
            )
        else:
            # Admin record was deleted, reset
            response = table.put_item(
                Item={"userName": username, "nextDispenserId": "100"}
            )
    else:
        # Create user with next dispenser
        disp_id = response["Items"][0]["nextDispenserId"]
        response = table.put_item(
            Item={"userName": "admin", "nextDispenserId": f"{int(disp_id)+1}"}
        )
        response = table.put_item(
            Item={"userName": username, "dispenserId": f"{disp_id}", "assets": None}
        )
        set_dispenser_attrib(
            username=username, user_pool_id=event["userPoolId"], dispenser_id=disp_id
        )
        set_group_attrib(
            username=username, user_pool_id=event["userPoolId"], group="user"
        )


    # No additional information is expected in the response, return event untouched
    return event
