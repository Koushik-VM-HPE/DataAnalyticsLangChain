import boto3, os
import boto3.dynamodb
import boto3.dynamodb.conditions
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError
from typing import Dict, Any, List, Optional
from boto3.dynamodb.conditions import Attr


load_dotenv()

# Initialize DynamoDB resource
db_client = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_DB_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_DB_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DB_REGION')
)
class DynamoDBUtils:
    @staticmethod
    def scan(table_name: str, filter: Optional[dict] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]: # type: ignore
        """
        Scan a given table with an optional filter expression and limit.
        """
        try:
            table = db_client.Table(table_name) # type: ignore
            scan_kwargs = {}

            if filter:
                filter_expression = None
                for attr_name, condition in filter.items():
                    if filter_expression:
                        filter_expression &= condition
                    else:
                        filter_expression = condition
                scan_kwargs["FilterExpression"] = filter_expression

            items = []
            last_evaluated_key = None

            while True:
                if last_evaluated_key:
                    scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

                response = table.scan(**scan_kwargs)
                items.extend(response.get("Items", []))

                # Stop when we reach the desired limit
                if limit and len(items) >= limit:
                    return items[:limit]  # Ensure we return exactly `limit` items

                last_evaluated_key = response.get("LastEvaluatedKey")

                # Stop if there are no more items to fetch
                if not last_evaluated_key:
                    break

            return items
        except (BotoCoreError, ClientError) as e:
            print(f"Error scanning table {table_name}: {str(e)}")
            return []



    @staticmethod
    def query(table_name: str, hash_key: str, hash_value: Any, range_key: Optional[str] = None, range_value: Optional[Any] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query a given table using the hash key and optional range key.
        """
        try:
            table = db_client.Table(table_name) # type: ignore
            key_condition = boto3.dynamodb.conditions.Key(hash_key).eq(hash_value)

            if range_key and range_value:
                key_condition = boto3.dynamodb.conditions.And(key_condition, boto3.dynamodb.conditions.Key(range_key).eq(range_value))

            query_kwargs = {"KeyConditionExpression": key_condition}

            if limit:
                query_kwargs["Limit"] = int(limit) # type: ignore

            response = table.query(**query_kwargs)
            return response.get("Items", [])
        except (BotoCoreError, ClientError) as e:
            print(f"Error querying table {table_name}: {str(e)}")
            return []


    # @staticmethod
    # def put_item(table_name: str, item: Dict[str, Any]) -> bool:
    #     """
    #     Insert a new item into a given table.
    #     """
    #     try:
    #         table = db_client.Table(table_name)
    #         table.put_item(Item=item)
    #         return True
    #     except (BotoCoreError, ClientError) as e:
    #         print(f"Error putting item into table {table_name}: {str(e)}")
    #         return False

    # @staticmethod
    # def patch_item(table_name: str, key: Dict[str, Any], updates: Dict[str, Any]) -> bool:
    #     """
    #     Update an existing item in a given table.
    #     """
    #     try:
    #         table = db_client.Table(table_name)
    #         update_expression = "SET " + ", ".join(f"{k} = :{k}" for k in updates.keys())
    #         expression_values = {f":{k}": v for k, v in updates.items()}

    #         table.update_item(
    #             Key=key,
    #             UpdateExpression=update_expression,
    #             ExpressionAttributeValues=expression_values
    #         )
    #         return True
    #     except (BotoCoreError, ClientError) as e:
    #         print(f"Error updating item in table {table_name}: {str(e)}")
    #         return False