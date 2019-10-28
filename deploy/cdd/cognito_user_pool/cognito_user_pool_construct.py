"""
Construct to create Cognito User Pool from L1 constructs until
schema support added to L2 construct.

props: CognitoUserPoolProps = CognitoUserPoolProps(
    user_pool_name: str = "PoolName",
    schema=[
        {
            "name": "group",
            "attributeDataType": "String",
            "mutable": True,
            "required": False,
        }
    ],
    client_name = "UserPoolClientName"
)
"""

from aws_cdk import aws_cognito as cognito, aws_iam as iam, core


class CognitoUserPoolProps(object):
    def __init__(
        self,
        user_pool_name: str,
        client_name: str,
        alias_attributes: str = None,
        auto_verified_attributes: str = None,
        schema: list = None,
        policies: dict = None,
        username_attributes=None,
    ):
        self._alias_attributes = alias_attributes
        self._auto_verified_attributes = auto_verified_attributes
        self._user_pool_name = user_pool_name
        self._client_name = client_name
        self._schema = schema
        self._policies = policies
        self._username_attributes = username_attributes

    @property
    def auto_verified_attributes(self) -> str:
        return self._auto_verified_attributes

    @property
    def alias_attributes(self) -> str:
        return self._alias_attributes

    @property
    def user_pool_name(self) -> str:
        return self._user_pool_name

    @property
    def client_name(self) -> str:
        return self._client_name

    @property
    def schema(self) -> list:
        return self._schema

    @property
    def policies(self) -> dict:
        return self._policies

    @property
    def username_attributes(self) -> str:
        return self._username_attributes

class CognitoUserPoolConstruct(core.Construct):
    def __init__(
        self, scope: core.Construct, id: str, props: CognitoUserPoolProps
    ) -> None:
        super().__init__(scope, id)

        # Create L1 user pool

        if "phone_number" in props.auto_verified_attributes:
            sns_role = iam.Role(
                # Role to allow Cognitio to send SNS (SMS) messages
                self,
                "SNSRole",
                assumed_by=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
                inline_policies=[
                    iam.PolicyDocument(
                        statements=[
                            iam.PolicyStatement(
                                actions=["sns:Publish"], resources=["*"]
                            )
                        ]
                    )
                ],
            )

            user_pool = cognito.CfnUserPool(
                self,
                "UserPool",
                alias_attributes=props.alias_attributes,
                auto_verified_attributes=props.auto_verified_attributes,
                user_pool_name=props._user_pool_name,
                schema=props._schema,
                policies=props._policies,
                sms_configuration=cognito.CfnUserPool.SmsConfigurationProperty(
                    external_id=props.user_pool_name + "-external",
                    sns_caller_arn=sns_role.role_arn,
                ),
            )
        else:
            # Email verification, SMS config not needed
            user_pool = cognito.CfnUserPool(
                self,
                "UserPool",
                alias_attributes=props.alias_attributes,
                auto_verified_attributes=props.auto_verified_attributes,
                user_pool_name=props._user_pool_name,
                schema=props._schema,
                policies=props._policies,
                username_attributes=props._username_attributes,
            )

        user_pool_client = cognito.CfnUserPoolClient(
            self,
            "UserPoolClient",
            user_pool_id=user_pool.ref,
            client_name=props._client_name,
            generate_secret=False,
            refresh_token_validity=30,
        )
        self.user_pool = user_pool
        self.user_pool_id = user_pool.ref
        self.user_pool_arn = user_pool.attr_arn
        self.client_id = user_pool_client.ref
        self.provider_name = user_pool.attr_provider_name
        core.CfnOutput(
            self,
            "CognitoUserPoolId",
            export_name="CognitoUserPoolId",
            value=user_pool.ref,
        )
        core.CfnOutput(
            self,
            "CognitoUserPoolIdArn",
            export_name="CognitoUserPoolIdArn",
            value=user_pool.attr_arn,
        )
        core.CfnOutput(
            self,
            "CognitoClientId",
            export_name="CognitoClientId",
            value=user_pool_client.ref,
        )
