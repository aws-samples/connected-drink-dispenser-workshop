import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal
import json
import os
import logging

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global Variables
httpHeaders = {"Access-Control-Allow-Origin": "*"}

ddb = boto3.resource("dynamodb")
iot_client = boto3.client("iot-data")

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
            body = f"ERROR, invalid type of {type(body)} for body of return"
            status_code = 500
    return {"body": body, "headers": headers, "statusCode": status_code}


def set_led_ring(amount: float):
    """Return count and color based on credit float amount

    the ring LED has 8 elements and are set based on credit amounts:

    credits         LEDs lit            Color
    =============== =================== ===========================
    0 - 0.24        8                    red (#FF0000)
    0.25 - 0.49     2                    white (#F0F0F0)
    0.50 - 0.74     4                    white (#F0F0F0)
    0.75 - 0.99     6                    white (#F0F0F0)
    1.00 - 1.99     1                    darkest green (#006600)
    2.00 - 2.99     2                    dark green (#009900)
    3.00 - 3.99     3                    green (#00E600)
    4.00 - 4.99     4                    bright green(#00FF00)
    5.00 - 5.99     5                    bright green(#00FF00)
    6.00 - 6.99     6                    bright green(#00FF00)
    7.00 - 7.99     7                    bright green(#00FF00)
    8.00 >          8                    bright green(#00FF00)
    """

    # Green colors for 1, 2, 3, and greater
    color_scale = ["#006600", "#009900", "#00E600", "#00FF00"]
    # Cast to float, most likely Decimal coming in
    amount = float(amount)
    if amount == 0.0:
        # No credits all lit up red
        count = 8
        color = "#FF0000"
    elif amount < 1.00:
        # 0.01 - 0.99 - 2 per .25, white
        count = int(amount / 0.25) * 2
        color = "#F0F0F0"
    else:
        # At least 1.00 or more, set count to 1-8 per 1.00
        count = int(amount / 1.00) if amount < 8.00 else 8
        if count < 4:
            color = color_scale[count - 1]
        else:
            color = color_scale[3]
    return count, color


def credit_dispenser(dispenser, crediting_dispenser):
    """Credit target dispenser with $0.25"""
    dispenser = str(dispenser)
    dispenser_table = ddb.Table(os.environ["DISPENSER_TABLE"])

    # Query dispenser
    response = dispenser_table.query(
        KeyConditionExpression=Key("dispenserId").eq(dispenser)
    )

    # If count is zero, this is a non-existent dispenser
    if response["Count"] == 0:
        return http_response(
            httpHeaders,
            200,
            f"ERROR: Credit not issued, dispenser {dispenser} does not exist",
        )
    else:
        user_db_record = response["Items"][0]

    # We have a valid dispenser, add $0.25 to it and put updated record
    user_db_record["credits"] = user_db_record["credits"] + Decimal(0.25)
    dispenser_table.put_item(Item=user_db_record)

    # Update led_ring desired state
    # For less than $1.00, count 1 to 3, greater than $1.00, count = 5
    count, color = set_led_ring(user_db_record["credits"])
    desired_state = {
        "state": {"desired": {"led_ring": {"count": count, "color": color}}}
    }
    iot_client.update_thing_shadow(
        thingName=dispenser, payload=json.dumps(desired_state)
    )

    # Publish IoT event to receiving dispenser
    publish_event(
        topic=f"events/{dispenser}",
        payload=f"Received $0.25 credit from dispenser: {crediting_dispenser}",
    )
    return http_response(httpHeaders, 200, f"Dispenser: {dispenser} credited $0.25")


def publish_event(topic, payload):
    """Publish payload to IoT topic as JSON attribute message"""
    iot_client.publish(topic=topic, qos=0, payload=f'{{"message": "{payload}"}}')


def handler(event, context):
    """Credit dispenser as long as calling entity is not the same"""
    logger.info("Received event: %s", json.dumps(event))

    if ("queryStringParameters") in event and (
        event["queryStringParameters"] is not None
    ):
        params = event["queryStringParameters"]
    else:
        response = http_response(httpHeaders, 500, "No parameters provided")
        return response

    try:
        # Id of dispenser (app) that invoked the Lambda
        crediting_dispenser = str(
            event["requestContext"]["authorizer"]["claims"]["custom:dispenserId"]
        )
        if "dispenserId" in params:
            if params["dispenserId"] != crediting_dispenser:
                return credit_dispenser(
                    dispenser=params["dispenserId"],
                    crediting_dispenser=crediting_dispenser,
                )
            else:
                return http_response(
                    httpHeaders,
                    500,
                    "Cannot give credit to your dispenser - cheating!!!!",
                )
        else:
            return http_response(
                httpHeaders, 500, 'Parameter "dispenserId" must be present'
            )
    except KeyError as e:
        logger.error("Error: %s", e)
        return http_response(httpHeaders, 500, e)
