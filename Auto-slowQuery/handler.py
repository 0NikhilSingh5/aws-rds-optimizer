import boto3


def slow_query_logs(event, context):
    client = boto3.client("rds")
    param_group_name = "my-database-pg"
    param_name = "slow_query_log"

    marker = "String"
    parameters = []

    while True:
        # I
        response = client.describe_db_parameters(
            DBParameterGroupName=param_group_name, Marker=marker
        )
        parameters.extend(response["Parameters"])
        # II
        if "Marker" in response:
            marker = response["Marker"]
        else:
            break

    parameter_value = None
    for parameter in parameters:
        if parameter["ParameterName"] == param_name:
            parameter_value = parameter.get("ParameterValue", "Not set")
            break

    if parameter_value is not None:
        print(f"The value of parameter '{param_name}' is '{parameter_value}'.")
    else:
        print(
            f"Parameter '{param_name}' not found in parameter group '{param_group_name}'."
        )

    if parameter_value == "0":
        response = client.modify_db_parameter_group(
            DBParameterGroupName="my-database-pg",
            Parameters=[
                {
                    "ParameterName": param_name,
                    "ParameterValue": "1",
                    "ApplyMethod": "immediate",
                },
            ],
        )
        print(
            f"Parameter {param_name} in parameter group {param_group_name}is changed to: 1"
        )

    elif parameter_value == "1":
        response = client.modify_db_parameter_group(
            DBParameterGroupName="my-database-pg",
            Parameters=[
                {
                    "ParameterName": param_name,
                    "ParameterValue": "0",
                    "ApplyMethod": "immediate",
                },
            ],
        )
        print(
            f"Parameter {param_name} in parameter group {param_group_name}is changed to 0 successfully"
        )

        return {"statusCode": 200}
