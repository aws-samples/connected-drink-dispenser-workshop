import json
import boto3
import csv

s = boto3.Session(profile_name="sandbox-admin-gadams")
client = s.client('lambda')
ddb = s.resource('dynamodb')
table = ddb.Table('cdd-workshop-UserTable')


event_temp = {
    "requestContext": {
        "authorizer": {
            "claims": {
                "cognito:username": None,
                "custom:dispenserId": None
            }
        }
    },
    "body": f"{{\"cognitoIdentityId\":\"us-west-2:0edbee18-0775-beef-0100-8a9b4ee0973f\"}}"
}

with open('bulk_user_test.csv', newline='') as csvfile:
    users = csv.DictReader(csvfile)
    for row in users:
        print(row["cognito:username"])

        # create/modify DDB entry
        response = table.put_item(
            Item={
                "userName": row["cognito:username"],
                "dispenserId": row["custom:dispenserId"],
                "assets": None
            }
        )


        event = event_temp
        event["requestContext"]["authorizer"]["claims"]["cognito:username"] = row["cognito:username"]
        event["requestContext"]["authorizer"]["claims"]["custom:dispenserId"] = row["custom:dispenserId"]
        event["body"] = f"{{\"cognitoIdentityId\":\"us-west-2:0edbee18-0775-beef-0{row['custom:dispenserId']}-8a9b4ee0973f\"}}"

        print(event)

        client.invoke(
            FunctionName="cdd-workshop-ApiGetResourcesFunction",
            InvocationType="Event",
            Payload=json.dumps(event)
        )

