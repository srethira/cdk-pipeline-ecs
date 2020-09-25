from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as _apigw
)

class WebServiceStack(core.Stack):
    gw_url: core.CfnOutput = None

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bundling_options = core.BundlingOptions(image=_lambda.Runtime.NODEJS_12_X.bundling_docker_image,
            user="root",
            command=[
                'bash', '-c',
                'cp /asset-input/* /asset-output/ && cd /asset-output && npm test'
            ])
        source_code = _lambda.Code.from_asset('./lambda', bundling=bundling_options)

        # create lambda function
        db_lambda = _lambda.Function(self, "lambda-function",
            runtime=_lambda.Runtime.NODEJS_12_X,
            handler="lambda-function.handler",
            code=source_code
        )

        gw = _apigw.LambdaRestApi(self, "Gateway", 
            handler=db_lambda, 
            description="Endpoint for a simple Lambda-powered web service"
        )

        # add an output with a well-known name to read it from the integ tests
        self.gw_url = gw.url