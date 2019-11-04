__copyright__ = (
    "Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved."
)
__license__ = "MIT-0"


from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    aws_apigateway as apigateway,
    aws_iot as iot,
    core,
)

# Import our constructs relative to app
from .static_site.static_site_construct import StaticSiteConstruct, StaticSiteProps
from .custom_resource.custom_resource_construct import (
    CustomResourceConstruct,
    CustomResourceProps,
)
from .cognito_user_pool.cognito_user_pool_construct import (
    CognitoUserPoolConstruct,
    CognitoUserPoolProps,
)


def add_cors_options(api_resource):
    """Add response to OPTIONS to enable CORS on an API resource."""
    mock = apigateway.MockIntegration(
        integration_responses=[
            {
                "statusCode": "200",
                "responseParameters": {
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    # "method.response.header.Access-Control-Allow-Credentials": "'true'",
                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,PUT,POST,DELETE'",
                },
            }
        ],
        passthrough_behavior=apigateway.PassthroughBehavior.WHEN_NO_MATCH,
        # content_handling=apigateway.ContentHandling.CONVERT_TO_TEXT,
        request_templates={"application/json": '{"statusCode": 200}'},
    )
    method_response = apigateway.MethodResponse(
        status_code="200",
        response_parameters={
            "method.response.header.Access-Control-Allow-Headers": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            # "method.response.header.Access-Control-Allow-Credentials": True,
            "method.response.header.Access-Control-Allow-Origin": True,
        },
    )
    api_resource.add_method(
        "OPTIONS", integration=mock, method_responses=[method_response]
    )


def add_resource_method(
    resource, http_method: str, integration, authorization_type, authorizer
):
    """From an API resource, create method and reference authorizer. Note that config is specific to API setup"""
    # https://github.com/aws/aws-cdk/issues/723
    method = resource.add_method(
        http_method=http_method,
        integration=integration,
        authorization_type=authorization_type,
    )
    method_resource = method.node.find_child("Resource")
    method_resource.add_property_override(
        "AuthorizerId", {"Ref": authorizer.logical_id}
    )


