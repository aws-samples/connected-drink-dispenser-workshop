---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: <i class="fas fa-greater-than"></i>&nbsp;
next: 
prev: 
title: Deploy Stack
weight: 20
---

This section covers the steps to locally build and then deploy the stack to your preferred region. All steps are completed within the `deploy/` directory.

## Modify Template Files

Copy the `deploy/config.json.default` to `deploy/config.json` and modify the new file and change the following parameters with the values from the prerequisites section:

* `Region` - AWS region to deploy and run the stack (for example, `us-west-2` from previous section).
* `HostName` - Fully qualified domain name for the stack to build and use, must not exist, it will be created.
* `ProfileName` - The name of the AWS CLI profile with administrative permissions.

## Process Local Dependencies

There are various python packages that need to be installed within the `deploy/.env` directory in order for CDK to run and process the stack. Follow these steps *once* to install the dependencies.

Change to the `deploy/` directory and activate the Python virtual environment.

```bash
$ cd Connected_drink_dispenser/cdk
$ source .env/bin/activate     # sh or bash
$ pip install -r requirements.txt
```

Verify by running `cdk synth` which will return a *long* CloudFormation stack in YAML. As long as no errors were returned, the `cdk synth` command has verified dependencies and created the artifacts in the `cdk.out/` subdirectory (don't delete this directory).

## Deploy Stack via CDK and CloudFormation

With the prerequisites and `config.json` set, run `cdk deploy`. This will take at least 30 minutes if not longer as there is a CloudFront (CDN) distribution involved. The final output should look like this:

```bash

 ✅  cdd-workshop

Outputs:
cdd-workshop.StaticSiteBucket34E5D9AF = cdd.example.com-static-site
cdd-workshop.APIEndpoint = https://xxxxxxx.execute-api.us-west-2.amazonaws.com/prod/
cdd-workshop.CognitoIdentityPool = us-west-2:38c0c443-xxx-xxxx-xxxx-692ebe311dfe
cdd-workshop.UserPoolCognitoUserPoolIdArn107A6E54 = arn:aws:cognito-idp:us-west-2:123456789012:userpool/us-west-2_foo
cdd-workshop.StaticSiteDistributionId8C64EF2A = E1MK8XXXX2S9X
cdd-workshop.APIEndpoint1793E782 = https://xxxxxxx.execute-api.us-west-2.amazonaws.com/prod/
cdd-workshop.UserPoolCognitoClientId49B6D8C4 = 4hp8jitmd6virxxxxxo68p6
cdd-workshop.UserPoolCognitoUserPoolIdA08E3514 = us-west-2_foo

Stack ARN:
arn:aws:cloudformation:us-west-2:123456789012:stack/cdd-workshop/deadbeef-d008-11e9-8962-02dbab669d48
$
```

When completed, you should be able to navigate to https://cdd.example.com to verify that CloudFront is working. There will be a *NoSuchKey* error, which we will fix in the next step, but you can verify that the HTTPS certificate is in place.

If there are any errors running `cdk deploy`, the stack will automatically rollback and delete all the resources. Due to the CloudFront distribution, this will take 30 minutes or longer to complete. Review the error, correct, and re-run the deploy step. Most errors will either be related to permissions associated with the credentials used to deploy, or lack of one of the prerequisites.

## Deploy Application and Documentation

With the stack deployed, we need to read some of the outputs from above, create the single page application, and then deploy it and this documentation. To do so, run the `deploy_app.py` script.

```bash
$ python deploy_app.py
Verifying local configuration files
Reading CloudFormation stack parameters to create files for web application
Clearing S3 bucket of ALL objects
Copying web application to S3 |################################| xxx/xxx⏎
Copying online documentation to S3 |################################| 121/121⏎
```




