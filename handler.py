'''  
This module uses the boto3 library to interact with Amazon RDS, and modify the parameters from the attached
parameter group.

Args:
  -event (dict): Dictionary containing information about the event that triggered the function.
  -context (LambdaContext): Context information about the invocation, including the function name,version, and ID.
'''

import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def slow_query_logs(event, context):
    """
    Modify slow query log parameter in RDS parameter group.
    
    Args:
        event (dict): Event data triggering the Lambda function
        context (LambdaContext): Lambda context information
    """
    try:
        # Initialize RDS client
        client = boto3.client("rds")
        
        # Configuration parameters
        param_group_name = "my-database-pg"
        param_name = "slow_query_log"
        
        # Retrieve current parameters
        parameters = []
        marker = None
        
        while True:
            # Describe DB parameters with optional marker
            describe_params = {
                "DBParameterGroupName": param_group_name
            }
            if marker:
                describe_params["Marker"] = marker
            
            response = client.describe_db_parameters(**describe_params)
            parameters.extend(response["Parameters"])
            
            # Check if there are more parameters to retrieve
            marker = response.get("Marker")
            if not marker:
                break
        
        # Find the current parameter value
        parameter_value = next(
            (param.get("ParameterValue", "0") 
             for param in parameters 
             if param["ParameterName"] == param_name),
            "0"
        )
        
        logger.info(f"Current parameter value: {parameter_value}")
        
        # Toggle parameter value
        new_value = "1" if parameter_value == "0" else "0"
        
        # Modify parameter group
        client.modify_db_parameter_group(
            DBParameterGroupName=param_group_name,
            Parameters=[
                {
                    "ParameterName": param_name,
                    "ParameterValue": new_value,
                    "ApplyMethod": "immediate",
                }
            ]
        )
        
        logger.info(f"Parameter {param_name} changed to: {new_value}")
        
        return {
            "statusCode": 200,
            "body": f"Successfully toggled {param_name} to {new_value}"
        }
    
    except Exception as e:
        logger.error(f"Error modifying RDS parameter: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
