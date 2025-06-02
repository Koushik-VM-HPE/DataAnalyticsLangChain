import boto3
import json
import os

dynamodb = boto3.resource(
    'dynamodb',
aws_access_key_id=os.getenv('AWS_DB_ACCESS_KEY_ID'),
aws_secret_access_key=os.getenv('AWS_DB_SECRET_ACCESS_KEY'),
aws_session_token=os.getenv('AWS_DB_SESSION_TOKEN'),
region_name='us-east-1'
)
TableName = os.getenv('AWS_DB_TABLE_NAME', 'devex_ocm_intg')  
table = dynamodb.Table(TableName)  # type: ignore

def scan_table():
    items = []
    response = table.scan()
    items.extend(response['Items'])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    return items

data = scan_table()

# Save to JSON
with open('dynamodb_data.json', 'w') as f:
    json.dump(data, f, default=str)
