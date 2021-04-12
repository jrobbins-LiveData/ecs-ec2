# based on https://blog.kylegalbraith.com/2019/10/24/how-to-run-docker-containers-via-aws-elastic-container-service/
from os import path

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import core as cdk
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationProtocol
from aws_cdk.aws_route53 import HostedZone


class EcsEc2Stack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Docker build
        asset = ecs.ContainerImage.from_asset(path.join(path.dirname(__file__), 'myWebApp'))

        # ECS cluster/resources

        # NOTE 't4g.micro' is a Graviton2 EC2 type
        # https://aws.amazon.com/ec2/graviton/
        # Free trial until June 30th 2021

        # NOTE Bottlerocket is AWS's new container-specific Linux
        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-bottlerocket.html
        # https://github.com/bottlerocket-os/bottlerocket/blob/develop/QUICKSTART-ECS.md
        # but doesn't seem to work yet with CDK constructs (https://github.com/aws/aws-cdk/issues/9945)     
        
        cluster = ecs.Cluster(self, 'myWebApp-cluster',
          capacity=dict(
            instance_type=ec2.InstanceType('t4g.micro'),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.ARM), # needed for Graviton2, works
            desired_capacity=1,
            task_drain_time=cdk.Duration.seconds(0)
          ),
          container_insights=True
        )


        # hosted_zone = HostedZone.from_hosted_zone_attributes(self, 'myTestZone', 
        #   hosted_zone_id='Z05838872A1WJ5MH2UI38',
        #   zone_name='jsr-ecs-ec2-test.com'
        # )

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedEc2Service.html
        load_balanced_service = ecs_patterns.ApplicationLoadBalancedEc2Service(self, 'myWebApp-service',
          # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/memory-management.html
          memory_limit_mib=512 , # TODO
          cluster=cluster,
          desired_count=1,
          max_healthy_percent=100,
          # https://github.com/aws/aws-cdk/issues/14107
          min_healthy_percent=0, # TODO daemon question
          service_name='myWebApp-service',
          task_image_options={
            'image': asset
          },
          # protocol=ApplicationProtocol.HTTPS,
          # redirect_http=True,
          # domain_name='alb.jsr-ecs-ec2-test.com',
          # domain_zone=hosted_zone,
          public_load_balancer=True
        )

        load_balanced_service.target_group.set_attribute('deregistration_delay.timeout_seconds', '0')
