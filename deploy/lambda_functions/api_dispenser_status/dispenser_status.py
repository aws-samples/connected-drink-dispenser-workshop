"""Queries and returns dispenser status from DynamoDB"""

import json
import os
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal


__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global Variables
httpHeaders = {"Access-Control-Allow-Origin": "*"}
ddb = boto3.resource("dynamodb")
dispenser_table = ddb.Table(os.environ["DISPENSER_TABLE"])
iot_client = boto3.client("iot")
iot_data_client = boto3.client("iot-data")


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, decimal.Decimal):  # pylint: disable=E0602
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def http_response(headers, status_code, body):
    """Create response dict for returning query"""
    if type(body) != str:
        if type(body) == dict:
            body = json.dumps(body)
        else:
            body = "ERROR, invalid type of {} for body of return".format(type(body))
            status_code = 500
    return {"body": body, "headers": headers, "statusCode": status_code}


def get_credits(dispenser):
    """Return current credit count"""
    response = dispenser_table.query(
        KeyConditionExpression=Key("dispenserId").eq(dispenser)
    )

    if response["Count"] == 0:
        return http_response(
            httpHeaders, 200, f"ERROR: Dispenser {dispenser} does not exist"
        )
    else:
        credits = float(response["Items"][0]["credits"])
        return credits


def get_led_status(shadow):
    """Return current reported state for attribute led"""

    # Default state if attribute not found in reported state
    led_state = "off"
    if "reported" in shadow["state"]:
        if "led" in shadow["state"]["reported"]:
            led_state = shadow["state"]["reported"]["led"]
    return led_state


def get_led_ring_status(shadow):
    """Return current reported state for ring led"""

    # Default values if led_ring not in reported state
    count = 0
    color = "#FFFFFF"
    if "reported" in shadow["state"]:
        if "led_ring" in shadow["state"]["reported"]:
            if "count" in shadow["state"]["reported"]["led_ring"]:
                count = int(shadow["state"]["reported"]["led_ring"]["count"])
            if "color" in shadow["state"]["reported"]["led_ring"]:
                color = str(shadow["state"]["reported"]["led_ring"]["color"])
    return {"count": count, "color": color}


def handler(event, context):
    """This function does not process any parameters, but returns complete
     details of the dispenser"""
    logger.info("Received event: {}".format(json.dumps(event)))

    dispenser_id = event["requestContext"]["authorizer"]["claims"]["custom:dispenserId"]
    shadow = json.loads(
        iot_data_client.get_thing_shadow(thingName=str(dispenser_id))["payload"]
        .read()
        .decode("utf-8")
    )
    body = json.dumps(
        {
            "credits": get_credits(dispenser_id),
            "led_state": get_led_status(shadow),
            "led_ring_state": get_led_ring_status(shadow),
        }
    )

    return http_response(httpHeaders, 200, body)
