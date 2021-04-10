# based on https://blog.kylegalbraith.com/2019/10/24/how-to-run-docker-containers-via-aws-elastic-container-service/
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import core as cdk


class EcsEc2Stack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR repository
        repository = ecr.Repository(self, 'myWebApp',
          repository_name='myWebApp'
        )

        # ECS cluster/resources
        cluster = ecs.Cluster(self, 'myWebApp-cluster',
          cluster_name='myWebApp-cluster'
        )

        # https://aws.amazon.com/ec2/graviton/
        # Free trial until June 30th 2021
        cluster.add_capacity('myWebApp-scaling-group',
          instance_type=ec2.InstanceType('t4g.micro'),
          desired_capacity=1
        )

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedEc2Service.html
        load_balanced_service = ecs_patterns.ApplicationLoadBalancedEc2Service(self, 'myWebApp-service',
          cpu=256,
          memory_limit_mib=512,
          cluster=cluster,
          desired_count=1,
          service_name='myWebApp-service',
          task_image_options={
            "image": ecs.ContainerImage.from_ecr_repository(repository),
            "container_port": 8080,
          },
          public_load_balancer=True
        )

        cdk.CfnOutput(self, 'ClusterArn', value=load_balanced_service.cluster.cluster_arn)
        cdk.CfnOutput(self, 'DnsName', value=load_balanced_service.load_balancer.load_balancer_dns_name)
