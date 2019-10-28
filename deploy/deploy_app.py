"""
    This script is run after the 'cdk deploy' has successfully completed. It
    will generate stack-specific files from the deployment, and then upload
    the single page application and documentation.
"""

import sys
import os
import json
import mimetypes
import shutil
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm


def spa_exports(
    cognito_id_pool: str,
    cognito_region: str,
    user_pool_id: str,
    user_pool_web_client_id: str,
    api_endpoint: str,
    iot_endpoint: str,
):
    """Create config file for inclusion into webpacked file"""
    return (
        "const awsmobile = {\n"
        f"    'aws_iot_endpoint': '{iot_endpoint}',\n"
        f"    'aws_cognito_identity_pool_id': '{cognito_id_pool}',\n"
        f"    'aws_cognito_region': '{cognito_region}',\n"
        f"    'aws_sign_in_enabled': 'enable',\n"
        f"    'aws_user_pools_id': '{user_pool_id}',\n"
        f"    'aws_user_pools_web_client_id': '{user_pool_web_client_id}',\n"
        f"     'cdd_api_endpoint': '{api_endpoint}',\n"
        f"    'aws_cloud_logic_custom': [\n"
        "        {\n"
        f"            'name': 'CDD_API',\n"
        f"            'endpoint': '{api_endpoint}',\n"
        f"            'region': '{cognito_region}'\n"
        "        }\n"
        "    ]\n"
        "}\n\n"
        "export default awsmobile;\n"
    )


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
                "config.json did not exist, created. Please modify config.json, complete the 'cdk deploy', then rerun this script"
            )
        else:
            print(
                "File config.json not found, must in same directory with deploy_app.py"
            )
        sys.exit(1)
    try:
        config = json.loads(config)
    except ValueError as e:
        print(f"Invalid format of {configfile}, error: {e}")
        sys.exit(1)
    return config


def read_manifest():
    """Read the manifest file to get the stackname

        As of cdk 1.13.1, the stackname can be found in the manifest file
        as an artifact object with a type of aws:cloudformation:stack
    
    """
    manifest_file = Path("cdk.out/manifest.json")
    if manifest_file.is_file():
        with open(manifest_file) as f:
            manifest = f.read()
    else:
        print("manifest.json not found in cdk.out directory.")
        sys.exit(1)

    try:
        manifest = json.loads(manifest)
    except ValueError as e:
        print(f"Invalid format of {manifest_file}, error: {e}")
        sys.exit(1)
    # Only return the first artifact
    for i in manifest["artifacts"]:
        if manifest["artifacts"][i]["type"] == "aws:cloudformation:stack":
            return i


def get_output(outputs, k):
    """Return output value for exported name"""
    for i in outputs:
        if "ExportName" in i:
            if i["ExportName"] == k:
                return i["OutputValue"]
    return "NotFound"


def s3_copy(s3_resource, bucket, local_directory, s3_key, message):
    """Copy all files starting from 'directory' to boto3 s3 resource appended after s3_key"""

    total_files = len(list(Path(local_directory).glob("**/*")))  # approx
    base_dir_len = len(Path(local_directory).parts)
    bar = tqdm(total=total_files, desc=f"Copying {message} to S3", unit=" files")
    for filename in Path(local_directory).glob("**/*"):
        parts = filename.parts[base_dir_len:]
        if filename.is_dir():
            # Don't process directories, only files
            bar.update()
            continue
        content_type = mimetypes.guess_type(str(filename))[0]
        if content_type is None:
            if parts[-1].split(".")[-1] == "map":
                # mimetypes skips on .map files, set content type manually
                content_type = "application/json"
        if content_type is not None:
            if s3_key:
                destination = Path(s3_key, os.path.join(*parts))
            else:
                destination = Path(os.path.join(*parts))
            s3_resource.meta.client.upload_file(
                str(filename),
                bucket,
                str(destination),
                ExtraArgs={"ContentType": content_type},
            )
        bar.update()
    bar.update(total_files)


def spa_deploy(s3, s3_bucket):
    """Compile (webpack) and sync files to S3"""

    try:
        # Error out if dependencies are not in place
        prev_cwd = Path.cwd()
        os.chdir(Path("../dispenser_app"))
        # cwd ../dispenser_app
        # clear local node_modules and dist directories
        # build app
        shutil.rmtree(Path("dist/"), ignore_errors=True)
        shutil.rmtree(Path("node_modules/"), ignore_errors=True)
        os.system("yarn install")
        os.system("yarn build")
        # sync to s3
        s3_copy(s3, s3_bucket, Path("dist"), "", "single page application")

    except Exception as e:
        print(f"Application build error (exiting): {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Read config file
    print("Verifying local configuration files")
    config = read_config()
    stackname = read_manifest()
    try:
        session = boto3.Session(profile_name=config["ProfileName"])
    except ClientError as e:
        print(f"ProfileName {config['ProfileName']} not found, error: {e}")
        sys.exit(1)

    # Read stack specific outputs from CloudFormation stack
    print("Reading CloudFormation stack parameters to create files for web application")
    try:
        cfn_client = session.client("cloudformation")
        response = cfn_client.describe_stacks(StackName=stackname)
        outputs = response["Stacks"][0]["Outputs"]
        # Get IoT endpoint for account
        iot_client = session.client("iot")
        aws_iot_endpoint = iot_client.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]
        aws_cognito_identity_pool_id = get_output(outputs, "CognitoIdentityPoolId")
        aws_cognito_region = config["Region"]
        aws_user_pools_id = get_output(outputs, "CognitoUserPoolId")
        aws_user_pools_web_client_id = get_output(outputs, "CognitoClientId")
        aws_api_endpoint = get_output(outputs, "APIEndpoint")
        s3_bucket = f"{config['HostName']}-static-site"
    except Exception as e:
        print(f"Error reading CloudFormation stack variables, exiting")
        sys.exit(1)

    # Create env file for SPA
    with open(Path("../dispenser_app/src/aws-exports.js"), "w") as file:
        file.write(
            spa_exports(
                aws_cognito_identity_pool_id,
                aws_cognito_region,
                aws_user_pools_id,
                aws_user_pools_web_client_id,
                aws_api_endpoint,
                aws_iot_endpoint
            )
        )

    # Delete all S3 objects
    print("Clearing S3 bucket of ALL objects")
    try:
        s3 = session.resource("s3")
        bucket = s3.Bucket(s3_bucket)
        bucket.objects.all().delete()
    except ClientError as e:
        print(f"Error clearing out S3 bucket: {s3_bucket}, error: {e}")
        sys.exit(1)

    # build and copy SPA
    spa_deploy(s3, s3_bucket)

    # copy up docs
    s3_copy(s3, s3_bucket, Path("../docs/hugo/public"), "docs/", "online documentation")
