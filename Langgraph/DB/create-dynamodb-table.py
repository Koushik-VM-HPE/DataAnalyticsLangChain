import boto3

# Connect to local DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-west-2',
                          endpoint_url='http://localhost:8000')

# Define table schema
table_name = 'devex_ocm_local'
key_schema = [
    {
        'AttributeName': 'tenantID_siteID',  # Replace with your partition key
        'KeyType': 'HASH'  # Partition key
    },
    {
        'AttributeName': 'clusterID',  # Replace with your sort key (if you have one)
        'KeyType': 'RANGE'  # Sort key
    }
]

attribute_definitions = [
    {
        'AttributeName': 'tenantID_siteID',  # Replace with your partition key
        'AttributeType': 'S'  # 'S' for string, 'N' for number, 'B' for binary
    },
    {
        'AttributeName': 'clusterID',  # Replace with your sort key (if you have one)
        'AttributeType': 'S'  # 'S' for string, 'N' for number, 'B' for binary
    }
]

provisioned_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}

# Create table
table = dynamodb.create_table( # type: ignore
    TableName=table_name,
    KeySchema=key_schema,
    AttributeDefinitions=attribute_definitions,
    ProvisionedThroughput=provisioned_throughput
)

print(f"Table '{table_name}' creation started...")

# Wait for the table to be created
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
print(f"Table '{table_name}' created successfully!")
