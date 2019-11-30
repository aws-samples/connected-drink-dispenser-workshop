"""
Methods to create and return resource values

Function and resource created:

iam_user - IAM user assigned to specific group for role permissions

"""

import os
import json
import logging
import time
import random
import boto3
from decimal import Decimal
from datetime import datetime
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Root certificate for Amazon CA1. Source of truth here:
# https://www.amazontrust.com/repository/AmazonRootCA1.pem
amazon_root_ca_ca1 = """-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----"""

shadow_clear = json.dumps({"state": {"reported": None, "desired": None}})
shadow_initial = json.dumps(
    {
        "state": {
            "desired": {
                "led": "off",
                "led_ring": {"count": 1, "color": "#006600"},
                "dispense_time_ms": 2000,
            }
        }
    }
)


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB item to JSON"""

    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, decimal.Decimal):  # pylint: disable=E0602
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def create_password():
    """Create a random password"""
    animal_word_list = [
        "bat",
        "cat",
        "dog",
        "fish",
        "bird",
        "horse",
        "tiger",
        "mouse",
        "chicken",
        "cow",
        "donkey",
    ]
    building_word_list = [
        "house",
        "bridge",
        "store",
        "station",
        "attic",
        "floor",
        "wall",
        "window",
        "porch",
        "door",
        "room",
    ]
    if bool(random.getrandbits(1)):
        return f"{animal_word_list[random.randint(0, 10)]}{random.randint(100, 999)}{building_word_list[random.randint(0, 10)]}"
    else:
        return f"{building_word_list[random.randint(0, 10)]}{random.randint(100, 999)}{animal_word_list[random.randint(0, 10)]}"


def iam_user(username, iam_group):
    "Create user with random password and assign to IAM group name"

    iam_client = boto3.client("iam")
    asset = {"iam_user": {}}

    # Read current IAM password policy and store
    # TODO - check for existing policy - new accounts don't have them
    # NOTE - Not safe for multiple users make changes at the same time
    prodPasswordPolicy = iam_client.get_account_password_policy()["PasswordPolicy"]
    prodPasswordPolicy.pop("ExpirePasswords", None)
    temppol = {
        "MinimumPasswordLength": 6,
        "RequireSymbols": False,
        "RequireNumbers": True,
        "RequireUppercaseCharacters": False,
        "RequireLowercaseCharacters": True,
        "AllowUsersToChangePassword": False,
    }
    iam_client.update_account_password_policy(**temppol)
    result = iam_client.create_user(UserName=username)
    asset["iam_user"]["userArn"] = result["User"]["Arn"]
    asset["iam_user"]["username"] = result["User"]["UserName"]
    asset["iam_user"]["password"] = create_password()
    iam_client.create_login_profile(
        UserName=username,
        Password=asset["iam_user"]["password"],
        PasswordResetRequired=False,
    )
    iam_client.add_user_to_group(GroupName=iam_group, UserName=username)
    # Reset password policy back to original
    iam_client.update_account_password_policy(**prodPasswordPolicy)
    return asset


def iot_thing_certificate(dispenser_id, iot_policy):
    """Create IoT thing, private key and CSR, register with AWS IoT and 
    return iot assets"""

    iot_client = boto3.client("iot")
    iot_data_client = boto3.client("iot-data")
    asset = {"iot": {"thingName": dispenser_id}}

    # Create thing
    iot_client.create_thing(thingName=dispenser_id)

    # Create certificate and private key
    key = ec.generate_private_key(curve=ec.SECP256R1(), backend=default_backend())
    # key = rsa.generate_private_key(
    #     public_exponent=65537, key_size=2048, backend=default_backend()
    # )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    asset["iot"]["privateKey"] = private_key

    # Generate a CSR and set subject (CN=dispenserId)
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    # Provide various details about who we are.
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "NV"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Las Vegas"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "re:Invent 2084"),
                    x509.NameAttribute(NameOID.COMMON_NAME, dispenser_id),
                ]
            )
        )
        .sign(key, hashes.SHA256(), default_backend())
    )

    # Generate AWS IoT certificate
    # NOTE: Use the ECDHE-ECDSA-AES128-SHA256 and CA3 root for communication
    result = iot_client.create_certificate_from_csr(
        certificateSigningRequest=str(
            csr.public_bytes(serialization.Encoding.PEM), "utf-8"
        ),
        setAsActive=True,
    )
    asset["iot"]["certificateArn"] = result["certificateArn"]
    asset["iot"]["certificatePem"] = result["certificatePem"]
    asset["iot"]["rootCA"] = amazon_root_ca_ca1

    # Thing and certificate created, attach thing <-> certificate <-> policy
    # Policy to certificate
    iot_client.attach_principal_policy(
        policyName=iot_policy, principal=asset["iot"]["certificateArn"]
    )
    # Thing to certificate
    iot_client.attach_thing_principal(
        thingName=asset["iot"]["thingName"], principal=asset["iot"]["certificateArn"]
    )

    # Clear then create initial shadow state
    iot_data_client.update_thing_shadow(
        thingName=asset["iot"]["thingName"], payload=shadow_clear
    )
    # Then set initial state
    iot_data_client.update_thing_shadow(
        thingName=asset["iot"]["thingName"], payload=shadow_initial
    )
    return asset


def cognito_iot_policy(cognito_identity_id, iot_policy):
    """Attach Cognitio identity to IoT policy"""

    asset = {"cognito": {}}
    try:
        iot_client = boto3.client("iot")
        iot_client.attach_policy(policyName=iot_policy, target=cognito_identity_id)
        asset["cognito"]["principalId"] = cognito_identity_id
        asset["cognito"]["iotPolicy"] = iot_policy
        return asset
    except ClientError as e:
        logger.error(
            f"ERROR: Could not attach principal {cognito_identity_id} to policy {iot_policy}, error: {e}"
        )
        return False


def initialize_dispenser_tables(dispenser_id):
    """With assets created, make the initial entries and credit for the participant's
    dispenser"""

    try:
        ddb = boto3.resource("dynamodb")
        log_entry = f"IoT: Initial shadow set for dispenser {dispenser_id}"
        ts = datetime.utcnow().isoformat() + "Z"

        # Create default DispenserStatus document
        dispenser_table = ddb.Table(os.environ["DISPENSER_TABLE"])
        item = {
            "dispenserId": dispenser_id,
            "credits": Decimal(str(1.00)),
            "leaderBoardStatus": Decimal(str(1)),
            "leaderBoardTime": Decimal(int(time.time())),
            "requests": [],
        }
        dispenser_table.put_item(Item=item)

        event_table = ddb.Table(os.environ["EVENT_TABLE"])
        item = {"dispenserId": dispenser_id, "timestamp": ts, "log": log_entry}
        event_table.put_item(Item=item)
        return True
    except ClientError as e:
        logger.error(f"ERROR: Could not update database tables, error: {e}")
        return False


def cloud9_instance(owner_arn, instance_type):
    """Create a Cloud 9 instance for the user in the default VPC"""

    asset = {"cloud9": {}}
    client = boto3.client("cloud9")
    username = owner_arn.split("/")[-1]

    # A new IAM user is not immediately available. Loop for up to 60 seconds before hard failing
    start_time = time.time()
    while (time.time() - start_time) < 60:
        try:
            response = client.create_environment_ec2(
                name=username,
                description=f"{username} Cloud9 environment",
                instanceType=instance_type,
                automaticStopTimeMinutes=60,
                ownerArn=owner_arn,
            )
            asset["cloud9"]["environmentId"] = response["environmentId"]
            logger.info(
                f"It took {time.time() - start_time} seconds to create the Cloud9 environment"
            )
            return asset
        except ClientError as e:
            # Log to collect statistics on average creation time
            logger.warning(
                f"Error creating Cloud9 environment (will retry), error: {e}"
            )
            time.sleep(1)
            continue
    # The Cloud9 instance was not created, log major error
    logger.error(f"Error creating Cloud 9 environment within 60 seconds")
    return asset