class CddBase(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        host_name,
        cert_arn,
        zone_id,
        admin_user: str,
        admin_password: str,
        cloud9_instance_size: str,
        participant_limit: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        stack = core.Stack.of(self)
        stack.template_options.description = "Connected Drink Dispenser Workshop"

        # Static Website
        props: StaticSiteProps = StaticSiteProps(
            fqdn=host_name,
            hosted_zone_id=zone_id,
            certificate_arn=cert_arn,
            error_configuration=[
                {
                    "error_code": 403,
                    "error_caching_min_ttl": 300,
                    "response_code": 200,
                    "response_page_path": "/index.html",
                },
                {
                    "error_code": 404,
                    "error_caching_min_ttl": 300,
                    "response_code": 200,
                    "response_page_path": "/index.html",
                },
            ],
        )
        cdd_site = StaticSiteConstruct(self, "StaticSite", props)

        # Custom resource to clean out static website bucket prior to delete
        # TODO: Move this to the StaticSiteConstruct as option
        props: CustomResourceProps = CustomResourceProps(
            name=id + "-CR-S3DeleteObjects",
            lambda_directory="./lambda_functions/cr_s3_delete",
            handler="index.main",
            timeout=30,
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={"BUCKET_NAME": cdd_site.bucket_name},
        )
        s3_delete_cr = CustomResourceConstruct(self, "EmptyCddS3Bucket", props)
        # DependsOn the bucket (we need to delete objects before the bucket is deleted)
        s3_delete_cr.resource.node.add_dependency(cdd_site.bucket_resource)
        policy_statement = iam.PolicyStatement()
        policy_statement.add_actions("s3:GetBucket*")
        policy_statement.add_actions("s3:GetObject*")
        policy_statement.add_actions("s3:DeleteObject*")
        policy_statement.add_actions("s3:List*")
        policy_statement.add_resources(cdd_site.bucket_resource.bucket_arn)
        policy_statement.add_resources(f"{cdd_site.bucket_resource.bucket_arn}/*")
        s3_delete_cr.add_policy_to_role(policy_statement)

        # IAM Constructs
        user_group = iam.Group(
            self,
            "UserGroup",
            group_name=id + "-CDDUserGroup",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("ReadOnlyAccess")
            ],
        )

        # DynamoDB tables
        user_db = dynamodb.Table(
            # UserId as key, user "admin" tracks next available dispenser id
            # No access to users, RW to Cognito Lambda
            self,
            "UserTable",
            table_name=id + "-UserTable",
            partition_key={"name": "userName", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        dispenser_db = dynamodb.Table(
            # Dispenser ID and credit amount - RO to users, RW to APIs
            self,
            "DispenserTable",
            table_name=id + "-DispenserTable",
            partition_key={
                "name": "dispenserId",
                "type": dynamodb.AttributeType.STRING,
            },
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        dispenser_events = dynamodb.Table(
            # Recorded events from dispenser actions
            self,
            "DispenserEvents",
            table_name=id + "-DispenserEvents",
            partition_key={
                "name": "dispenserId",
                "type": dynamodb.AttributeType.STRING,
            },
            sort_key={"name": "timestamp", "type": dynamodb.AttributeType.STRING},
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        # Cognito Resources
        # User pool with phone_number as username
        props: CognitoUserPoolProps = CognitoUserPoolProps(
            user_pool_name=id + "-users",
            client_name=id + "-webclient",
            auto_verified_attributes=["phone_number"],
            schema=[
                {
                    "name": "group",
                    "attributeDataType": "String",
                    "mutable": True,
                    "required": False,
                },
                {
                    "name": "dispenserId",
                    "attributeDataType": "String",
                    "mutable": True,
                    "required": False,
                },
            ],
            policies={
                "passwordPolicy": {
                    "minimumLength": 6,
                    "requireLowercase": True,
                    "requireNumbers": True,
                    "requireSymbols": False,
                    "requireUppercase": False,
                }
            },
        )
        user_pool = CognitoUserPoolConstruct(self, "UserPool", props)

        # Role and lambda triggers
        lambda_cognito_access_role = iam.Role(
            # Access to IDP calls (for triggers)
            self,
            "LambdaCognitoAccessRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        iam.PolicyStatement(actions=["cognito-idp:*"], resources=["*"]),
                        iam.PolicyStatement(actions=["dynamodb:*"], resources=["*"]),
                    ]
                )
            ],
        )

        # Triggers for UserPool
        # Pre-sign-up: triggered when username, password, and phone number submitted
        lambda_cognito_trigger_pre_signup = lambda_.Function(
            self,
            "CogntioTriggerPreSignUp",
            function_name=id + "-CogntioTriggerPreSignUp",
            code=lambda_.AssetCode("./lambda_functions/cog_pre_signup"),
            handler="lambda.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_cognito_access_role,
            timeout=core.Duration.seconds(6),
            environment={
                "USER_TABLE": user_db.table_name,
                "PARTICIPANT_LIMIT": participant_limit,
            },
        )
        lambda_cognito_trigger_pre_signup.add_permission(
            "AllowCognitoPreSign",
            principal=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            source_arn=user_pool.user_pool_arn,
        )
        # Post confirmation: triggered after validation code provided
        lambda_cognito_trigger_post_confirm = lambda_.Function(
            self,
            "CogntioTriggerPostConfirm",
            function_name=id + "-CogntioTriggerPostConfirm",
            code=lambda_.AssetCode("./lambda_functions/cog_post_confirm"),
            handler="lambda.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_cognito_access_role,
            timeout=core.Duration.seconds(6),
            environment={
                "USER_TABLE": user_db.table_name,
                "PARTICIPANT_LIMIT": participant_limit,
            },
        )
        lambda_cognito_trigger_post_confirm.add_permission(
            "AllowCognitoPostConfirm",
            principal=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            source_arn=user_pool.user_pool_arn,
        )

        # Attach triggers to pool
        user_pool.user_pool.lambda_config = cognito.CfnUserPool.LambdaConfigProperty(
            pre_sign_up=lambda_cognito_trigger_pre_signup.function_arn,
            post_confirmation=lambda_cognito_trigger_post_confirm.function_arn,
        )

        cognito.CfnUserPoolGroup(
            self,
            "UserPoolCDDUser",
            group_name="cdd_user",
            description="General users of CDD (participants)",
            user_pool_id=user_pool.user_pool_id,
        )
        cognito.CfnUserPoolGroup(
            self,
            "UserPoolCDDAdmin",
            group_name="cdd_admin",
            description="CDD administrators",
            user_pool_id=user_pool.user_pool_id,
        )
        identity_pool = cognito.CfnIdentityPool(
            self,
            "IdentityPool",
            identity_pool_name=id.replace("-", "") + "_idpool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                {
                    "clientId": user_pool.client_id,
                    "providerName": user_pool.provider_name,
                }
            ],
        )
        core.CfnOutput(
            self,
            "CognitoIdentityPoolId",
            export_name="CognitoIdentityPoolId",
            value=identity_pool.ref,
        )

        # Custom resource to create admin user - cannot do via CFn to set password
        props: CustomResourceProps = CustomResourceProps(
            name=id + "-CR-CreateCognitoAdminUser",
            lambda_directory="./lambda_functions/cr_create_admin_user",
            handler="index.main",
            timeout=30,
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
                "COGNITO_CLIENT_ID": user_pool.client_id,
                "ADMIN_USERNAME": admin_user,
                "ADMIN_PASSWORD": admin_password,
            },
        )
        create_admin_user_cr = CustomResourceConstruct(self, "CreateAdminUser", props)
        # DependsOn the user pool
        create_admin_user_cr.resource.node.add_dependency(user_pool)
        policy_statement = iam.PolicyStatement()
        policy_statement.add_actions("cognito-idp:SignUp")
        policy_statement.add_actions("cognito-idp:AdminConfirmSignUp")
        policy_statement.add_resources("*")
        create_admin_user_cr.add_policy_to_role(policy_statement)

        # IAM roles for identity pool auth/unauth
        cog_unauth_role = iam.Role(
            self,
            "cognitoUnauthRole",
            role_name=f"Cognito_{identity_pool.identity_pool_name}_Unauth_Role",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )
        cog_unauth_role.attach_inline_policy(
            iam.Policy(
                self,
                "cognitoUnauth",
                policy_name="cognitoUnauth",
                statements=[
                    iam.PolicyStatement(
                        actions=["mobileanalytics:PutEvents", "cognito-sync:*"],
                        resources=["*"],
                    )
                ],
            )
        )
        cog_auth_role = iam.Role(
            self,
            "cognitoAuthRole",
            role_name=f"Cognito_{identity_pool.identity_pool_name}_Auth_Role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonESCognitoAccess")
            ],
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )
        cog_auth_role.attach_inline_policy(
            iam.Policy(
                self,
                "cognitoAuth",
                policy_name="cognitoAuth",
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "mobileanalytics:PutEvents",
                            "cognito-sync:*",
                            "execute-api:*",
                        ],
                        resources=["*"],
                    ),
                    # Provide full access to IoT for the authenticated user
                    # The AWS IoT policy scopes down the access
                    iam.PolicyStatement(actions=["iot:*"], resources=["*"]),
                ],
            )
        )
        # Finally, attach auth and unauth roles to Identity pool
        cognito.CfnIdentityPoolRoleAttachment(
            self,
            "CDDIdentityPoolRoleAttach",
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": cog_auth_role.role_arn,
                "unauthenticated": cog_unauth_role.role_arn,
            },
        )

        ### Supporting IAM Roles and Policies
        lambda_full_access_role = iam.Role(
            # Wide open role for Lambda's to access other services
            self,
            "LambdaFullAccessRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        iam.PolicyStatement(actions=["*"], resources=["*"]),
                    ]
                )
            ],
        )
        lambda_iot_full_access_role = iam.Role(
            # Wide open role for Lambda's to access other services
            self,
            "LambdaIoTFullAccessRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        iam.PolicyStatement(
                            actions=["dynamodb:*", "iot:*"], resources=["*"]
                        ),
                    ]
                )
            ],
        )
        lambda_api_app_role = iam.Role(
            # Role for APIG Lambda functions - make specific per Lambda/method if needed
            self,
            "ApiAppRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        iam.PolicyStatement(
                            actions=["dynamodb:*"],
                            resources=[
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{dispenser_db.table_name}",
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{dispenser_events.table_name}",
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{user_db.table_name}",
                            ],
                        ),
                        iam.PolicyStatement(actions=["iot:*"], resources=["*"]),
                    ]
                )
            ],
        )
        lambda_api_delete_user_role = iam.Role(
            # Role for APIG Lambda delete user - specific as this has to delete multiple services
            self,
            "ApiDeleteUserRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        iam.PolicyStatement(
                            actions=["dynamodb:*"],
                            resources=[
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{dispenser_db.table_name}",
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{dispenser_events.table_name}",
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{user_db.table_name}",
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=["cloud9:DeleteEnvironment"], resources=["*"]
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "iam:DeleteLoginProfile",
                                "iam:ListGroupsForUser",
                                "iam:RemoveUserFromGroup",
                                "iam:DeleteUser",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            actions=["cognito-idp:AdminDeleteUser"], resources=["*"]
                        ),
                        iam.PolicyStatement(actions=["iot:*"], resources=["*"]),
                    ]
                )
            ],
        )
        lambda_api_dispense_role = iam.Role(
            # Role for lambda
            self,
            "CommandRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        iam.PolicyStatement(
                            actions=["dynamodb:*"],
                            resources=[
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{dispenser_db.table_name}",
                                f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{dispenser_events.table_name}",
                            ],
                        ),
                        iam.PolicyStatement(actions=["iot:*"], resources=["*"]),
                    ]
                )
            ],
        )

        # IoT Policies
        iot_policy_dispenser_limited = iot.CfnPolicy(
            self,
            "IoTDispenserLimitedPolicy",
            policy_name=id + "-DispenserLimitedAccess",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Connect"],
                        "Resource": [
                            f"arn:aws:iot:{stack.region}:{stack.account}:client/${{iot.Connection.Thing.ThingName}}"
                        ],
                        "Condition": {
                            "Bool": {"iot:Connection.Thing.IsAttached": [True]}
                        },
                    },
                    {"Effect": "Allow", "Action": ["iot:Receive"], "Resource": ["*"]},
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Subscribe"],
                        "Resource": [
                            f"arn:aws:iot:{stack.region}:{stack.account}:topicfilter/$aws/things/${{iot:Certificate.Subject.CommonName}}/shadow/*",
                            f"arn:aws:iot:{stack.region}:{stack.account}:topicfilter/$aws/things/${{iot:Certificate.Subject.CommonName}}/cmd/${{iot:Certificate.Subject.CommonName}}",
                        ],
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Publish"],
                        "Resource": [
                            f"arn:aws:iot:{stack.region}:{stack.account}:topic/$aws/things/${{iot:Certificate.Subject.CommonName}}/shadow/update",
                            f"arn:aws:iot:{stack.region}:{stack.account}:topic/$aws/things/${{iot:Certificate.Subject.CommonName}}/shadow/get",
                            f"arn:aws:iot:{stack.region}:{stack.account}:topic/test/${{iot:Certificate.Subject.CommonName}}",
                            f"arn:aws:iot:{stack.region}:{stack.account}:topic/cmd/${{iot:Certificate.Subject.CommonName}}/response",
                        ],
                    },
                ],
            },
        )
        iot_policy_client = iot.CfnPolicy(
            self,
            "IoTClientPolicy",
            policy_name=id + "-IoTClientAccess",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Connect", "iot:Receive"],
                        "Resource": ["*"],
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Subscribe"],
                        "Resource": [
                            f"arn:aws:iot:{stack.region}:{stack.account}:topicfilter/events/*",
                            f"arn:aws:iot:{stack.region}:{stack.account}:topicfilter/$aws/things/*/shadow/update/accepted",
                        ],
                    },
                ],
            },
        )

        ### Lambda Functions
        # General Lambda Functions NOT associated with APIG
        lambda_process_events = lambda_.Function(
            self,
            "ProcessEvents",
            function_name=id + "-ProcessEvents",
            code=lambda_.AssetCode("./lambda_functions/process_events"),
            handler="process_events.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_iot_full_access_role,
            timeout=core.Duration.seconds(20),
            environment={
                "EVENT_TABLE": dispenser_events.table_name,
                "STATUS_TABLE": dispenser_db.table_name,
            },
        )

        ## API Lambda functions
        # Return credit for dispenser
        api_credit_dispenser_function = lambda_.Function(
            self,
            "ApiCreditDispenserFunction",
            function_name=id + "-ApiCreditDispenserFunction",
            code=lambda_.AssetCode("./lambda_functions/api_credit_dispenser"),
            handler="credit_dispenser.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_api_app_role,
            timeout=core.Duration.seconds(15),
            memory_size=128,
            environment={
                "DISPENSER_TABLE": dispenser_db.table_name,
                "EVENT_TABLE": dispenser_events.table_name,
            },
        )
        # Command
        api_command_function = lambda_.Function(
            self,
            "ApiCommandFunction",
            function_name=id + "-ApiCommandFunction",
            code=lambda_.AssetCode("./lambda_functions/api_command"),
            handler="command.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_api_app_role,
            timeout=core.Duration.seconds(15),
            memory_size=128,
            environment={
                "DispenserTable": dispenser_db.table_name,
                "EventTable": dispenser_events.table_name,
            },
        )
        # Request dispense operation (set shadow or command to dispense)
        api_dispense_function = lambda_.Function(
            self,
            "ApiDispenseFunction",
            function_name=id + "-ApiDispenseFunction",
            code=lambda_.AssetCode("./lambda_functions/api_dispense"),
            handler="dispense.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_api_dispense_role,
            timeout=core.Duration.seconds(15),
            memory_size=128,
            environment={
                "DISPENSER_TABLE": dispenser_db.table_name,
                "EVENT_TABLE": dispenser_events.table_name,
            },
        )
        # Request dispense operation (set shadow or command to dispense)
        api_dispenser_status_function = lambda_.Function(
            self,
            "ApiDispenserStatusFunction",
            function_name=id + "-ApiDispenserStatusFunction",
            code=lambda_.AssetCode("./lambda_functions/api_dispenser_status"),
            handler="dispenser_status.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_api_app_role,
            timeout=core.Duration.seconds(15),
            memory_size=128,
            environment={
                "DISPENSER_TABLE": dispenser_db.table_name,
            },
        )
        # Request user details from user table, create resources if needed
        # NOTE: This uses an overley permissive policy to create the resources needed
        api_get_resources_function = lambda_.Function(
            self,
            "ApiGetResourcesFunction",
            function_name=id + "-ApiGetResourcesFunction",
            code=lambda_.AssetCode("./lambda_functions/api_get_resources"),
            handler="get_resources.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_full_access_role,
            # Timeout is for user creation: certain tasks such as Cloud9 may take longer
            # TODO: For race conditions (double execute of API), add tag to DDB user table that
            # creation in progress
            timeout=core.Duration.seconds(300),
            memory_size=128,
            environment={
                "DISPENSER_TABLE": dispenser_db.table_name,
                "EVENT_TABLE": dispenser_events.table_name,
                "USER_TABLE": user_db.table_name,
                "USER_PERMISSIONS_GROUP": user_group.group_name,
                "IOT_POLICY_DISPENSER_LIMITED": iot_policy_dispenser_limited.policy_name,
                "IOT_POLICY_CLIENT": iot_policy_client.policy_name,
                "CLOUD9_INSTANCE_SIZE": cloud9_instance_size,
            },
        )
        # Request user details from user table
        api_delete_user_function = lambda_.Function(
            self,
            "ApiDeleteUserFunction",
            function_name=id + "-ApiDeleteUserFunction",
            code=lambda_.AssetCode("./lambda_functions/api_delete_user"),
            handler="delete_user.handler",
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambda_api_delete_user_role,
            timeout=core.Duration.seconds(28),
            memory_size=256,
            environment={
                "DISPENSER_TABLE": dispenser_db.table_name,
                "EVENT_TABLE": dispenser_events.table_name,
                "USER_TABLE": user_db.table_name,
                "USER_POOL_ID": user_pool.user_pool_id,
            },
        )

        ### API Gateway
        api = apigateway.RestApi(
            self,
            id + "-API",
            api_key_source_type=apigateway.ApiKeySourceType.HEADER,
            deploy_options=apigateway.StageOptions(stage_name="prod"),
        )

        core.CfnOutput(
            self,
            "APIEndpoint",
            export_name="APIEndpoint",
            value=f"https://{api.rest_api_id}.execute-api.{stack.region}.amazonaws.com/prod/",
        )
        # Although / is not used as method, provide OPTIONS for hinting CORS
        add_cors_options(api.root)
        # Define Cognito authorizer and attach to gateway
        cog_authorizer = apigateway.CfnAuthorizer(
            self,
            "CognitoAuth",
            name="CognitoAuthName",
            rest_api_id=api.rest_api_id,
            type="COGNITO_USER_POOLS",
            identity_source="method.request.header.Authorization",
            provider_arns=[user_pool.user_pool_arn],
        )

        # # Resources (paths) and methods (GET, POST, etc.), for the API
        api_credit_resource = api.root.add_resource("credit")
        add_resource_method(
            api_credit_resource,
            http_method="GET",
            integration=apigateway.LambdaIntegration(api_credit_dispenser_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cog_authorizer,
        )
        add_cors_options(api_credit_resource)
        # command
        api_command_resource = api.root.add_resource("command")
        add_resource_method(
            api_command_resource,
            http_method="GET",
            integration=apigateway.LambdaIntegration(api_command_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cog_authorizer,
        )
        add_cors_options(api_command_resource)
        # Actuate dispenser
        api_dispense_resource = api.root.add_resource("dispense")
        add_resource_method(
            api_dispense_resource,
            http_method="GET",
            integration=apigateway.LambdaIntegration(api_dispense_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cog_authorizer,
        )
        add_cors_options(api_dispense_resource)
        # Return dispenser status (from DynamoDB)
        api_dispenser_status_resource = api.root.add_resource("status")
        add_resource_method(
            api_dispenser_status_resource,
            http_method="GET",
            integration=apigateway.LambdaIntegration(api_dispenser_status_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cog_authorizer,
        )
        add_cors_options(api_dispenser_status_resource)
        # Return user details from User Table
        api_get_resources_resource = api.root.add_resource("getResources")
        add_resource_method(
            api_get_resources_resource,
            http_method="POST",
            integration=apigateway.LambdaIntegration(api_get_resources_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cog_authorizer,
        )
        add_cors_options(api_get_resources_resource)
        # Create a user based on valid token
        api_delete_user_resource = api.root.add_resource("deleteUser")
        add_resource_method(
            api_delete_user_resource,
            http_method="POST",
            integration=apigateway.LambdaIntegration(api_delete_user_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cog_authorizer,
        )
        add_cors_options(api_delete_user_resource)

        # Create policy and reference group
        iam.Policy(
            self,
            "UserPermissionsPolicy",
            groups=[user_group],
            policy_name=id + "-UserPermissions",
            statements=[
                iam.PolicyStatement(
                    actions=["iot:Subscribe", "iot:Connect", "iot:Receive"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    # Do not all users to see the table with credentials
                    effect=iam.Effect.DENY,
                    actions=["dynamodb:*"],
                    resources=[
                        f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{user_db.table_name}"
                    ],
                ),
            ],
        )

        # IoT Constructs
        # Rule to process shadow events and send to logging
        iot_rule_log_shadow_events = iot.CfnTopicRule(
            self,
            "LogShadowEventsRule",
            rule_name=id.replace("-", "") + "_LogShadowEvents",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                description="Based on shadow topic and content, process messages via Lambda",
                rule_disabled=False,
                aws_iot_sql_version="2016-03-23",
                sql="select *, topic() AS topic FROM '$aws/things/+/shadow/update/documents'",
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn=lambda_process_events.function_arn
                        )
                    )
                ],
            ),
        )
        # Allow rule to invoke the logging function
        lambda_process_events.add_permission(
            "AllowIoTRule1",
            principal=iam.ServicePrincipal("iot.amazonaws.com"),
            source_arn=iot_rule_log_shadow_events.attr_arn,
        )
        # Rule to process generic events and send to logging
        iot_rule_log_generic_events = iot.CfnTopicRule(
            self,
            "LogGenericEventsRule",
            rule_name=id.replace("-", "") + "_LogGenericEvents",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                description="Log generic events, enrich, then send to Lambda",
                rule_disabled=False,
                aws_iot_sql_version="2016-03-23",
                sql="select *, timestamp() AS ts, topic() AS topic FROM 'events'",
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn=lambda_process_events.function_arn
                        )
                    )
                ],
            ),
        )
        # Allow generic_events rule to Invoke the process_events function
        lambda_process_events.add_permission(
            "AllowIoTRule2",
            principal=iam.ServicePrincipal("iot.amazonaws.com"),
            source_arn=iot_rule_log_generic_events.attr_arn,
        )
        # Rule to process dispenser specific events and send to logging
        iot_rule_log_dispenser_events = iot.CfnTopicRule(
            self,
            "LogDispenserEventsRule",
            rule_name=id.replace("-", "") + "_LogDispenserEvents",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                description="Log specific dispenser events, enrich, then send to Lambda",
                rule_disabled=False,
                aws_iot_sql_version="2016-03-23",
                sql="select *, timestamp() AS ts, topic() AS topic FROM 'events/+'",
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn=lambda_process_events.function_arn
                        )
                    )
                ],
            ),
        )
        # Allow log_dispenser_events rule to Invoke the process_events function
        lambda_process_events.add_permission(
            "AllowIoTRule3",
            principal=iam.ServicePrincipal("iot.amazonaws.com"),
            source_arn=iot_rule_log_dispenser_events.attr_arn,
        )
        # Rule to process cmd/NNN/response WHERE "command=dispense"
        iot_rule_command_response_dispense = iot.CfnTopicRule(
            self,
            "DispenseCommandResponseRule",
            rule_name=id.replace("-", "") + "_DispenseCommandResponse",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                description="Invoke Lambda to process dispense commands from dispenser",
                rule_disabled=False,
                aws_iot_sql_version="2016-03-23",
                sql="select *, topic() AS topic FROM '$aws/things/+/shadow/update/accepted' WHERE isUndefined(state.reported.response) = False",
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn=api_dispense_function.function_arn
                        )
                    )
                ],
            ),
        )
        # Allow command_response rule to Invoke the dispense function to reconcile outstanding requests
        api_dispense_function.add_permission(
            "AllowIoTCommandResponseRule",
            principal=iam.ServicePrincipal("iot.amazonaws.com"),
            source_arn=iot_rule_command_response_dispense.attr_arn,
        )

        # Custom resource to delete workshop users - run to clean up any lingering ones
        # if the admin user didn't clean up. A lot of dependsOn as users are created with bindings
        # to other resources
        props: CustomResourceProps = CustomResourceProps(
            name=id + "-CR-DeleteParticipantUsers",
            lambda_directory="./lambda_functions/cr_delete_participant_users",
            handler="index.main",
            timeout=30,
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={
                # Read user records from UserTable
                "USER_TABLE": user_db.table_name,
                # Invoke the api_delete_user function
                "DELETE_USER_LAMBDA_FUNCTION": api_delete_user_function.function_arn,
            },
        )
        delete_participant_users_cr = CustomResourceConstruct(
            self, "DeleteParticpantUsers", props
        )
        # DependsOn the API Delete User Function
        delete_participant_users_cr.resource.node.add_dependency(
            api_delete_user_function
        )
        # DependsOn the user pool to delete Cognito users
        delete_participant_users_cr.resource.node.add_dependency(user_pool)
        # DependsOn the DynamoDB UserTable
        delete_participant_users_cr.resource.node.add_dependency(user_db)
        # DependsOn the IoT dispenser and client policies
        delete_participant_users_cr.resource.node.add_dependency(
            iot_policy_dispenser_limited
        )
        delete_participant_users_cr.resource.node.add_dependency(iot_policy_client)
        # DependsOn the IoT IAM user group
        delete_participant_users_cr.resource.node.add_dependency(user_group)
        # Permissions for function to delete users
        policy_statement = iam.PolicyStatement()
        policy_statement.add_actions("dynamodb:*")
        policy_statement.add_resources(
            f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/{user_db.table_name}"
        )
        delete_participant_users_cr.add_policy_to_role(policy_statement)
        policy_statement = iam.PolicyStatement()
        policy_statement.add_actions("lambda:InvokeFunction")
        policy_statement.add_resources(api_delete_user_function.function_arn)
        delete_participant_users_cr.add_policy_to_role(policy_statement)

