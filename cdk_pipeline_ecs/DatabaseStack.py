
from aws_cdk import (
    core,
    aws_dynamodb
)

class DatabaseStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # create dynamo table
        self.demo_table = aws_dynamodb.Table(
            self, "demo_table",
            partition_key=aws_dynamodb.Attribute(
                name="first_name",
                type=aws_dynamodb.AttributeType.STRING
            )
        )
