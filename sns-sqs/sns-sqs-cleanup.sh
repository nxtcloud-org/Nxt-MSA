#!/bin/bash

# 변수 설정
TOPIC_NAME="your topic"
QUEUE_NAME="your queue"
REGION="us-east-1"

# 리소스 정보 파일에서 ARN 읽기
if [ -f aws-resources.txt ]; then
    TOPIC_ARN=$(grep "SNS Topic ARN:" aws-resources.txt | cut -d' ' -f4)
    QUEUE_URL=$(grep "SQS Queue URL:" aws-resources.txt | cut -d' ' -f4)
    SUBSCRIPTION_ARN=$(grep "Subscription ARN:" aws-resources.txt | cut -d' ' -f3)

    # 구독 삭제
    echo "Deleting SNS subscription..."
    aws sns unsubscribe --subscription-arn $SUBSCRIPTION_ARN

    # SNS 토픽 삭제
    echo "Deleting SNS topic..."
    aws sns delete-topic --topic-arn $TOPIC_ARN

    # SQS 큐 삭제
    echo "Deleting SQS queue..."
    aws sqs delete-queue --queue-url $QUEUE_URL

    # 리소스 정보 파일 삭제
    rm aws-resources.txt
    
    echo "Cleanup completed!"
else
    echo "aws-resources.txt not found. Please ensure resources exist."
fi