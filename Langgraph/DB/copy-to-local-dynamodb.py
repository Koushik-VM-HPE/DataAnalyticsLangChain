import boto3
import json

# Connect to local DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1',
                          endpoint_url='http://localhost:8000')
table = dynamodb.Table('devex_ocm_local') # type: ignore

# Load data from the JSON file (exported from AWS DynamoDB)
with open('dynamodb_data.json') as f:
    items = json.load(f)

# Batch write to local DynamoDB
with table.batch_writer() as batch:
    for item in items:
        batch.put_item(Item=item)

print("Data imported successfully.")

# Some commands to verify 
#table creation:
# aws dynamodb describe-table --table-name devex_ocm_local --endpoint-url http://localhost:8000
# aws dynamodb list-tables --endpoint-url http://localhost:8000
# aws dynamodb scan --table-name devex_ocm_local --endpoint-url http://localhost:8000
