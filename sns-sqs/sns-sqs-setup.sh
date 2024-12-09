#!/bin/bash

# 변수 설정
TOPIC_NAME="your topic"
QUEUE_NAME="your queue"
REGION="us-east-1"

echo "Creating SNS topic and SQS queue..."

# SNS 토픽 생성
TOPIC_ARN=$(aws sns create-topic --name $TOPIC_NAME --region $REGION --output text)
echo "SNS Topic created: $TOPIC_ARN"

# SQS 큐 생성
QUEUE_URL=$(aws sqs create-queue --queue-name $QUEUE_NAME --region $REGION --output text)
echo "SQS Queue created: $QUEUE_URL"

# SQS Queue ARN 가져오기
QUEUE_ARN=$(aws sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)
echo "SQS Queue ARN: $QUEUE_ARN"

# SQS 큐에 대한 정책 설정
POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "$QUEUE_ARN",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "$TOPIC_ARN"
        }
      }
    }
  ]
}
EOF
)

# SQS 큐에 정책 적용
aws sqs set-queue-attributes \
    --queue-url $QUEUE_URL \
    --attributes "{\"Policy\":$(echo $POLICY | jq -c .)}"

# SNS 토픽을 SQS 큐에 구독
SUBSCRIPTION_ARN=$(aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol sqs \
    --notification-endpoint $QUEUE_ARN \
    --output text)

echo "Subscription created: $SUBSCRIPTION_ARN"

# 생성된 리소스 정보 파일 저장
cat > aws-resources.txt << EOF
SNS Topic ARN: $TOPIC_ARN
SQS Queue URL: $QUEUE_URL
SQS Queue ARN: $QUEUE_ARN
Subscription ARN: $SUBSCRIPTION_ARN
EOF

echo "Setup completed! Resource information saved to aws-resources.txt"