from aws_cdk.core import Construct, Stack, Stage, Environment, CfnOutput 
from cdk_pipeline_ecs.AppStack import AppStack
from cdk_pipeline_ecs.DBStack import DBStack
from cdk_pipeline_ecs.WebServiceStack import WebServiceStack


class ApplicationStage(Stage):
    load_balancer_address: CfnOutput = None
    gateway_url: CfnOutput = None

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        db_stack = DBStack(self, "DBStack")

        app_stack = AppStack(self, "AppStack", db_stack.demo_table)

        web_service_stack = WebServiceStack(self, "WebServiceStack")

        self.load_balancer_address = CfnOutput(app_stack, "LbAddress",
            value=f"http://{app_stack.load_balancer_dns_name}")

        self.gateway_url = CfnOutput(app_stack, "GatewayUrl",
            value=web_service_stack.gw_url)