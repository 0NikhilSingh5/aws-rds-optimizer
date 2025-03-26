# RDS Parameter Manager: Dynamic Slow Query Logging

## Overview

During periods of high CPU usage, database performance often degrades due to slow-running queries, impacting application performance and user experience. Manually identifying and mitigating these issues is inefficient and time-consuming.

This workflow automates the process of enabling slow query logging only when CPU utilization crosses a defined threshold. Instead of keeping the `slow_query_log` parameter enabled at all times (which results in large log files), this system dynamically enables logging only when necessary using AWS Lambda, SNS, and CloudWatch Alarms.

### **Key Benefits**

1. **Immediate Response**: Automatically enables slow query logging when high CPU usage is detected, allowing rapid analysis.
2. **Operational Efficiency**: Eliminates manual intervention and monitoring, freeing up resources for critical tasks.
3. **Enhanced Performance**: Ensures optimal database performance by dynamically managing parameters.

## **Workflow**

![Workflow](./Screenshots/workflow.png)

---

## **Resource Setup**

### **1. Amazon RDS Setup**
If you don't have an RDS instance, follow this guide to create one:  
🔗 [AWS RDS Setup Guide](https://aws.amazon.com/getting-started/hands-on/create-mysql-db/)

### **2. CloudWatch Alarm Configuration**

1. **Navigate to AWS CloudWatch**  
   - Log in to the AWS Console and open the CloudWatch service.

2. **Create an Alarm**
   - Click on **Alarms** → **Create Alarm**

   ![Screenshot](./Screenshots/Untitled.png)

3. **Select Metric**
   - Click on **Select Metric**
   
   ![Screenshot](./Screenshots/Untitled%201.png)

4. **Choose RDS Metrics**
   - Select **RDS** → **DBInstanceIdentifier**
   
   ![Screenshot](./Screenshots/Untitled%202.png)
   
   ![Screenshot](./Screenshots/Untitled%203.png)

5. **Set CPU Utilization Threshold**
   - Choose **CPUUtilization** metric and define the threshold (e.g., **80%**).
   
   ![Screenshot](./Screenshots/Untitled%204.png)
   
   ![Screenshot](./Screenshots/Untitled%205.png)

6. **Configure SNS Notification**
   - In **Configure Actions**, select an **SNS Topic** (`my-database-high-cpu`).
   - *(If SNS is not yet created, you can modify the alarm later to include the topic.)*
   
   ![Screenshot](./Screenshots/Untitled%206.png)

7. **Name & Create Alarm**
   - Give a descriptive name and review the settings before creating the alarm.
   
   ![Screenshot](./Screenshots/Untitled%207.png)

---

## **3. Deploying AWS Lambda via Serverless Framework**

We will use the Serverless Framework to deploy the Lambda function and trigger it via SNS events.

### **Prerequisites**

🔹 Install & Configure AWS CLI  
- [Download AWS CLI](https://awscli.amazonaws.com/AWSCLIV2.msi)  
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/reference/configure/)

🔹 Install Serverless Framework  
- [Serverless Framework Setup](https://www.serverless.com/framework/docs-getting-started)

### **4. Create a New Serverless Project**

1. **Initialize Project**
   - Choose `AWS - Python - Starter`
   
   ![Screenshot](./Screenshots/Untitled%208.png)

2. **Name the Project** (e.g., `Auto-SlowQuery`)
   
   ![Screenshot](./Screenshots/Untitled%209.png)

3. **Modify handler.py**
   - Open `handler.py` and replace its content with the Lambda function script.
   - Code can be found [here](./rds_slow_query_parameter_toggle.py)
   
   ![Screenshot](./Screenshots/Untitled%2010.png)

4. **Update serverless.yml**
   ```yaml
   service: Auto-slowQuery
   
   frameworkVersion: '3'
   
   provider:
     name: aws
     runtime: python3.9
   
   functions:
     slow_query_logs:
       handler: handler.slow_query_logs
       events:
         - sns: my-database-high-cpu
   ```

### **5. Deploy Lambda Function**

Run the following command in the Serverless project directory:
```bash
deploy --stage production --region ap-south-1
```

![Deploy Screenshot](./Screenshots/deploy.png)

**Monitor Deployment Progress**  
Check the **CloudFormation** stack in AWS Console.

Once deployed, the Lambda function will be automatically triggered by the SNS event:

![Lambda Config Screenshot](./Screenshots/Untitled%2011.png)

### **6. Assign IAM Policy to Lambda Execution Role**

Attach the following policy to the Lambda execution role to allow it to modify RDS parameters:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:TagResource"
            ],
            "Resource": [
                "arn:aws:logs:ap-south-1:516978611867:log-group:/aws/lambda/Auto-slowQuery-production*:*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:ap-south-1:516978611867:log-group:/aws/lambda/Auto-slowQuery-production*:*:*"
            ],
            "Effect": "Allow"
        },
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Action": [
                "rds:DescribeDBParameterGroups",
                "rds:DescribeDBParameters",
                "rds:ModifyDBParameterGroup"
            ],
            "Resource": [
                "arn:aws:rds:ap-south-1:516978611867:pg:my-database-pg"
            ]
        }
    ]
}
```

---

## **Scope for Improvement**

1. **Advanced Slow Query Log Analysis**
   - Use tools like **pt-query-digest** (Percona Toolkit) or **mysqlslowdump** to analyze logs.
   - Save analyzed logs to **Amazon S3** and generate a **pre-signed URL** for secure sharing.

2. **High CPU Usage Process Export**
   - Extract high CPU usage processes from RDS instances.
   - Identify resource-intensive queries and optimize them.

This workflow significantly enhances database performance monitoring while reducing manual intervention, making it a scalable and efficient solution for production environments.

