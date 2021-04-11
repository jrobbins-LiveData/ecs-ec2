# based on https://blog.kylegalbraith.com/2019/10/24/how-to-run-docker-containers-via-aws-elastic-container-service/
from os import path

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import core as cdk


class EcsEc2Stack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Docker build
        asset = ecs.ContainerImage.from_asset(path.join(path.dirname(__file__), 'myWebApp'))

        # ECS cluster/resources

        # NOTE 't4g.micro' is a Graviton2 EC2 type
        # https://aws.amazon.com/ec2/graviton/
        # Free trial until June 30th 2021
        
        cluster = ecs.Cluster(self, 'myWebApp-cluster',
          capacity=dict(
            instance_type=ec2.InstanceType('t4g.micro'),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.ARM), # needed for Graviton2
            desired_capacity=1,
            task_drain_time=cdk.Duration.seconds(0)
          ),
          container_insights=True
        )

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedEc2Service.html
        load_balanced_service = ecs_patterns.ApplicationLoadBalancedEc2Service(self, 'myWebApp-service',
          memory_limit_mib=512 , # TODO
          cluster=cluster,
          desired_count=1,
          max_healthy_percent=100,
          min_healthy_percent=0, # TODO daemon question
          service_name='myWebApp-service',
          task_image_options={
            "image": asset
          },
          public_load_balancer=True
        )
