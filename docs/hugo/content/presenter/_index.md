---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: <i class="fas fa-chalkboard-teacher"></i>&nbsp;
next:
prev:
title: Setting Up the Workshop
weight: 20
---

## Welcome Presenter!

This section will walk you through setting up the _Connected Drink Dispenser_ workshop for participants. It covers the workshop setup, how procure and build hardware, and the approach to introduce the workshop and mentor the participants attending the workshop.

{{% notice warning %}}
Deploying the workshop opens your account to anyone registering for an account from the single-page app. Each participant (user) is provisioned with a Cloud9 instance that allows them to run processes and access the Internet. Only deploy the workshop over a period of time (hours, not days) where you can monitor activity in your account, and destroy the workshop once completed to secure resources.
{{% /notice %}}

Each section covers details for understanding, setting up, and presenting the workshop. Follow each of these sections in order to fully build the workshop.

1. Prerequisites to host the workshop for one or multiple runs.
1. Building and deploying the workshop cloud assets.
1. Procuring drink dispenser hardware.
1. Presentation tips and FAQ for supporting participant.
1. Layout of the repository.

### Quick-start Using Cloud9

Follow these steps to deploy from a Cloud9 instance in the account where you wish to run the workshop:

1. Ensure a Route 53 hosted public zone is [setup](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring.html) for a private domain name you have registered. The domain `example.com` is used below.
1. Launch a Cloud9 IDE from an account with all the IAM permissions needed to deploy the Cloud Development Kit (CDK) stack, _from the region where you want to deploy the workshop_. As there are a _lot_ of IAM related permissions needed, the AWS managed permissions group, _AdministratorAccess_, has the necessary permissions.
1. Before installing dependencies, extend the EBS volume to 20GiB in size. Recent changes to installed tools will fully consume the 10GiB initially allocated.
1. Open a new terminal, install dependencies, clone this repository, and create the `connected-drink-dispenser-workshop/deploy/config.json` file from the template.

   ```bash
   ### Copy and paste these lines into terminal
   cd ~/environment/
   npm install -g cdk
   npm install -g yarn
   git clone https://github.com/aws-samples/connected-drink-dispenser-workshop.git
   cd connected-drink-dispenser-workshop/deploy/
   sudo pip-3.6 install -r requirements.txt
   cp config.json.default config.json
   ### end of copy/paste
   ```

1. Update the `config.json` file's values and save the file when complete:

   - **ProfileName** - Change to `default` (this uses the permissions from our user account in Cloud9)
   - **AdminPassword** - Enter the value for the dispenser app admin user, must include _lower case_, _upper case_, and a _number_
   - **Region** - Set to the region you want the workshop to be deployed (should be the same as where Cloud9 was launched)
   - **Hostname** - Enter the fully qualified domain name to use for workshop for the Route 53 hosted zone (e.g., `cdd.example.com`)

1. From the terminal, bootstrap the CDK into the region (optional if you are already using CDK in that region) with the command `cdk bootstrap`:

   ```bash
   cdk bootstrap
       Bootstrapping environment aws://ACCOUNT/REGION...
   CDKToolkit: creating CloudFormation changeset...
   0/2 | 3:21:24 PM | CREATE_IN_PROGRESS   | AWS::S3::Bucket | StagingBucket
   0/2 | 3:21:25 PM | CREATE_IN_PROGRESS   | AWS::S3::Bucket | StagingBucket Resource creation Initiated
   1/2 | 3:21:47 PM | CREATE_COMPLETE      | AWS::S3::Bucket | StagingBucket
   2/2 | 3:21:49 PM | CREATE_COMPLETE      | AWS::CloudFormation::Stack | CDKToolkit
       Environment aws://ACCOUNT/REGION bootstrapped.
   ```

1. Deploy the workshop with the command `cdk deploy`. This will create a lot of updates as the stack progresses and will take 30-50 minutes to complete due to the CloudFront deployment:

   ```bash
   $ cdk deploy
   ... LIST OF RESOURCES ...
   Do you wish to deploy these changes (y/n)? y
   cdd-workshop: deploying...
   Updated: asset.d58800906a30c9e60c2dc7e40199f78f18842fa61a81094dd212ef1d9c4607a7 (zip)
   ... BUILD STEPS ...
   cdd-workshop.StaticSiteDistributionId8C64EF2A = E5J4ADZ0ZK1C5
   cdd-workshop.UserPoolCognitoClientId49B6D8C4 = 2b38h8da7dds832qvio3vkds5b
   cdd-workshop.UserPoolCognitoUserPoolIdA08E3514 = us-west-2_bnzrtUys3

   Stack ARN:
   arn:aws:cloudformation:us-west-2:904880203774:stack/cdd-workshop/832c88d0-1b7c-11ea-b1f9-02b80ff4b548
   $
   ```

   If you see errors or _CREATE_FAILED_ messages, review the reasons, which most likely will be permissions related. At this point the CDK will attempt to rollback and delete the deployment of resources. You may need to go into CloudFormation and delete the stack manually or issue the command `cdk destroy`. To resolve permissions errors, add the needed permissions to your account, and then close the Cloud9 IDE web page and relaunch from the console to refresh permissions.

   With expanded permissions, attempt again to deploy the stack until the success message above is seen.

1. Finally, issue the command `python deploy_app` to build the single page application, and upload all resources to the S3 origin bucket:

   ```bash
   $ python deploy_app.py
   ... BUILD AND UPLOAD STEPS
   DONE  Build complete. The dist directory is ready to be deployed.
   INFO  Check out deployment instructions at https://cli.vuejs.org/guide/deployment.html

   Done in 65.14s.
   Copying Single page web application to S3: 36 files [00:05,  6.22 files/s]
   Copying Credential C formatter page to S3: 6 files [00:00, 79.67 files/s]
   Copying Online documentation to S3: 446 files [00:13, 33.56 files/s]
   ```

At this point, the stack if fully deployed and ready to start! Once the workshop is over, either delete via CloudFormation or from the same Cloud9 IDE, issue the command `cdk destroy` from the `deploy` directory.
