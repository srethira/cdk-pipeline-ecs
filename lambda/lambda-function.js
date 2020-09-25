const AWS = require('aws-sdk');

const dynamo = new AWS.DynamoDB();

exports.handler = async function(event) {
  console.log("request:", JSON.stringify(event, undefined, 2));
  var item = await dynamo.getItem({
    TableName: process.env.TABLE_NAME,
    Key:{
      first_name: {
        S: 'srikanth'
      }
    }
  }).promise();
  return {
    statusCode: 200,
    headers: { "Content-Type": "text/plain" },
    body: JSON.stringify({
      event: event,
      item,
    }),
  };
}