"""
Example template for Lambda custom resource. Copy this file and cfnresource.py to a new
directory relative to the main cdk-app and modify.
 
NOTE: This code is not called from the construct. You can copy this and the
      cfnresource.py file to a new directory and modify. Please ensure physical_id
      is unique for all create lambdas.
"""

def main(event, context):
    import logging as log
    import cfnresponse

    log.getLogger().setLevel(log.INFO)

    # This needs to change if there are to be multiple resources
    # in the same stack -- test
    physical_id = "TheOnlyCustomResource"

    try:
        log.info("Input event: %s", event)

        # Check if this is a Create and we're failing Creates
        if event["RequestType"] == "Create" and event["ResourceProperties"].get(
            "FailCreate", False
        ):
            raise RuntimeError("Create failure requested")
        elif event["RequestType"] == "Create":
            # Operations to perform during Create, then return attributes
            attributes = {"Response": "Create performed"}
        elif event["RequestType"] == "Update":
            # Operations to perform during Update, then return attributes
            attributes = {"Response": "Update performed"}
        else:
            # Operations to perform during Delete, then return attributes
            attributes = {"Response": "Delete performed"}
        cfnresponse.send(event, context, cfnresponse.SUCCESS, attributes, physical_id)

    except Exception as e:
        log.exception(e)
        # cfnresponse's error message is always "see CloudWatch"
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
