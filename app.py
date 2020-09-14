#!/usr/bin/env python3

from aws_cdk import core

from cdk_pipeline_ecs.cdk_pipeline_ecs_stack import CdkPipelineEcsStack


app = core.App()
CdkPipelineEcsStack(app, "cdk-pipeline-ecs")

app.synth()
