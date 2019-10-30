
# Welcome to the Connected Drink Dispenser Resource Setup!

This project will setup all AWS resources.

The `cdk.json` file tells the CDK Toolkit how to execute your app, while the `config.json` file provides the unique parameters for creating the cloud infrastructure.

Overall there are three steps to complete build and deployment:

1. Modify/create the `config.json` file with your parameters, `HostName` being the most important
1. Run the `cdk ... deploy` command to fully deploy the CloudFormation stack
1. Run the `python3 deploy_app.py` command to locally build the singe page application and copy it and the documentation to the provisioned S3 bucket

There are some individual steps to get started with CloudFormation Development Kit below, but also check out the documentation for more details.

## Individual Steps

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

# Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
