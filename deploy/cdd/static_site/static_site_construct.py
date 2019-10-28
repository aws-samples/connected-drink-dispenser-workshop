"""
Generates static web site, CloudFormation, and locked down access to bucket
from provided properties. If valid certificate is found for domain name, that is
included also.

Example:
from .static_site.static_site_construct import StaticSiteConstruct, StaticSiteProps


class MyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        props: StaticSiteProps = StaticSiteProps(
            fqdn=scope.node.try_get_context('fqdn'),
            hosted_zone_id=scope.node.try_get_context('hosted_zone_id'),
            certificate_arn=scope.node.try_get_context('certificate_arn')
        )
        StaticSiteConstruct(self, "MyStaticSiteConstruct", props)
"""

from aws_cdk import (
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_iam as iam,
    core,
)


class StaticSiteProps(object):
    def __init__(
        self,
        fqdn: str,
        hosted_zone_id: str,
        certificate_arn: str = None,
        error_configuration = [],
    ):
        self._fqdn = fqdn
        self._hosted_zone_id = hosted_zone_id
        self._certificate_arn = certificate_arn
        self._error_configuration = error_configuration

    @property
    def fqdn(self) -> str:
        return self._fqdn

    @property
    def hosted_zone_id(self) -> str:
        return self._hosted_zone_id

    @property
    def certificate_arn(self) -> str:
        return self._certificate_arn

    # Error config is for CloudFront actions, specifically for SPA related actions
    @property
    def error_configuration(self) -> list:
        return self._error_configuration


class StaticSiteConstruct(core.Construct):
    def __init__(self, scope: core.Construct, id: str, props: StaticSiteProps) -> None:
        super().__init__(scope, id)

        fqdn = props.fqdn
        certificate_arn = props.certificate_arn
        error_configuration = props.error_configuration

        if len(error_configuration) == 0:
            error_codes = None
        else:
            error_codes = []
            for error_config in error_configuration:
                error_codes.append(
                    cloudfront.CfnDistribution.CustomErrorResponseProperty(
                        error_code=error_config["error_code"],
                        error_caching_min_ttl=error_config["error_caching_min_ttl"],
                        response_code=error_config["response_code"],
                        response_page_path=error_config["response_page_path"],
                    )
                )

        # Content Bucket
        site_bucket = s3.Bucket(
            self,
            "SiteBucket",
            bucket_name=fqdn + "-static-site",
            website_index_document="index.html",
            website_error_document="index.html",
            block_public_access=s3.BlockPublicAccess(block_public_policy=True),
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        self.bucket_name = fqdn + "-static-site"
        self.bucket_resource = site_bucket
        origin_access_identity = cloudfront.CfnCloudFrontOriginAccessIdentity(
            self,
            "OriginIdentity",
            cloud_front_origin_access_identity_config={
                "comment": "Allow CloudFront to access web site"
            },
        )
        # Create IAM policy for S3 Canonical User
        policy_statement = iam.PolicyStatement()
        policy_statement.add_actions("s3:GetBucket*")
        policy_statement.add_actions("s3:GetObject*")
        policy_statement.add_actions("s3:List**")
        policy_statement.add_resources(site_bucket.bucket_arn)
        policy_statement.add_resources(f"{site_bucket.bucket_arn}/*")
        policy_statement.add_canonical_user_principal(
            origin_access_identity.attr_s3_canonical_user_id
        )
        site_bucket.add_to_resource_policy(policy_statement)
        core.CfnOutput(self, "Bucket", value=site_bucket.bucket_name)

        # CloudFront distribution with or without certificate
        source_configuration = cloudfront.SourceConfiguration(
            s3_origin_source=cloudfront.S3OriginConfig(
                s3_bucket_source=site_bucket,
                origin_access_identity_id=origin_access_identity.ref,
            ),
            behaviors=[cloudfront.Behavior(is_default_behavior=True)],
        )
        # Use ACM Certificate if provided, otherwise no-SSL
        if certificate_arn:
            # CloudFront distribution that provides HTTPS
            alias_configuration = cloudfront.AliasConfiguration(
                acm_cert_ref=certificate_arn,
                names=[fqdn],
                ssl_method=cloudfront.SSLMethod.SNI,
                security_policy=cloudfront.SecurityPolicyProtocol.TLS_V1_1_2016,
            )
            distribution = cloudfront.CloudFrontWebDistribution(
                self,
                "SiteDistribution",
                alias_configuration=alias_configuration,
                error_configurations=error_codes,
                origin_configs=[source_configuration],
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            )
        else:
            distribution = cloudfront.CloudFrontWebDistribution(
                self,
                "SiteDistribution",
                origin_configs=[source_configuration],
                error_configurations=error_codes,
            )
        core.CfnOutput(self, "DistributionId", value=distribution.distribution_id)

        # Route53 alias record for the CloudFront Distribution
        zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            id="HostedZoneID",
            hosted_zone_id=props.hosted_zone_id,
            zone_name=props.fqdn,
        )

        route53.ARecord(
            self,
            "SiteAliasRecord",
            record_name=fqdn,
            target=route53.AddressRecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
            zone=zone,
        )
