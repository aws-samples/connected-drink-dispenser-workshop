"""
Creates a custom resource to be called during CREATE, UPDATE, or DELETE

NOTE: If using this construct ensure function names and the physical_id
      parameter are unique

Example:
from aws_cdk import aws_lambda as lambda_
from .custom_resource.custom_resource_construct import CustomResourceConstruct, CustomResourceProps

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        props: CustomResourceProps = CustomResourceProps(
            name="MyFunctionName",              # Name for function, ensure it is unique
            lambda_directory="./example"        # Location of Lambda relative to base cdk-app
            handler="index.main",               # filename.function to invoke for custom_resource_handler/
            timeout=30,                         # max execution in seconds
            runtime=lambda_.Runtime.PYTHON_3_7, # Runtime value from aws_lambda
            resource_properties={"foo": "bar"}, # ?Dictionary of resourceproperties as part of Properties object
            environment={"FOO": "bar"}          # ?Dictionary of environment variables passed to Lambda
        )
        resource = CustomResourceConstruct(self, "MyCustomResourceConstruct", props)
        resource.add_policy_to_role(aws_cdk.iam.PolicyStatement())
"""

import uuid
from aws_cdk import (
    aws_cloudformation as cfn,
    aws_iam as iam,
    aws_lambda as lambda_,
    core,
)
from os import path


class CustomResourceProps(object):
    """
    Creates properties object with attributes to pass to CustomResourceConstruct
    """
    def __init__(
        self,
        name: str,
        lambda_directory: str,
        handler: str,
        timeout: int,
        runtime: lambda_.Runtime = None,
        policy: iam.PolicyStatement = None,
        resource_properties: dict = None,
        environment: dict = None,
    ):
        self._name = name
        self._lambda_directory = lambda_directory
        self._handler = handler
        self._timeout = timeout
        self._runtime = runtime
        self._resource_properties = resource_properties
        self._environment = environment

    @property
    def name(self) -> str:
        return self._name

    @property
    def lambda_directory(self) -> str:
        return self._lambda_directory

    @property
    def handler(self) -> str:
        return self._handler

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def runtime(self) -> lambda_.Runtime:
        return self._runtime

    @property
    def resource_properties(self) -> dict:
        return self._resource_properties

    @property
    def environment(self) -> dict:
        return self._environment


class CustomResourceConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, id: str, props: CustomResourceProps, **kwargs
    ) -> None:
        super().__init__(scope, id)

        name = props.name
        lambda_directory = props.lambda_directory
        handler = props.handler
        timeout = props.timeout
        runtime = props.runtime
        environment = props.environment
        resource_properties = props.resource_properties
        lambda_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name + handler))

        resource = cfn.CustomResource(
            self,
            "Resource",
            provider=cfn.CustomResourceProvider.lambda_(
                lambda_.SingletonFunction(
                    self,
                    "Singleton",
                    environment=environment,
                    function_name=name,
                    uuid=lambda_uuid,
                    code=lambda_.AssetCode(lambda_directory),
                    handler=handler,
                    timeout=core.Duration.seconds(timeout),
                    runtime=runtime,
                )
            ),
            properties=resource_properties,
        )
        self.resource = resource
        self.response = resource.get_att("Response").to_string()

    def add_policy_to_role(self, policy: iam.PolicyStatement):
        """Adds inline policy statement to the Lambda service role"""
        lambda_function = self.node.find_child("Singleton")
        lambda_function.add_to_role_policy(policy)
