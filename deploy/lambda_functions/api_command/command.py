"""
    Issue commands from application to interact with dispenser as an API call
"""

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

import boto3
from botocore.exceptions import ClientError
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global Variables
http_headers = {"Access-Control-Allow-Origin": "*"}
valid_commands = ["setLed"]

iot_data_client = boto3.client("iot-data")


def http_response(headers, status_code, body):
    """Create response dict for returning query"""
    if type(body) != str:
        if type(body) == dict:
            body = json.dumps(body)
        else:
            body = "ERROR, invalid type of {} for body of return".format(type(body))
            status_code = 500
    return {"body": body, "headers": headers, "statusCode": status_code}


def set_led(thing, state):
    """Toggle or force on/off the led"""

    # Read state value and set new state
    if state == "toggle":
        response = iot_data_client.get_thing_shadow(thingName=thing)
        shadow = json.loads(response["payload"].read().decode("utf-8"))
        led_current_state = "off"
        if "reported" in shadow["state"]:
            if "led" in shadow["state"]["reported"]:
                led_current_state = shadow["state"]["reported"]["led"]
        if led_current_state == "off":
            led_new_state = "on"
        else:
            led_new_state = "off"
    elif (state == "on") or (state == "off"):
        led_new_state = state
    else:
        return http_response(
            http_headers,
            500,
            'Command "setLed" must be set to "on", "off", or "toggle"',
        )

    shadow_payload = {"state": {"desired": {"led": led_new_state}}}
    response = iot_data_client.update_thing_shadow(
        thingName=thing, payload=json.dumps(shadow_payload)
    )
    return http_response(
        http_headers,
        200,
        f"Led state state {led_new_state} successfully put into shadow",
    )


def handler(event, context):
    """Process entry point for lambda."""
    logger.info(f"Received event: {json.dumps(event)}")
    if "queryStringParameters" in event:
        params = event["queryStringParameters"]
    else:
        return http_response(http_headers, 500, "No parameters provided")

    # thing/dispenser
    dispenser = str(event["requestContext"]["authorizer"]["claims"]["custom:dispenserId"])
    try:
        # Verify command provided and execute
        if "setLed" in params:
            # value is off, on, or toggle
            response = set_led(dispenser, params["setLed"])
        else:
            response = http_response(
                http_headers,
                500,
                f"Invalid command provided, valid commands are: {valid_commands}",
            )
        # options process (missing, good or bad 200/500)
        return response
    except KeyError as e:
        logger.error("Error: %s", e)
        return http_response(http_headers, 500, e)
