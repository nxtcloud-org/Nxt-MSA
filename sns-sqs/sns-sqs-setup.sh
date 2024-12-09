#!/bin/bash

# 변수 설정
TOPIC_NAME="msa-topic-00"
QUEUE_NAME="msa-queue-00"
REGION="us-east-1"

echo "Creating SNS topic and SQS queue..."

# SNS 토픽 생성
TOPIC_ARN=$(aws sns create-topic --name $TOPIC_NAME --region $REGION --output text)
echo "SNS Topic created: $TOPIC_ARN"

# SQS 큐 생성
QUEUE_URL=$(aws sqs create-queue --queue-name $QUEUE_NAME --region $REGION --output text)
echo "SQS Queue created: $QUEUE_URL"


# 생성된 리소스 정보 파일 저장
cat > aws-resources.txt << EOF
SNS Topic ARN: $TOPIC_ARN
SQS Queue URL: $QUEUE_URL
EOF

echo "SNS, SQS 생성 완료 aws-resources.txt"