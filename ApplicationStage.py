from aws_cdk.core import Construct, Stack, Stage, Environment, CfnOutput
from cdk_pipeline_ecs.ApplicationStack import ApplicationStack
from cdk_pipeline_ecs.DatabaseStack import DatabaseStack
from cdk_pipeline_ecs.WebServiceStack import WebServiceStack


class ApplicationStage(Stage):
    load_balancer_address: CfnOutput = None
    gateway_url: CfnOutput = None

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # db_stack = DatabaseStack(
        #     self, 
        #     "DatabaseStack"
        # )

        env = kwargs['env']

        app_stack = ApplicationStack(
            self, 
            "ApplicationStack",
            env=env
        )

        # web_service_stack = WebServiceStack(
        #     self, 
        #     "WebServiceStack", 
        #     db_stack.demo_table
        # )

        self.load_balancer_address = CfnOutput(
            app_stack, 
            "LbAddress",
            value=f"http://{app_stack.load_balancer_dns_name}"
        )

        # self.gateway_url = CfnOutput(
        #     web_service_stack, 
        #     "GatewayUrl",
        #     value=web_service_stack.gw_url
        # )
