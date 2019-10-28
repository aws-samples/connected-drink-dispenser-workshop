import setuptools


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
        "aws-cdk.core",
        "aws_cdk.aws_cognito",
        "aws_cdk.aws_cloudfront",
        "aws_cdk.aws_dynamodb",
        "aws_cdk.aws_s3",
        "aws_cdk.aws_iam",
        "aws_cdk.aws_iot",
        "aws_cdk.aws_route53",
        "aws_cdk.aws_route53_targets"
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
