import json
import os

def handler(event, context):
    """
    Simple Lambda function that responds to API Gateway requests.
    Can be extended to interact with DynamoDB and S3.
    """
    
    # Get environment variables
    table_name = os.environ.get('DYNAMODB_TABLE', 'Not configured')
    bucket_name = os.environ.get('S3_BUCKET', 'Not configured')
    
    # Parse the request
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    # Simple response
    response_body = {
        'message': 'Hello from Pulumi Lambda!',
        'path': path,
        'method': method,
        'dynamodb_table': table_name,
        's3_bucket': bucket_name,
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(response_body),
    }