import boto3
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


# Configure AWS CloudWatch Logs
cloudwatch_logs_group_name = "book-app-logs"
cloudwatch_logs_stream_name = "demo-log-stream"


# Initialize AWS CloudWatch Logs client
cloudwatch_logs_client = boto3.client("logs")

# Function to log data to CloudWatch Logs


def log_to_cloudwatch(data):
    try:
        cloudwatch_logs_client.create_log_group(logGroupName=cloudwatch_logs_group_name)
    except cloudwatch_logs_client.exceptions.ResourceAlreadyExistsException:
        pass

    try:
        cloudwatch_logs_client.create_log_stream(
            logGroupName=cloudwatch_logs_group_name, logStreamName=cloudwatch_logs_stream_name
        )
    except cloudwatch_logs_client.exceptions.ResourceAlreadyExistsException:
        pass

    log_event = {
        "logGroupName": cloudwatch_logs_group_name,
        "logStreamName": cloudwatch_logs_stream_name,
        "logEvents": [
            {
                "timestamp": int(time.time() * 1000),
                "message": str(data),
            },
        ],
    }
    cloudwatch_logs_client.put_log_events(**log_event)
