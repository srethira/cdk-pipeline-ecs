from aws_cdk.core import Construct, Stack, Stage, Environment, CfnOutput 
from cdk_pipeline_ecs.AppStack import AppStack
from cdk_pipeline_ecs.DBStack import DBStack


class ApplicationStage(Stage):
    load_balancer_address: CfnOutput = None

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        db_stack = DBStack(self, "DBStack")

        app_stack = AppStack(self, "AppStack", db_stack.demo_table)

        self.load_balancer_address = CfnOutput(app_stack, "LbAddress",
            value=f"http://{app_stack.load_balancer_dns_name}")