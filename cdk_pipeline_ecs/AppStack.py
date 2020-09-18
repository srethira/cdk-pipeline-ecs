from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ssm as ssm,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elb_targets
)


class AppStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Fargate Service
        task_definition = ecs.FargateTaskDefinition(
            self, 
            "TaskDef", 
            memory_limit_mib=512, 
            cpu=256
        )

        container = task_definition.add_container(
            "web", 
            image=ecs.ContainerImage.from_registry("nginx:latest")
        )

        port_mapping = ecs.PortMapping(
            container_port=8000,
            protocol=ecs.Protocol.TCP
        )

        container.add_port_mappings(port_mapping)

        # These below steps allows to reuse ecs cluster which is aleady creatd by shared stack

        # TODO Get cluster name from ssm parameter
        cluster_name=ssm.StringParameter.from_string_parameter_name(
            self, "GetClusterName",
            string_parameter_name="/dev/compute/container/ecs-cluster-name"
        )
        # cluster_name="Prod-SharedStack-ClusterEB0386A7-iYv2Qrkn50ns"

        # TODO Get vpc from ssm parameter
        # vpc_name="shared-pipeline/Prod/SharedStack/Vpc"

        # Get vpc from lookup attributes
        # ec2_vpc = ec2.Vpc.from_lookup(
        #     self, "GetVpc", 
        #     vpc_name=vpc_name
        # )

        vpc_az = ssm.StringParameter.from_string_parameter_name(
            self, "GetVpcAz",
            string_parameter_name="/dev/network/vpc/vpc-az"
        )

        vpc_id = ssm.StringParameter.from_string_parameter_name(
            self, "GetVpcId",
            string_parameter_name="/dev/network/vpc/vpc-id"
        )

        ec2_vpc = ec2.Vpc.from_vpc_attributes(
            self, "GetVpc",
            availability_zones=vpc_az,
            vpc_id=vpc_id
        )

        # TODO Get security group id from ssm parameter
        security_group_id=ssm.StringParameter.from_string_parameter_name(
            self, "GetSgId",
            string_parameter_name="/dev/network/vpc/security-group-id"
        )
        # security_group_id="sg-056caf7401bfe8493"

        # Get security group from lookup
        ec2_sgp = ec2.SecurityGroup.from_security_group_id(
            self, "GetSgp", 
            security_group_id=security_group_id
        )

        # Pass vpc, sgp and ecs cluster name to get ecs cluster info
        ecs_cluster = ecs.Cluster.from_cluster_attributes(
            self,"GetEcsCluster",
            cluster_name=cluster_name,
            vpc=ec2_vpc,
            security_groups=[ec2_sgp]
        )

        # Create Fargate Service
        service = ecs.FargateService(self, "Service", 
            cluster=ecs_cluster,
            task_definition=task_definition
        )

        # Create Application LoadBalancer
        lb = elbv2.ApplicationLoadBalancer(self, "LB", 
            vpc=ec2_vpc, 
            internet_facing=True
        )

        # Add listener to the LB
        listener = lb.add_listener("PublicListener", 
            port=80, 
            open=True
        )

        # Route to container
        listener.add_targets("Fargate",port=8000,
            # path_pattern="/container",
            # priority=10,
            targets=[service]
        )    