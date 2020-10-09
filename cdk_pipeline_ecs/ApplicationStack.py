from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ssm as ssm,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elb_targets,
    aws_lambda as _lambda,
    aws_codedeploy as codedeploy,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam
)
import os.path
import pathlib


class ApplicationStack(core.Stack):
    load_balancer_dns_name: core.CfnOutput = None

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        env = kwargs['env']

        work_dir = pathlib.Path(__file__).parents[1]

        # These below steps allows to reuse ecs cluster which is aleady creatd by shared stack

        # Get cluster name from ssm parameter
        cluster_name = ssm.StringParameter.from_string_parameter_name(
            self, 
            "GetClusterName",
            string_parameter_name="/dev/compute/container/ecs-cluster-name"
        ).string_value

        vpc_az = ssm.StringListParameter.from_string_list_parameter_name(
            self, 
            "GetVpcAz",
            string_list_parameter_name="/dev/network/vpc/vpc-az"
        ).string_list_value

        # using string instead of stringlist because of subnets parsing issue
        vpc_public_subnets_1 = ssm.StringParameter.from_string_parameter_name(
            self, 
            "GetVpcPublicSubnets1",
            string_parameter_name="/dev/network/vpc/vpc-public-subnets-1"
        ).string_value

        vpc_public_subnets_2 = ssm.StringParameter.from_string_parameter_name(
            self, 
            "GetVpcPublicSubnets2",
            string_parameter_name="/dev/network/vpc/vpc-public-subnets-2"
        ).string_value

        vpc_id = ssm.StringParameter.from_string_parameter_name(
            self, 
            "GetVpcId",
            string_parameter_name="/dev/network/vpc/vpc-id"
        ).string_value

        ec2_vpc = ec2.Vpc.from_vpc_attributes(
            self, 
            "GetVpc",
            availability_zones=vpc_az,
            vpc_id=vpc_id,
            public_subnet_ids=[vpc_public_subnets_1, vpc_public_subnets_2]
        )

        # Get security group id from ssm parameter
        security_group_id = ssm.StringParameter.from_string_parameter_name(
            self, 
            "GetSgId",
            string_parameter_name="/dev/network/vpc/security-group-id"
        ).string_value

        # Get security group from lookup
        ec2_sgp = ec2.SecurityGroup.from_security_group_id(
            self, 
            "GetSgp",
            security_group_id=security_group_id
        )

        # # myDateTimeFunction lambda function
        # my_datetime_lambda = _lambda.Function(
        #     self, 
        #     "my-datetime",
        #     runtime=_lambda.Runtime.NODEJS_12_X,
        #     handler="myDateTimeFunction.handler",
        #     code=_lambda.Code.asset("./lambda"),
        #     current_version_options=_lambda.VersionOptions(
        #         removal_policy=core.RemovalPolicy.RETAIN, 
        #         retry_attempts=1
        #     )
        # )

        # my_datetime_lambda.add_to_role_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=["lambda:InvokeFunction"],
        #         resources=["*"]
        #     )
        # )

        # # beforeAllowTraffic lambda function
        # pre_traffic_lambda = _lambda.Function(
        #     self, 
        #     "pre-traffic",
        #     runtime=_lambda.Runtime.NODEJS_12_X,
        #     handler="beforeAllowTraffic.handler",
        #     code=_lambda.Code.asset(
        #         "./lambda"
        #     ),
        #     environment=dict(
        #         NewVersion=my_datetime_lambda.current_version.function_arn
        #     )
        # )

        # pre_traffic_lambda.add_to_role_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=["codedeploy:PutLifecycleEventHookExecutionStatus"],
        #         resources=["*"]
        #     )
        # )

        # pre_traffic_lambda.add_to_role_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=["lambda:InvokeFunction"],
        #         resources=["*"]
        #     )
        # )

        # # afterAllowTraffic lambda function
        # post_traffic_lambda = _lambda.Function(
        #     self, 
        #     "post-traffic",
        #     runtime=_lambda.Runtime.NODEJS_12_X,
        #     handler="afterAllowTraffic.handler",
        #     code=_lambda.Code.asset(
        #         "./lambda"
        #     ),
        #     environment=dict(
        #         NewVersion=my_datetime_lambda.current_version.function_arn
        #     )
        # )

        # post_traffic_lambda.add_to_role_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=["codedeploy:PutLifecycleEventHookExecutionStatus"],
        #         resources=["*"]
        #     )
        # )

        # post_traffic_lambda.add_to_role_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=["lambda:InvokeFunction"],
        #         resources=["*"]
        #     )
        # )

        # # create a cloudwatch event rule
        # rule = events.Rule(
        #     self, 
        #     "CanaryRule",
        #     schedule=events.Schedule.expression(
        #         "rate(10 minutes)"
        #     ),
        #     targets=[events_targets.LambdaFunction(
        #         my_datetime_lambda.current_version
        #     )],

        # )

        # # create a cloudwatch alarm based on the lambda erros metrics
        # alarm = cloudwatch.Alarm(
        #     self, 
        #     "CanaryAlarm",
        #     metric=my_datetime_lambda.current_version.metric_invocations(),
        #     threshold=0,
        #     evaluation_periods=2,
        #     datapoints_to_alarm=2,
        #     treat_missing_data=cloudwatch.TreatMissingData.IGNORE,
        #     period=core.Duration.minutes(5),
        #     alarm_name="CanaryAlarm"
        # )

        # lambda_deployment_group = codedeploy.LambdaDeploymentGroup(
        #     self, 
        #     "datetime-lambda-deployment",
        #     alias=my_datetime_lambda.current_version.add_alias(
        #         "live"
        #     ),
        #     deployment_config=codedeploy.LambdaDeploymentConfig.ALL_AT_ONCE,
        #     alarms=[alarm],
        #     auto_rollback=codedeploy.AutoRollbackConfig(
        #         deployment_in_alarm=True
        #     ),
        #     pre_hook=pre_traffic_lambda,
        #     post_hook=post_traffic_lambda
        # )

        # Create Application LoadBalancer
        lb = elbv2.ApplicationLoadBalancer(
            self, 
            "LB",
            vpc=ec2_vpc,
            internet_facing=True
        )

        lb_tg_blue = elbv2.ApplicationTargetGroup(
            self,
            "ALBTargetGroupBlue",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            vpc=ec2_vpc
        )

        lb_tg_green = elbv2.ApplicationTargetGroup(
            self,
            "ALBTargetGroupGreen",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            vpc=ec2_vpc
        )

        # Add listener to the LB
        listener = lb.add_listener(
            "ALBListenerProdTraffic",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            open=True,
            default_action=elbv2.ListenerAction(
                action_json=elbv2.CfnListener.ActionProperty(
                    type="forward",
                    forward_config=elbv2.CfnListener.ForwardConfigProperty(
                        target_groups=[elbv2.CfnListener.TargetGroupTupleProperty(
                            target_group_arn=lb_tg_blue.load_balancer_arns,
                            weight=1
                        )]
                    )
                )
            )
        )

        # Fargate Service
        blue_task_definition = ecs.FargateTaskDefinition(
            self,
            "BlueTaskDefinition",
            memory_limit_mib=512,
            cpu=256,
            family="ecs-demo"
        )

        container = blue_task_definition.add_container(
            "web",
            image=ecs.ContainerImage.from_asset(
                os.path.join(
                    work_dir,
                    "container"
                )
            ),
            # Build custom health check for your application specific
            # and add them here. Ex: Pingcheck, Database etc.
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "echo"]
            ),
            # environment=dict(name="latest")
        )

        port_mapping = ecs.PortMapping(
            container_port=8000,
            protocol=ecs.Protocol.TCP
        )

        container.add_port_mappings(
            port_mapping
        )

        # Pass vpc, sgp and ecs cluster name to get ecs cluster info
        ecs_cluster = ecs.Cluster.from_cluster_attributes(
            self, 
            "GetEcsCluster",
            cluster_name=cluster_name,
            vpc=ec2_vpc,
            security_groups=[ec2_sgp]
        )

         # Create Fargate Service
        # Current limitation: Blue/Green deployment
        # https://github.com/aws/aws-cdk/issues/1559
        service = ecs.FargateService(
            self, 
            "Service",
            cluster=ecs_cluster,
            task_definition=blue_task_definition,
            assign_public_ip=True,
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.EXTERNAL
            ),
            desired_count=2,
            min_healthy_percent=50
        )

        self.add_transform(
            "AWS::CodeDeployBlueGreen"
        )

        # core.CfnHook(
        #     self,
        #     "EcsHook",
        #     type="AWS::CodeDeploy::BlueGreen"
        # )

        ecs_task_execution_role=iam.Role(self,
            "ECSTaskExecutionRole",
            assumed_by=iam.ServicePrincipal(
                service="ecs-tasks.amazonaws.com"
            ),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                managed_policy_name="AmazonECSTaskExecutionRolePolicy"
            )]
        )

        core.CfnCodeDeployBlueGreenHook(
            self,
            "CodeDeployBlueGreenHook",
            applications=[core.CfnCodeDeployBlueGreenApplication(
                ecs_attributes=core.CfnCodeDeployBlueGreenEcsAttributes(
                    task_definitions=["BlueTaskDefinition","GreenTaskDefinition"],
                    task_sets=["BlueTaskSet","GreenTaskSet"],
                    traffic_routing=core.CfnTrafficRouting(
                        prod_traffic_route=core.CfnTrafficRoute(
                            logical_id=listener.node.default_child.__getattribute__("logical_id"),
                            type="AWS::ElasticLoadBalancingV2::Listener"
                        ),
                        test_traffic_route=core.CfnTrafficRoute(
                            logical_id=listener.node.default_child.__getattribute__("logical_id"),
                            type="AWS::ElasticLoadBalancingV2::Listener"
                        ),
                        target_groups=["ALBTargetGroupBlue","ALBTargetGroupGreen"]
                    )
                ),
                target=core.CfnCodeDeployBlueGreenApplicationTarget(
                    logical_id="ServiceD69D759B",
                    type="AWS::ECS::Service"
                )
            )],
            traffic_routing_config=core.CfnTrafficRoutingConfig(
                type=core.CfnTrafficRoutingType.TIME_BASED_CANARY,
                time_based_canary=core.CfnTrafficRoutingTimeBasedCanary(
                  bake_time_mins=5,
                  step_percentage=15  
                )
            ),
            service_role=ecs_task_execution_role.role_name,
        )

        blue_task_set=ecs.CfnTaskSet(
            self,
            "BlueTaskSet",
            cluster=ecs_cluster.cluster_name,
            launch_type="FARGATE",
            service=service.service_name,
            task_definition="BlueTaskDefinition",
            load_balancers=[ecs.CfnTaskSet.LoadBalancerProperty(
                container_name="DemoApp",
                container_port=80,
                target_group_arn=lb_tg_blue.load_balancer_arns
            )]
        )

        ecs.CfnPrimaryTaskSet(
            self,
            "PrimaryTaskSet",
            cluster=ecs_cluster.cluster_name,
            service=service.service_name,
            task_set_id="BlueTaskSet",
        )

        # # Default to Lambda
        # listener.add_targets(
        #     "Lambda",
        #     targets=[elb_targets.LambdaTarget(
        #         my_datetime_lambda
        #     )]
        # )

        # # Additionally route to container
        # listener.add_targets(
        #     "Fargate", 
        #     port=8000,
        #     path_pattern="/container",
        #     priority=10,
        #     targets=[service]
        # )

        # add an output with a well-known name to read it from the integ tests
        self.load_balancer_dns_name = lb.load_balancer_dns_name			