# rds_parameter_automation
This repository contains an AWS Lambda function designed to automate the performance tuning of Amazon RDS instances. The Lambda function is triggered by an SNS topic in response to a CloudWatch alarm when CPU usage exceeds 90%. The script dynamically adjusts the slow_query_log parameter to help identify and mitigate performance bottlenecks.
