#!/usr/bin/env python3

import sys
import os
import json
import shutil
import re
from pathlib import Path
from string import ascii_lowercase, digits

import boto3
from botocore.exceptions import ClientError
from aws_cdk import core
from cdd.base_services import CddBase

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"


def read_config():
    configfile = Path("config.json")
    if configfile.is_file():
        with open(configfile) as f:
            config = f.read()
    else:
        # If default file exists, copy to config. json
        configdef = Path("config.json.default")
        if configdef.is_file():
            shutil.copyfile(configdef, "config.json")
            print(
                "config.json did not exist, created. Please modify config.json and re-run CDK"
            )
        else:
            print("File config.json not found, must in same directory with cdk_app.py")
        sys.exit(1)
    try:
        config = json.loads(config)
    except ValueError as e:
        print(f"Invalid format of {configfile}, error: {e}")
        sys.exit(1)
    return config


def verify_domain(host_name, session):
    """Verify domain name exists and is public"""
    c = session.client("route53")
    host_name = ".".join(host_name.split(".")[-2:]) + "."
    r = c.list_hosted_zones_by_name(DNSName=host_name)
    for i in r["HostedZones"]:
        if i["Name"] == host_name and i["Config"]["PrivateZone"] == False:
            zone_id = i["Id"].split("/")[-1]
            return zone_id
    print(f"Error: Public zone for domain {host_name[:-1]} not found")
    exit(1)


def verify_certificate(host_name, session):
    """
    Verify a certificate covers the domain name
    NOTE: The region is hard-coded to us-east-1 as this is where CloudFront
          required server certificates to reside
    """
    cert_arn = False
    c = session.client("acm", region_name="us-east-1")
    paginator = c.get_paginator("list_certificates")
    page_iterator = paginator.paginate(CertificateStatuses=["ISSUED"])
    for page in page_iterator:
        for cert in page["CertificateSummaryList"]:
            cert_cn = cert["DomainName"]
            rxString = (
                r"(?:^|\s)(\w+\.)?" + cert_cn.replace(".", r"\.")[3:] + r"(?:$|\s)"
            )
            regex = re.compile(rxString)
            if regex.match(host_name):
                return cert["CertificateArn"]
            else:
                continue
    if not cert_arn:
        print(
            f"Error: No certificates have common name that matches {host_name}, please review:"
        )
        print(
            "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html for more details"
        )
        sys.exit(1)


if __name__ == "__main__":
    # Read config file
    config = read_config()
    try:
        session = boto3.Session(profile_name=config["ProfileName"])
    except ClientError as e:
        print(f"ProfileName {config['ProfileName']} not found, error: {e}")
        sys.exit(1)

    # Process and validate user parameters
    required_params = (
        "HostName",
        "ProfileName",
        "Region",
        "AdminUserName",
        "AdminPassword",
        "Cloud9InstanceSize",
        "ParticipantLimit",
    )
    if not all(param in config for param in required_params):
        print(
            f"All required parameters not found in config.json: {required_params} must be provided"
        )
        sys.exit(1)
    # Hosted Zone Id for Domain name
    zone_id = verify_domain(config["HostName"], session)
    # Verify AWS Certificate Manager has valid certificate for the domain name entry
    cert_arn = verify_certificate(config["HostName"], session)
    # Verify admin user and password values are not NULL
    if config["AdminUserName"] == "" or config["AdminPassword"] == "":
        print(f"Both AdminUserName and AdminPassword must have values set")
        sys.exit(1)
    # Validate password complexity of a minimum of 6 characters, lower case, and numeric
    # are included
    password = config["AdminPassword"]
    if not (
        len(password) >= 6
        and any(c.islower() for c in password)
        and any(c.isdigit() for c in password)
    ):
        print(
            f"AdminPassword value must be at least 6 or more characters and contain both lower case and numeric characters"
        )
        sys.exit(1)

    # Create app and resources
    app = core.App()
    base = CddBase(
        app,
        "cdd-workshop",
        host_name=config["HostName"],
        zone_id=zone_id,
        cert_arn=cert_arn,
        admin_user=config["AdminUserName"],
        admin_password=config["AdminPassword"],
        cloud9_instance_size=config["Cloud9InstanceSize"],
        participant_limit=config["ParticipantLimit"],
    )

    app.synth()
