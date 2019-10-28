"""
    Lambda invoked by IoT Rules Engine to process logging events
    and store in DynamoDB table. Different logic used based on source
    of event (shadow topic or event/dispenserId topic)
    Standalone, not API Gateway

    Environment Variables:
      EVENT_TABLE - DDB table to post events
"""

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime as dt
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

# Global variables for function access and Lambda reuse
ddb = boto3.resource("dynamodb")
event_db = ddb.Table(os.environ["EVENT_TABLE"])


def thing_name(topic):
    """Get thing name from provided shadow topic"""
    return topic.split("/")[2]


def compare_shadow(current, previous, path="", section=""):
    """Compare current shadow to previous shadow documents for
    desired and reported states"""

    err = ""
    key_add = ""
    key_change = ""
    old_path = path
    for k in current.keys():
        if k == "desired" or k == "reported":
            section = k
        else:
            # Set path only after desired or reported
            path = old_path + "[%s]" % k
        if not k in previous:
            key_add += f'Attribute {path} = {current[k]} added to "{section} state"\n'
        else:
            if isinstance(current[k], dict) and isinstance(previous[k], dict):
                err += compare_shadow(current[k], previous[k], path, section)
            else:
                if current[k] != previous[k]:
                    key_change += f'Attribute {path} in "{section} state" changed from "{previous[k]}" to "{current[k]}"'

    for k in previous.keys():
        path = old_path + "[%s]" % k
        if not k in current:
            key_add += f'Attribute {path} removed from "{section} state"\n'

    return "Shadow: " + key_add + key_change + err


def process_shadow(event):
    """Create log entry on changes seen between current and previous shadow states"""

    log_entry = {
        "dispenserId": event["topic"].split("/")[2],
        "timestamp": dt.utcnow().isoformat() + "Z",
        "log": compare_shadow(event["current"]["state"], event["previous"]["state"]),
    }
    return log_entry


def process_generic_event(event):
    """Create log entry from "event" topic"""

    if "dispenserId" in event:
        dispenser_id = event["dispenserId"]
        if "message" in event:
            # Use the text of this field only
            message = f'MQTT: {event["message"]}'
        else:
            # Display all other non-used fields
            message = "MQTT: " +  str({key: event[key] for key in event if key not in ["topic", "ts", "dispenserId"]})
    else:
        dispenser_id = "000"
        message = f"ERROR: Message received without 'dispenserId' set, message was: {event}"

    log_entry = {
        "dispenserId": dispenser_id,
        "timestamp": dt.utcnow().isoformat() + "Z",
        "log": message,
    }
    return log_entry


def process_dispenser_event(event):
    """Create log entry from "event/dispenserId" topic"""

    dispenser_id = event["topic"].split("/")[1]
    if "message" in event:
        # Use the text of this field only
        message = f'MQTT: {event["message"]}'
    else:
        message = "MQTT: " +  str({key: event[key] for key in event if key not in ["topic", "ts", "dispenserId"]})
    log_entry = {
        "dispenserId": dispenser_id,
        "timestamp": dt.utcnow().isoformat() + "Z",
        "log": message,
    }
    return log_entry



def publish_event(entry, table):
    """Put log entry into DynamoDB table"""

    try:
        # Write to events table
        table.put_item(Item=entry)
    except ClientError as e:
        logging.error("An error has occurred:, {}".format(e))


def handler(event, context):
    """Process properly formed JSON messages from AWS IoT topics"""
    logger.info("Received event: %s", json.dumps(event))

    # Determine source of event by topic and process
    if "topic" not in event:
        logger.error("Attribute 'topic' not found in event: %s", json.dumps(event))
        return
    # $aws/things/+/shadow/update/documents
    if event["topic"].startswith("$aws/things/"):
        # Shadow document
        log_entry = process_shadow(event)
    elif event["topic"].startswith("events/"):
        # Per dispenser topic (e.g., "events/123")
        log_entry = process_dispenser_event(event)
    elif event["topic"] == "events":
        # Generic event
        log_entry = process_generic_event(event)
    else:
        # Should not get here - log anyway
        log_entry = {
            "dispenserId": "000",
            "timestamp": dt.utcnow().isoformat() + "Z",
            "log": f"ERROR: received event on unknown topic, original event is {event}",
        }
    publish_event(log_entry, event_db)

    return
