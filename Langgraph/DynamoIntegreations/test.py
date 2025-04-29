from typing import Dict
from dynamoDBUtils import DynamoDBUtils
from boto3.dynamodb.conditions import Attr

# Replace with an actual table name in your DynamoDB
TABLE_NAME = "devex_ocm_intg"

def test_scan():
    print("\n🔍 Testing Scan Method...")
    filter = {"clusterName": Attr("clusterName").eq("st0322")}
    items = DynamoDBUtils.scan(table_name=TABLE_NAME, limit=5, filter=filter)
    print(f" Scan Result ({len(items)} items):")
    for item in items:
        print(item)

def test_query():
    print("\n🔍 Testing Query Method...")

    # Replace these with actual keys in your DynamoDB table
    HASH_KEY = "tenantID_siteID"  # Adjust as per your schema
    HASH_VALUE = "c96iblviqa4b4joq1f2g_e1d8cecd-a7fb-45fb-a245-965e0f961ff6"   # Sample user_id

    items = DynamoDBUtils.query(table_name=TABLE_NAME, hash_key=HASH_KEY, hash_value=HASH_VALUE, limit=3)
    
    print(f" Query Result ({len(items)} items):")
    for item in items:
        print(item)

if __name__ == "__main__":
    print("\n Running DynamoDB Utility Tests...")
    test_scan()
    # test_query()
    print("\n All tests completed.")
