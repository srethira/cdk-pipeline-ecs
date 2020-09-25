from aws_cdk.core import Stack, StackProps, Construct, SecretValue, Environment
from aws_cdk.pipelines import CdkPipeline, SimpleSynthAction, ShellScriptAction
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

        pipeline = CdkPipeline(
            self, 
            "Pipeline",
            pipeline_name="MyAppPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=codepipeline_actions.GitHubSourceAction(
                action_name="GitHub",
                output=source_artifact,
                oauth_token=SecretValue.secrets_manager(
                    github_token_secret_name
                ),
                trigger=codepipeline_actions.GitHubTrigger.POLL,
                owner="srethira",
                repo="cdk-pipeline-ecs",
                branch="lambda-bg"
            ),
            # Current limitation: generate CodeBuild reports within @aws-cdk/cdk-pipelines
            # https://github.com/aws/aws-cdk/issues/10464
            synth_action=SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                # enable privileged mode for docker-in-docker (for asset bundling)
                environment=dict(
                    privileged=True
                ),
                install_command="pipeline/bin/install.sh",
                build_command="python -m unittest test/test_*",
                synth_command="cdk synth",
                copy_environment_variables=["GITHUB_TOKEN"]
            )
        )

        # Do this as many times as necessary with any account and region for testing
        # Account and region may be different from the pipeline's.
        test = ApplicationStage(
            self, 
            'Testing',
            env=Environment(
                account="462864815626", 
                region="us-west-1"
            )
        )

        test_stage = pipeline.add_application_stage(
            test
        )

        test_stage.add_actions(
            ShellScriptAction(
                action_name='validate', 
                commands=['curl -Ssf $ENDPOINT_URL/container'],
                use_outputs=dict(
                    ENDPOINT_URL=pipeline.stack_output(
                        test.load_balancer_address
                    )
                )
            )
        )

        test_stage.add_actions(
            ShellScriptAction(
                action_name='integration', 
                commands=['python -m unittest test/test_*'],
                additional_artifacts=[source_artifact]
            )
        )

        # Do this as many times as necessary with any account and region for prod
        prod = ApplicationStage(
            self, 
            'Prod',
            env=Environment(
                account="462864815626", 
                region="us-west-2"
            )
        )

        prod_stage = pipeline.add_application_stage(
            prod
        )

        prod_stage.add_actions(
            ShellScriptAction(
                action_name='validate', 
                commands=['curl -Ssf $ENDPOINT_URL/container'],
                use_outputs=dict(
                    ENDPOINT_URL=pipeline.stack_output(
                        prod.load_balancer_address
                    )
                )
            )
        )

        prod_stage.add_actions(
            ShellScriptAction(
                action_name='integration', 
                commands=['python -m unittest test/test_*'],
                additional_artifacts=[source_artifact]
            )
        )
