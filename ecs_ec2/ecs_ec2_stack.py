# based on https://blog.kylegalbraith.com/2019/10/24/how-to-run-docker-containers-via-aws-elastic-container-service/
from os import path

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import core as cdk


class EcsEc2Stack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Docker build
        this_dir = path.dirname(__file__)
        asset = ecs.ContainerImage.from_asset(path.join(this_dir, 'myWebApp'))

        # ECS cluster/resources
        cluster = ecs.Cluster(self, 'myWebApp-cluster',
          cluster_name='myWebApp-cluster'
        )

        # https://aws.amazon.com/ec2/graviton/
        # Free trial until June 30th 2021
        # but not sure how to use!
        cluster.add_capacity('myWebApp-scaling-group',
          instance_type=ec2.InstanceType('t2.micro'), # TODO 't4g.micro'
          desired_capacity=1,
          task_drain_time=cdk.Duration.seconds(0)
        )


        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedEc2Service.html
        load_balanced_service = ecs_patterns.ApplicationLoadBalancedEc2Service(self, 'myWebApp-service',
          # cpu=256, # TODO
          memory_limit_mib=1024, # TODO
          cluster=cluster,
          desired_count=1,
          max_healthy_percent=100,
          min_healthy_percent=0, # TODO daemon question
          service_name='myWebApp-service',
          task_image_options={
            "image": asset,
            "container_port": 80
          },
          public_load_balancer=True
        )

        cdk.CfnOutput(self, 'ClusterArn', value=load_balanced_service.cluster.cluster_arn)
        cdk.CfnOutput(self, 'DnsName', value=load_balanced_service.load_balancer.load_balancer_dns_name)
