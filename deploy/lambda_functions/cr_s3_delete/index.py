"""
CloudFormation custom resource to delete all objects in S3 bucket defined in
the BUCKET_NAME environment variable. To use, ensure there is a "DependsOn" to
the referenced bucket on the custom resource.
"""
def main(event, context):
    import os
    import logging as log
    import boto3
    import cfnresponse

    log.getLogger().setLevel(log.INFO)

    # This needs to change if there are to be multiple resources
    # in the same stack -- test
    physical_id = "S3DeleteAllFiles"

    try:
        log.info("Input event: %s", event)
        log.info("Environment variables: %s", os.environ)

        # Check if this is a Create and we're failing Creates
        if event["RequestType"] == "Create" and event["ResourceProperties"].get(
            "FailCreate", False
        ):
            raise RuntimeError("Create failure requested")
        elif event["RequestType"] == "Create":
            # Operations to perform during Create, then return attributes
            attributes = {"Response": "S3DeleteAllFiles CREATE performed, no actions taken"}
        elif event["RequestType"] == "Update":
            # Operations to perform during Update, then return attributes
            attributes = {"Response": "S3DeleteAllFiles UPDATE performed, no actions taken"}
        else:
            # Operations to perform during Delete, then return attributes
            s3 = boto3.resource("s3")
            bucket = s3.Bucket(os.environ["BUCKET_NAME"])
            bucket.objects.all().delete()
            attributes = {"Response": "S3DeleteAllFiles DELETE performed, all S3 objects in referenced bucket deleted"}
        cfnresponse.send(event, context, cfnresponse.SUCCESS, attributes, physical_id)

    except Exception as e:
        log.exception(e)
        # cfnresponse's error message is always "see CloudWatch"
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
