"""
CloudFormation custom resource to create an admin user in the
Cognito User Pool. Uses username and password environment variables
sent in.
"""

import boto3
from botocore.exceptions import ClientError
import cfnresponse


def create_admin_user(cognito_client_id, cognito_user_pool_id, username, password):
    """Create user and set password in Cognito User Pool"""
    cognitoClient = boto3.client("cognito-idp")

    # Create Cognito user
    result = cognitoClient.sign_up(
        ClientId=cognito_client_id,
        Username=username,
        Password=password,
        UserAttributes=[
            {"Name": "custom:group", "Value": "admin"},
            {"Name": "phone_number", "Value": "+18005551212"},
        ],
    )
    result = cognitoClient.admin_confirm_sign_up(
        UserPoolId=cognito_user_pool_id, Username=username
    )


def main(event, context):
    import os
    import logging as log
    import boto3
    import cfnresponse

    log.getLogger().setLevel(log.INFO)

    # This needs to change if there are to be multiple resources
    # in the same stack
    physical_id = "CongnitoCreateAdminUser" 

    try:
        log.info("Input event: %s", event)
        log.info("Environment variables: %s", os.environ)

        # Check if this is a Create and we're failing Creates
        if event["RequestType"] == "Create" and event["ResourceProperties"].get(
            "FailCreate", False
        ):
            raise RuntimeError("Create failure requested")
        elif event["RequestType"] == "Create":
            # Operations to perform during Create
            create_admin_user(
                os.environ["COGNITO_CLIENT_ID"],
                os.environ["COGNITO_USER_POOL_ID"],
                os.environ["ADMIN_USERNAME"],
                os.environ["ADMIN_PASSWORD"],
            )
            attributes = {
                "Response": f"{physical_id} CREATE performed, admin user: {os.environ['ADMIN_USERNAME']} created"
            }
        elif event["RequestType"] == "Update":
            # Recreate admin user
            create_admin_user(
                os.environ["COGNITO_CLIENT_ID"],
                os.environ["COGNITO_USER_POOL_ID"],
                os.environ["ADMIN_USERNAME"],
                os.environ["ADMIN_PASSWORD"],
            )
            attributes = {
                "Response": f"{physical_id} UPDATE performed, admin user: {os.environ['ADMIN_USERNAME']} re-created"
            }
        else:
            # No operation required for delete, CloudFormation will delete the user pool
            attributes = {
                "Response": f"{physical_id} DELETE performed, no actions taken"
            }
        cfnresponse.send(event, context, cfnresponse.SUCCESS, attributes, physical_id)

    except Exception as e:
        log.exception(e)
        # cfnresponse's error message is always "see CloudWatch"
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
