from aws_cdk.core import Construct, Stack, Stage, Environment, CfnOutput 
from cdk_pipeline_ecs.AppStack import AppStack

class ApplicationStage(Stage):
    load_balancer_address: CfnOutput = None

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        app_stack = AppStack(self, "AppStack")

        self.load_balancer_address = CfnOutput(app_stack, "LbAddress",
            value=f"http://{app_stack.load_balancer_dns_name}")