from aws_cdk.core import Stack, StackProps, Construct, SecretValue, Environment
from aws_cdk.pipelines import CdkPipeline, SimpleSynthAction
from ApplicationStage import ApplicationStage

import aws_cdk.aws_codepipeline as codepipeline
import aws_cdk.aws_codepipeline_actions as codepipeline_actions
import os



# Stack to hold the pipeline
#
class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        github_token_secret_name = os.getenv('GITHUB_TOKEN', '')

        pipeline = CdkPipeline(self, "Pipeline",
            pipeline_name="MyAppPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=codepipeline_actions.GitHubSourceAction(
                action_name="GitHub",
                output=source_artifact,
                oauth_token=SecretValue.secrets_manager(github_token_secret_name),
                trigger=codepipeline_actions.GitHubTrigger.POLL,
                owner="srethira",
                repo="cdk-pipeline-ecs",
                branch="ecs-ru"
            ),
            synth_action=SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command="npm install -g aws-cdk && pip install -r requirements.txt",
                # build_command="mvn package",
                synth_command="cdk synth",
                copy_environment_variables=["GITHUB_TOKEN"]
            )
        )

        # Do this as many times as necessary with any account and region
        # Account and region may be different from the pipeline's.
        pipeline.add_application_stage(ApplicationStage(self, 'Prod',
            env=Environment(account="462864815626", region="us-west-2")))