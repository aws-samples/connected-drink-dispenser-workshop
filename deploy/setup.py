import setuptools

__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cdk",
    version="0.0.1",
    description="Connected Drink Dispenser Resource Setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "cdd"},
    packages=setuptools.find_packages(where="cdd"),
    install_requires=[
        "boto3",
        "botocore",
        "tqdm",
        "aws-cdk.core>=1.20.0",
        "aws_cdk.aws_cognito>=1.20.0",
        "aws_cdk.aws_cloudfront>=1.20.0",
        "aws_cdk.aws_dynamodb>=1.20.0",
        "aws_cdk.aws_s3>=1.20.0",
        "aws_cdk.aws_iam>=1.20.0",
        "aws_cdk.aws_iot>=1.20.0",
        "aws_cdk.aws_route53>=1.20.0",
        "aws_cdk.aws_route53_targets>=1.20.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        # "Development Status :: 4 - Beta",
        # "Intended Audience :: Developers",
        # "License :: OSI Approved :: Apache Software License",
        # "Programming Language :: JavaScript",
        # "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
