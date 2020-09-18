from aws_cdk.core import Construct, Stack, Stage, Environment
from cdk_pipeline_ecs.AppStack import AppStack

class ApplicationStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        app_stack = AppStack(self, "AppStack")