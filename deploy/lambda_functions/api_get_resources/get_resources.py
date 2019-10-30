"""
Method to return users configuration details, and if they don't
exist, to create the specific assets

"""

import json
import os
import logging
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal
from collections.abc import MutableMapping


import create_resources as AWS_resource

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global Variables - Lambda manages CORS
httpHeaders = {"Access-Control-Allow-Origin": "*"}
ddb = boto3.resource("dynamodb")


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, decimal.Decimal):  # pylint: disable=E0602
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def scrub_event(event, keys):
    """Removes body which is POSTed data"""
    keys_set = set(keys)

    modified_dict = {}
    for key, value in event.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = scrub_event(value, keys_set)
            else:
                modified_dict[key] = value
    return modified_dict


def handler(event, context):
    """This function does not process any parameters, but returns complete
     details of the user based on username in token"""

    try:
        cognito_identity_id = json.loads(event["body"])["cognitoIdentityId"]
        scrubbed_event = scrub_event(event, ["body"])
    except Exception as e:
        logger.error("Password parameter not found in body, error: %s", e)
        retval = {
            "body": "ERROR: password parameter not sent",
            "headers": httpHeaders,
            "statusCode": 200,
        }
        return retval
    # Log event without body component (which contains password)
    logger.info("Received event: {}".format(json.dumps(scrubbed_event)))
    print(f"cog id: {cognito_identity_id}")

    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    dispenser_id = event["requestContext"]["authorizer"]["claims"]["custom:dispenserId"]
    table = ddb.Table(os.environ["USER_TABLE"])

    # Query user and return contents of assets
    response = table.query(KeyConditionExpression=Key("userName").eq(username))
    if len(response["Items"]) == 1:
        user_db_record = response["Items"][0]
        if response["Items"][0]["assets"] == "CREATING":
            # Another call has started the creation process
            time.sleep(5)
            logger.error(f"Resources for {username} already in progress")
            retval = {
                "body": json.dumps(
                    {"message": "ERROR: Could not create all resources, see log files"}
                ),
                "headers": httpHeaders,
                "statusCode": 200,
            }
            return retval
        if response["Items"][0]["assets"] == None:
            # Create assets

            # First set user record to status of creating in case multiple API calls are made
            response = table.put_item(
                Item={
                    "userName": username,
                    "dispenserId": dispenser_id,
                    "assets": "CREATING",
                }
            )

            assets = {}
            try:
                # IAM user
                iam_user = AWS_resource.iam_user(
                    username, os.environ["USER_PERMISSIONS_GROUP"]
                )
                assets.update(iam_user)
                # IoT Thing and certificates
                iot = AWS_resource.iot_thing_certificate(
                    dispenser_id=dispenser_id,
                    iot_policy=os.environ["IOT_POLICY_DISPENSER_LIMITED"],
                )
                assets.update(iot)
                # Associate IoT policy with Cognito identity
                cognito = AWS_resource.cognito_iot_policy(
                    cognito_identity_id=cognito_identity_id,
                    iot_policy=os.environ["IOT_POLICY_CLIENT"]
                )
                assets.update(cognito)
                # Cloud9 Instance
                cloud9 = AWS_resource.cloud9_instance(
                    iam_user["iam_user"]["userArn"], os.environ["CLOUD9_INSTANCE_SIZE"]
                )
                assets.update(cloud9)
                # Initial dispenser status in DDB - no assets returned
                AWS_resource.initialize_dispenser_tables(dispenser_id)
            except Exception as e:
                logger.error("Error during creation of resources, error: %s", e)
                retval = {
                    "body": "ERROR: Could not create all resources, see log files",
                    "headers": httpHeaders,
                    "statusCode": 200,
                }
                return retval
            user_db_record["assets"] = assets
            response = table.put_item(
                Item={
                    "userName": username,
                    "dispenserId": dispenser_id,
                    "assets": user_db_record["assets"],
                }
            )
        # Return completed assets
        body = json.dumps(user_db_record)
        retval = {"body": json.dumps(body), "headers": httpHeaders, "statusCode": 200}
    else:
        # should not reach, only authenticated users can hit this
        logger.error("Exception, user record not found in UserTable")
        retval = {"body": json.dumps({}), "headers": httpHeaders, "statusCode": 500}

    return retval
