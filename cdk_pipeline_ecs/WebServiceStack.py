from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as _apigw
)

class WebServiceStack(core.Stack):
    gw_url: core.CfnOutput = None

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create lambda function
        db_lambda = _lambda.Function(self, "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_6,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.asset("./lambda")
        )

        gw = _apigw.LambdaRestApi(self, "Gateway", 
            handler=db_lambda, 
            description="Endpoint for a simple Lambda-powered web service"
        )

        # add an output with a well-known name to read it from the integ tests
        self.gw_url = gw.url