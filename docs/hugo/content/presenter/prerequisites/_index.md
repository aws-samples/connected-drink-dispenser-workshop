---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: <i class="fas fa-greater-than"></i>&nbsp;
next: 
prev: 
title: Prerequisites
weight: 10
---

We have strived to keep the amount of prerequisites to a minimum in order to setup the infrastructure for the workshop. Please ensure that all of these are completed before progressing to the next step.

* An AWS account to be used to host the workshop services and participant IAM user accounts. It is recommended to use or create a new or sandbox account as the participants will have permissions to see resources.
* Have a local Workstation or laptop available

    To build and run the CloudFormation steps, you will need a workstation, an EC2 instance, or a laptop. All the steps are written and based on Linux/macOS. If you don't have a similar environment, you may use an Amazon Linux based EC2 instance. No matter what you use, please ensure the following tools are installed:

  * AWS CLI with admin credentials (see below)
  * NodeJS >= 8.11.x and npm
  * Python >= 3.6 and pip
  * [AWS Cloud Development Kit (CDK)](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)

    The following commands will verify that the command line tools are properly installed:
    {{< highlight bash >}}
$ aws iam get-account-summary       # AWS CLI
{
    "SummaryMap": {
      ...
    }
}
$ node -v                          # NodeJS
v12.8.0
$ npm -v                           # Node package manager
6.10.2
$ python --version                 # Python
Python 3.7.4
$ pip --version                    # Python module manager
pip 19.2.2 from ...
$ cdk --version                    # CDK utility (from npm)
1.4.0 (build 175471f)
    {{< /highlight >}}


* [An AWS CLI named profile.](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) The profile in `~/.aws/config` should contain the target region, and the `~/.aws/credentials` file should have an access key and secret access key with administrative access (or minimum to deploy and run the stack). The profile name `cdk-user` will be used throughout this guide.
* A registered domain name managed by Route 53 in the workshop account. This can either be through registration in Route 53, or [making Amazon Route 53 the DNS service for the domain](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/MigratingDNS.html). If we want the URL for the workshop to be  `cdd.example.com`, in Route 53 there needs to be a public hosted zone for `example.com`.
* To target the appropriate account, region and other aspects, the following entries need to be considered and changed in the `config.json` file (the default value used in this guide listed first):
    * **Region** - `us-west-2`<br/>Region identifier, must support all AWS resources being used.
  * **HostName** - `cdd.example.com`<br/>The fully qualified domain name entry to be created from the Route 53 hosted zone details above (`example.com`). Note, subdomain entries can also be used such as `cdd.foo.example.com`, but must be created from Route 53. 
  * **ProfileName** - `cdk-user`<br />The AWS CLI profile name referenced above. It is used by the build and deploy steps to use the right account and credentials.
  * **AdminUserName** - `admin`<br/>The username to log into the web application for administrative purposes.
  * **AdminPassword** - `NO DEFAULT VALUE`<br/>This needs to be completed in the `config.json` file and is only used for web application related tasks, and *not* for AWS account activities.
  * **cloud9InstanceSize** - `t3.small`<br/>Instance size for each participants Cloud 9 environment. Select larger (or smaller) depending upon how long the Amazon FreeRTOS compilation should take.
  * **ParticipantLimit** - `20`<br/>The maximum amount of user accounts that can be created, after which, new account creation will fail. It is best to set this to 5-10% above total expected participants.
* An Amazon Certificate Manager (ACM) validated server certificate in N. Virginia, to encrypt access to the web application. 
{{% notice warning %}}
The certificate needs to be created in the N. Virginia region to work with Amazon CloudFront. Also, the issued certificate must support the fully qualified domain name you wish to use. For example, a certificate for `*.example.com` is valid for the domain name `cdd.example.com`, but would *not* work for `cdd.foo.example.com` since the wildcard is only matches the third element `foo`, and not the  fourth one, `cdd`.
{{% /notice %}}
