"""
Methods to delete specific resources and return status

Function and resource created:

iam_user - IAM user deleted from account

"""

import os
import json
import logging
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def iam_user(username):
    """Delete the user from IAM"""

    client = boto3.client("iam")
    try:
        client.delete_login_profile(UserName=username)
        response = client.list_groups_for_user(UserName=username)
        for i in response["Groups"]:
            client.remove_user_from_group(UserName=username, GroupName=i["GroupName"])
        client.delete_user(UserName=username)
        return True
    except ClientError as e:
        logger.error(f"Error deleting IAM user: {username}, error: {e}")
        return False


def cognito_user(username, user_pool_id):
    """Delete the user from Cognito User Pool"""

    client = boto3.client("cognito-idp")
    try:
        client.admin_delete_user(UserPoolId=user_pool_id, Username=username)
        return True
    except ClientError as e:
        logger.error(f"Error deleting Cognito user: {username}, error: {e}")
        return False


def iot_thing_certificate(certificate_arn, thing_name):
    """Detach any policies from principal, then delete certificate and thing"""

    iot_client = boto3.client("iot")
    iot_data_client = boto3.client("iot-data")

    # Certificates must be disassociated with policies and things before being deleted
    # Detach policies from certificate
    try:
        response = iot_client.list_attached_policies(target=certificate_arn)
        for policy in response["policies"]:
            response = iot_client.detach_principal_policy(
                policyName=policy["policyName"], principal=certificate_arn
            )
        # Detach things from certificate
        response = iot_client.list_principal_things(principal=certificate_arn)
        for thing in response["things"]:
            response = iot_client.detach_thing_principal(
                thingName=thing, principal=certificate_arn
            )
        # Revoke and delete certificate
        response = iot_client.update_certificate(
            certificateId=certificate_arn.split("/")[-1], newStatus="REVOKED"
        )
        response = iot_client.delete_certificate(
            certificateId=certificate_arn.split("/")[-1], forceDelete=False
        )
    except ClientError as e:
        logger.error(f"ERROR deleting IoT certificate, error: {e}")
        return False

    # With certificate deleted, delete thing shadown and thing
    response = iot_data_client.delete_thing_shadow(thingName=thing_name)
    response = iot_client.delete_thing(thingName=thing_name)


def clean_dispenser_tables(dispenser_id):
    """Remove entry from dispenser table and log to event table"""

    try:
        ddb = boto3.resource("dynamodb")
        log_entry = f"Account: Deleted record for dispenser: {dispenser_id}"
        ts = datetime.utcnow().isoformat() + "Z"

        # Delete dispenser entry
        dispenser_table = ddb.Table(os.environ["DISPENSER_TABLE"])
        dispenser_table.delete_item(Key={"dispenserId": dispenser_id})

        event_table = ddb.Table(os.environ["EVENT_TABLE"])
        item = {"dispenserId": dispenser_id, "timestamp": ts, "log": log_entry}
        event_table.put_item(Item=item)
        return True
    except ClientError as e:
        logger.error(f"ERROR: Could not delete dispenser {dispenser_id}, error: {e}")
        return False


def cognito_identity_iot_policy(cognito_identity_id, iot_policy):
    """Detach Cognito principal from IoT policy"""

    print(f"Attempting to detach identity: {cognito_identity_id} from policy: {iot_policy}")
    try:
        client = boto3.client("iot")
        client.detach_policy(
            policyName=iot_policy,
            target=cognito_identity_id
        )
        return True
    except ClientError as e:
        logger.error(
            f"Detaching Cogntio identity {cognito_identity_id} from IoT Policy {iot_policy}, error: {e}"
        )
        return False


def cloud9(environment_id):
    """Delete Cloud9 instance and environment"""

    try:
        client = boto3.client("cloud9")
        client.delete_environment(environmentId=environment_id)
        return True
    except ClientError as e:
        logger.error(
            f"Deleting Cloud9 environment and instance {environment_id}, error: {e}"
        )
        return False
