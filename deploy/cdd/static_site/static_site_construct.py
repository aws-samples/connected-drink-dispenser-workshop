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
        error_configuration=[],
        output_name: str = None,
    ):
        self._fqdn = fqdn
        self._hosted_zone_id = hosted_zone_id
        self._certificate_arn = certificate_arn
        self._error_configuration = error_configuration
        self._output_name = output_name

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

    # Name to apply to output if provided
    @property
    def output_name(self) -> str:
        return self._output_name


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

        # Uses new method for OAI (still breaking changes) - https://github.com/aws/aws-cdk/pull/4491
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self,
            "OriginIdentity"
        )
        # Add CloudFront Origin Access Identity to the bucket
        site_bucket.grant_read(origin_access_identity)

        core.CfnOutput(self, "Bucket", value=site_bucket.bucket_name)

        # CloudFront distribution with or without certificate
        source_configuration = cloudfront.SourceConfiguration(
            s3_origin_source=cloudfront.S3OriginConfig(
                s3_bucket_source=site_bucket,
                origin_access_identity=origin_access_identity,
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
        core.CfnOutput(
            self,
            "DistributionId",
            value=distribution.distribution_id,
            export_name=props.output_name,
        )

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
            target=route53.RecordTarget.from_alias(
                alias_target=targets.CloudFrontTarget(distribution)
            ),
            zone=zone,
        )
